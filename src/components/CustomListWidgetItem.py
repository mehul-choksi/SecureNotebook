from PyQt6.QtWidgets import QListWidgetItem

class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, title, data):
        super().__init__(title)
        self.title = title
        self.data = data

    def get_data(self):
        return self.data