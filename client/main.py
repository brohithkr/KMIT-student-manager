from os.path import dirname, abspath, isfile, join as joinpath
from sys import argv, exit, executable
from re import fullmatch
from requests import get as urlget, post as urlpost
from datetime import date
# from json import load as loadjson
from base64 import b64decode as b64d, b64encode as b64e

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QAction, QLineEdit, QComboBox, 
    QToolButton, QPushButton, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsView, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QImage, QColorConstants
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QObject, QThread

import sys

from setlunchtime import *
from gethistory import *
from getlatecomers import *
from srvrcfg import SERVERURL, headers

BASE_DIR = None
if getattr(sys, 'frozen', False):
    BASE_DIR = dirname(executable)
elif __file__:
    BASE_DIR = dirname(abspath(__file__))

DATA_DIR = joinpath(dirname(abspath(__file__)), "res")

with open(joinpath(DATA_DIR, "Anonymous.png"), "rb") as img:
    anonymous_img = b64e(img.read()), "Anonymous"

DATE = date.today()
YEAR = int(str(DATE.year)[2:])

class MainWin(QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        
        self.details: QLabel
        self.rno: QLineEdit
        self.invalid: QLabel
        self.PassType: QComboBox
        self.Tools: QToolButton
        self.GenPassBtn: QPushButton
        self.Image: QGraphicsView

        ui_file_path = joinpath(DATA_DIR, 'design.ui')
        loadUi(ui_file_path, self)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status.setStyleSheet("padding-right: 12px; padding-bottom: 3px")
        self.status.setText("Waiting for data...")

        self.statusBar().addWidget(self.status, 1)

        self.rno.editingFinished.connect(lambda: self.rno.setText(self.rno.text().upper()))
        self.rno.textChanged.connect(self.handleRollNo)
        self.rno.returnPressed.connect(lambda: self.PassType.setFocus())

        self.PassType.currentIndexChanged.connect(lambda idx: self.GenPassBtn.setEnabled(idx > -1))
        self.GenPassBtn.pressed.connect(self.generatePass)

        self.setupOptions()
        self.handleRollNo("")

    @pyqtSlot(str)
    def handleRollNo(self, _):
        self.rno.setText(self.rno.text().upper())
        rno = self.rno.text()

        if not fullmatch("\d{2}BD1A\d{2}[A-HJ-NP-RT-Z0-9]{2}", rno):
            self.PassType.setCurrentIndex(-1)
            self.PassType.setDisabled(True)
            self.GenPassBtn.setDisabled(True)
            self._SetImg(*anonymous_img)
            self.details.setText("## Enter data")
            self.details.setStyleSheet("color: #ccc")
            self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.invalid.setText("Invalid Roll No." if len(rno)==10 else "")
            self.status.setText("Invalid Roll No." if len(rno)==10 else "Waiting for data")
            return
        
        self.StateHandler = QThread()
        self.detailsUpdater = DetailsFetcher(rno)
        self.detailsUpdater.moveToThread(self.StateHandler)
        self.StateHandler.started.connect(self.detailsUpdater.updateDetails)

        self.detailsUpdater.error.connect(self.error)
        self.detailsUpdater.success.connect(self.updateUI)

        self.StateHandler.finished.connect(self.detailsUpdater.deleteLater) 
        self.StateHandler.finished.connect(self.StateHandler.deleteLater) 
        self.StateHandler.start()
        # self._SetImg("Processing")

        admn_yr = int(rno[:2])

        self.PassType.setEnabled(True)
        self.PassType.model().item(2).setEnabled(admn_yr < YEAR-3 or 
                                                 (admn_yr == YEAR-3 and DATE.month > 6))

    @pyqtSlot(dict)
    def updateUI(self, student_details):
        self.details.setText(f"##### Name:\n### {student_details['name']}\n---\n#### Section: {student_details['dept']}-{student_details['section']}\n#### Year: {student_details['year']}\n")
        self.details.setStyleSheet("color: #000")
        self.details.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        if student_details["picture"] == None:
            self._SetImg(*anonymous_img)
            self._SetImg("Image not found", "Error", False)
        else:
            self._SetImg(student_details["picture"], "Student")

    def setupOptions(self):
        settingsMenu = QMenu(self)
        settingsMenu.addAction('Set Lunch time', self.setLunchTime)
        settingsMenu.addAction('Download History', self.dloadMonthHistory)
        settingsMenu.addAction('Latecomers data', self.getLatecomersData)

        self.Tools.setMenu(settingsMenu)
        self.Tools.setDefaultAction(QAction(self))

        icon = QIcon()
        icon.addPixmap(QPixmap(joinpath(DATA_DIR, "Gear.png")), QIcon.Normal, QIcon.On)
        self.Tools.setIcon(icon)
        self.Tools.setText(None)

    def setLunchTime(self):
        self.status.setText("Modifying Lunch Time")
        dlg = LunchTimeDialog(self)
        dlg.show()
        self.status.setText("Waiting...")

    def dloadMonthHistory(self):
        self.status.setText("Downloading Pass History")
        dlg = GetHistoryDialog(self)
        dlg.show()
        self.status.setText("Waiting...")

    def getLatecomersData(self):
        self.status.setText("Downloading Latecomers data")
        dlg = GetLatecomersDialog(self)
        dlg.show()
        self.status.setText("Waiting...")

    def _SetImg(self, img: bytes | str | None = None, imgtype: str | None = None, reset:bool = True) -> None:
        if reset:
            self.Scene = QGraphicsScene()
            self.ImgBox = QGraphicsPixmapItem()
        if imgtype == None or imgtype == "Error":
            text = self.Scene.addText("Enter Data" if img == None else img)
            text.setDefaultTextColor(QColorConstants.Red)
            if imgtype == "Error" and not reset:
                text.setY(self.ImgBox.boundingRect().center().y() + 55 - text.boundingRect().height()/2)
                text.setX(self.ImgBox.boundingRect().center().x() - text.boundingRect().width()/2)
        else: 
            self.Img = QImage.fromData(b64d(img), 'PNG' if imgtype=="QR" or imgtype=="Anonymous" else 'JPG')
            if imgtype == "Student": self.PixMap = QPixmap.fromImage(self.Img).scaled(300, 370)
            else: self.PixMap = QPixmap.fromImage(self.Img).scaledToWidth(300)
            self.ImgBox.setPixmap(self.PixMap)
            self.Scene.addItem(self.ImgBox)
        self.Image.setScene(self.Scene)
        self.Image.setAlignment(Qt.AlignmentFlag.AlignCenter)

    @pyqtSlot()
    def generatePass(self):
        self.status.setText("Processing...")
        passtype = self.PassType.currentIndex()
        try:
            response = urlpost(f"{SERVERURL}/gen_pass", headers=headers, 
                                json={"roll_no": self.rno.text().upper(), 
                                "pass_type": "one_time" if passtype == 0 else
                                                "daily" if passtype == 1 else "alumni" })
        except (ConnectionError, Timeout):
            self.error("Connection Error!\nCheck Internet & Try again.")
            self.status.setText("Connection Error.")
            return
        
        self.status.setText("Generating Pass")

        result = response.content.decode()

        if result.startswith("Error:"):
            self.error(result.split(":", 1)[1])
            self.status.setText("Waiting...")
        elif result.startswith("Traceback"):
            self.error(f"Server error. Returned:\n{result}")
            self.status.setText("Waiting...")
        elif result.startswith("Warning:"):
            self.error(result.split(":", 1)[1])
        elif response.status_code == 200: 
            self.success("Pass Successfully created")
            self.status.setText("Done")

    @pyqtSlot(str)
    def error(self, msg):
        QMessageBox.critical(self, "Error!", msg)

    @pyqtSlot(str)
    def success(self, msg):
        QMessageBox.information(self, "Success", msg)

    @pyqtSlot(int)
    def crash(self, response):
        QMessageBox.critical(self, "Server Error!!", f"Unexpected server error occured.\nResponse code: {response}")
        exit()


class DetailsFetcher(QObject):
    error = pyqtSignal(str)
    success = pyqtSignal(dict)
    def __init__(self, rno: str):
        self.rno = rno 
        super().__init__(None)

    def updateDetails(self):
        print("Started")
        try: 
            self.res = urlget(f"{SERVERURL}/get_student_data?rollno={self.rno}", headers=headers)
        except (ConnectionError, Timeout):
            self.error.emit("Unable to connect to server. Check connection & Try again.")
        else:
            if self.res.status_code == 200:
                self.success.emit(self.res.json())
                return
            else:
                self.error.emit("Roll number not found." if self.res.status_code == 404 else "Unable to fetch Student details")
                return
        
if __name__ == '__main__':
    from platform import system
    ostype = system()
    iconext = "png"

    if ostype == "Windows":
        # Windows Taskbar icon fix
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("KMIT.Pass.Generator.1")
        iconext = "ico"
    elif ostype == "Darwin": iconext = "icns"

    app = QApplication(argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    win = MainWin()
    win.setWindowIcon(QIcon(f"{DATA_DIR}/kmit.{iconext}"))
    win.show()
    exit(app.exec())