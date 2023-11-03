from os.path import dirname, abspath, isfile, join as joinpath
from sys import argv, exit, executable
from re import fullmatch
from requests import post as urlpost
from datetime import date
from base64 import b64decode as b64d, b64encode as b64e
from configparser import ConfigParser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QAction, QLineEdit, QComboBox, 
    QToolButton, QPushButton, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsView, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QSizeF

import sys

from setlunchtime import *
from gethistory import *
from getlatecomers import *
from srvrcfg import SERVERURL, headers, details

BASE_DIR = None
if getattr(sys, 'frozen', False):
    BASE_DIR = dirname(executable)
elif __file__:
    BASE_DIR = dirname(abspath(__file__))

DATE = date.today()
YEAR = int(str(DATE.year)[2:])
DATA_DIR = joinpath(dirname(abspath(__file__)), "res")

savedPageSize = False
cfg = ConfigParser()
if isfile(joinpath(BASE_DIR, '.config.ini')):
    cfg.read(joinpath(BASE_DIR, '.config.ini'))
    sections = cfg.sections()
    if "PageSize" in sections:
        savedPageSize = True
else:
    cfg["PageSize"] = {"height": "-1", "width": "-1"}


class MainWin(QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        
        self.details: QLabel
        self.rno: QLineEdit
        self.invalid: QLabel
        self.PassType: QComboBox
        self.Tools: QToolButton
        self.GenPassBtn: QPushButton
        self.PrintBtn: QPushButton
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

        self.invalid.setStyleSheet("color: red;")

        self.PassType.currentIndexChanged.connect(lambda idx: self.GenPassBtn.setEnabled(idx > -1))
        self.GenPassBtn.pressed.connect(self.generatePass)
        self.PrintBtn.pressed.connect(self.printQR)

        icon = QIcon()
        icon.addPixmap(QPixmap(joinpath(DATA_DIR, "Print.png")), QIcon.Normal, QIcon.On)
        self.PrintBtn.setIcon(icon)
        self.PrintBtn.setText(None)

        self.PrintBtn.hide()

        self.setupOptions()
        self.handleRollNo("")

    @pyqtSlot(str)
    def handleRollNo(self, _):
        self.PrintBtn.hide()
        rno = self.rno.text().upper()

        if not fullmatch("\d{2}BD1A\d{2}[A-HJ-NP-RT-Z0-9]{2}", rno):
            self.PassType.setCurrentIndex(-1)
            self.PassType.setDisabled(True)
            self.GenPassBtn.setDisabled(True)
            with open(joinpath(DATA_DIR, "Anonymous.png"), "rb") as img:
                self._SetImg(b64e(img.read()), "Anonymous")
            self.details.setText("## Enter data")
            self.details.setStyleSheet("color: #ccc")
            self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.invalid.setText("Invalid Roll No." if len(rno)==10 else "")
            self.status.setText("Invalid Roll No." if len(rno)==10 else "Waiting for data")
            return
        
        self.updateDetails()
        # self._SetImg("Processing")

        admn_yr = int(rno[:2])

        self.PassType.setEnabled(True)
        self.PassType.model().item(2).setEnabled(admn_yr < YEAR-3 or 
                                                 (admn_yr == YEAR-3 and DATE.month > 6))

    def updateDetails(self):
        # urlget("http://localhost:3000/details").json()
        self.details.setText(f"##### Name:\n### {details['name']}\n---\n#### Section: {details['section']}\n#### Year: {details['year']}\n")
        self.details.setStyleSheet("color: #000")
        self.details.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self._SetImg(details["image"].encode(), 'Student')
        # ...

    def printQR(self):
        self.status.setText("Printing Pass")
        Printer = QPrinter(QPrinterInfo.defaultPrinter())
        saved_size = None
        if savedPageSize:
            saved_size = (float(cfg["PageSize"]["width"]), float(cfg["PageSize"]["height"]))
            Printer.setPageSizeMM(QSizeF(*saved_size))
        Printer.setPageMargins(5,5,5,5, QPrinter.Millimeter)
        
        painter = QPainter()
        printdlg = QPrintDialog(Printer)
        printdlg.exec()

        painter.begin(Printer)
        res = min(Printer.width(), Printer.height())
        painter.drawImage(0,0,self.Img.scaled(res, res))
        painter.end()

        self.status.setText("Printing Pass")

        pagesize = Printer.pageSizeMM()
        if saved_size != (wd:=pagesize.width(), ht:=pagesize.height()):
            cfg["PageSize"]["width"], cfg["PageSize"]["height"] = str(wd), str(ht)
            with open(joinpath(BASE_DIR , '.config.ini'), "w") as f:
                cfg.write(f)

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

    def _SetImg(self, img: bytes | str | None = None, imgtype: str | None = None) -> None:
        self.Scene = QGraphicsScene()
        self.ImgBox = QGraphicsPixmapItem()
        if imgtype == None:
            self.Scene.addText("Enter Data" if img == None else img)
            self.PrintBtn.setDisabled(True)
        else: 
            self.Img = QImage.fromData(b64d(img), 'PNG' if imgtype=="QR" or imgtype=="Anonymous" else 'JPG')
            self.PixMap = QPixmap.fromImage(self.Img).scaledToWidth(300)
            self.ImgBox.setPixmap(self.PixMap)
            self.Scene.addItem(self.ImgBox)
            self.PrintBtn.setEnabled(True)
            if imgtype=="QR": self.PrintBtn.show()
            else: self.PrintBtn.hide()
        self.Image.setScene(self.Scene)
        self.Image.setAlignment(Qt.AlignmentFlag.AlignCenter)

    @pyqtSlot()
    def generatePass(self):
        self.status.setText("Processing...")
        res = None
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

        res = response.content.decode()

        if res.startswith("Error:"):
            self.error(res.split(":", 1)[1])
            self.status.setText("Waiting...")
        elif res.startswith("Traceback"):
            self.error(f"Server error. Returned:\n{res}")
            self.status.setText("Waiting...")
        else:
            passimg = None
            data = res.split("\n")
            if res.startswith("Warning:"):
                self.error(data[0])
                if self.PassType.currentIndex() == 2: passimg = data[1]
            else:
                passimg = res

            if self.PassType.currentIndex() == 2: 
                self._SetImg(passimg.encode(), "QR")
                self.PrintBtn.show()
            elif response.status_code == 200 and not res.startswith("Warning:"): 
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