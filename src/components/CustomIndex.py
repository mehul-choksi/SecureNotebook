from PyQt6.QtWidgets import QListWidget
from src.components.CustomListWidgetItem import CustomListWidgetItem


class CustomIndex(QListWidget):
    def __init__(self):
        super().__init__()
    
    def populate_indices(self, entries):
        self.clear()
        for date in entries.keys():
            docket_text = str(date) + ' : ' + entries[date][:25]
            docket_text = docket_text.replace('\n', ' ')
            docket_text = docket_text.replace('\t', ' ')
            custom_list_item = CustomListWidgetItem(docket_text, entries[date])
            self.addItem(custom_list_item)
        
        self.sortItems()
    
  