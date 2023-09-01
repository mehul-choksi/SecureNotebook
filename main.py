import sys
from PyQt6.QtWidgets import QApplication, QDialog
from src.Controls import MainWindow
from src.components.PasswordInputDialog import PasswordInputDialog
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QDate


class Main():
    def __init__(self):
        super().__init__()
        
if __name__ == "__main__":
    app = QApplication([])

    dialog = PasswordInputDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        password = dialog.getPassword()
        try:
            window = MainWindow(password)

            pixmap = QPixmap('logo.png')
            icon = QIcon(pixmap)
            app.setWindowIcon(icon)

            window.show()
            today = QDate.currentDate()
            window.calendar_widget.setSelectedDate(today)
            sys.exit(app.exec())
        except:
            pass
    
    else:
        print("Dialog canceled")