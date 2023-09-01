from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        layout = QVBoxLayout()
        old_passwd_label = QLabel("Enter Old Password:")
        self.old_passwd = QLineEdit()
        new_passwd_label = QLabel("Enter New Password:")
        self.new_passwd = QLineEdit()
        confirm_passwd_label = QLabel("Confirm New Password:")
        self.confirm_passwd = QLineEdit()
        
        layout.addWidget(old_passwd_label)
        layout.addWidget(self.old_passwd)
        layout.addWidget(new_passwd_label)
        layout.addWidget(self.new_passwd)
        layout.addWidget(confirm_passwd_label)
        layout.addWidget(self.confirm_passwd)
                
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def getPasswords(self):
        return [self.old_passwd.text(), self.new_passwd.text(), self.confirm_passwd.text()]