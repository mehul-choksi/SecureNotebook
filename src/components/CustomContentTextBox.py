from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt

class CustomContentTextBox(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isHtmlView = True

    def setPlainText(self, text):
        super().setPlainText(text)
        self.isHtmlView = False

    def setHtml(self, html):
        super().setHtml(html)
        self.isHtmlView = True