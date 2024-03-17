from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QDialogButtonBox
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt

from requests import post as urlpost

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

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self)
        buttonBox.addButton("Revoke", QDialogButtonBox.ButtonRole.ActionRole)

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