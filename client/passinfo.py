from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLayout,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QPushButton,
)
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt

from requests import post as urlpost
# from datetime import datetime

from srvrcfg import SERVERURL, headers, TIMEOUT


class PassInfoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Pass Info")

        parent.setDisabled(True)
        self.setEnabled(True)

        self.details = parent.activePass
        self.error = False

        match self.details["pass_type"]:
            case "one_type":
                self.details["pass_type"] = "Gate"
            case "daily":
                self.details["pass_type"] = "Lunch"
            case "alumni":
                self.details["pass_type"] = "Alumni"
            case "namaaz":
                self.details["pass_type"] = "Namaaz"

        # self.details["issued_on"] = datetime.fromtimestamp(int(self.details["issued_on"])).strftime("%d-%m-%Y, %I:%M %p") # utc epoch to string

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self)

        revokeButton = QPushButton("Revoke", buttonBox)
        buttonBox.addButton(revokeButton, QDialogButtonBox.ButtonRole.DestructiveRole)

        form = QFormLayout()
        form.addRow("Pass Type", QLabel(self.details["pass_type"]))
        form.addRow("Issued On", QLabel(self.details["issued_on"]))

        layout = QVBoxLayout(self)
        layout.addLayout(QFormLayout)
        layout.addWidget(buttonBox)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        revokeButton.clicked.connect(self.revokePass)
        buttonBox.accepted.connect(self.close)

    def revokePass(self):
        try:
            response = urlpost(
                f"{SERVERURL}/revoke_pass",
                headers=headers,
                json={"roll_no": self.details["rno"]},
                timeout=TIMEOUT,
            )
        except (ConnectionError, TimeoutError):
            self.parent().error("Connection Error!\nCheck Connection & Try again.")
            self.parent().status.setText("Connection Error.")
            self.error = True
            self.reject()

        if response.status_code == 200:
            self.parent().success(
                f"Successfully revoked {self.details['pass_type']} Pass for {self.details['rno']}."
            )
            self.close()
        else:
            self.parent().error(
                f"Unexpected error:\nResponse code: {response.status_code}\n{response.content.decode()}"
            )
            self.reject()

    def reject(self):
        if self.parent():
            self.parent().setEnabled(True)
        super().reject()

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.parent():
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.parent().setEnabled(True)
        return super().closeEvent(a0)
