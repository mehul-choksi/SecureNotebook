from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout
import sys

class PasswordInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter the password: ")
        layout = QVBoxLayout()
        label = QLabel("Enter Password:")
        self.line_edit = QLineEdit()
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def getPassword(self):
        return self.line_edit.text()