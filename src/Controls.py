from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QDate, QKeyCombination
from src.components.CustomIndex import CustomIndex
from src.components.CustomCalendarWidget import CustomCalendarWidget
from src.storage.file_storage import FileStorage
from src.components.CustomContentTextBox import CustomContentTextBox
from src.components.ChangePasswordDialog import ChangePasswordDialog
from markdown_it import MarkdownIt
import html2text

class MainWindow(QMainWindow):
    def __init__(self, password):
        super().__init__()
        
        # Initialize file storage object
        self.password = password
        self.file_storage = FileStorage()
        self.file_storage.initialize(self.password)
        self.file_storage.readFromFile()

        self.md = MarkdownIt()
        self.editsMade = False

        # configure font in above widgets
        font = QFont()
        font.setPointSize(10)

        self.setWindowTitle("SecureNoteBook")
        self.resize(800,600)

        # Create the main widget and set it as the central widget for the main window
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a horizontal layout for the main widget
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(0)

        # Create the first section
        left_controls = QWidget()
        left_controls.setMaximumWidth(250)
        self.left_controls_layout = QVBoxLayout(left_controls)

        # Create a calendar widget
        # self.calendar_widget = QCalendarWidget()
        self.calendar_widget = CustomCalendarWidget()
        # self.calendar_widget.setMaximumHeight(200)
        self.calendar_widget.clicked.connect(self.on_date_click)
        self.calendar_widget.selectionChanged.connect(self.on_date_click)

        self.left_controls_layout.addWidget(self.calendar_widget)

         # Create a search field
        self.search_widget = QLineEdit()
        self.search_widget.setFont(font)
        self.search_widget.setPlaceholderText("Search Text ...")
        self.search_widget.textChanged.connect(self.search)

        self.left_controls_layout.addWidget(self.search_widget)

        # construct the index widget -> index of serch results or index of content_dict
        self.index_widget = CustomIndex()
        self.index_widget.populate_indices(self.file_storage.content_dict)
        self.index_widget.itemClicked.connect(self.on_index_item_click)

        self.left_controls_layout.addWidget(self.index_widget)

        layout.addWidget(left_controls)
        # ---------------------------------------------------------------------------
        # Create the second section
        content_pane = QWidget()
        content_pane_layout = QVBoxLayout(content_pane)

        # Create the button section
        button_section = QWidget()
        button_section_layout = QHBoxLayout(button_section)

        self.today_button = QPushButton("Today")
        self.today_button.clicked.connect(self.on_today_button_click)
        button_section_layout.addWidget(self.today_button)

        self.date_box = QLineEdit()
        self.date_box.setMaximumWidth(125)
        self.date_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_box.setStyleSheet('background-color: lightgreen; border: 1px solid blue')
        self.date_box.setText(self.calendar_widget.selectedDate().toString("d MMMM yyyy"))
        # longFormat = QLocale().toString(self.calendar_widget.selectedDate(), "MMMM d, yyyy")

        button_section_layout.addWidget(self.date_box)

        save_shortcut = QShortcut(QKeySequence(QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_S)), self)
        save_shortcut.activated.connect(self.hard_save)

        config_passwd_button = QPushButton("Change Password") 
        config_passwd_button.clicked.connect(self.show_password_dialog)
        button_section_layout.addWidget(config_passwd_button)

        # Add button section to second section layout
        content_pane_layout.addWidget(button_section)

        # Create a multi-line text field for rendering contents.
        self.content_text_edit_widget = CustomContentTextBox()
        self.content_text_edit_widget.setFont(font)
        self.content_text_edit_widget.textChanged.connect(self.save_to_content_dict)

        # Add text edit to content pane layout
        content_pane_layout.addWidget(self.content_text_edit_widget)

        # Add the second section to the main layout
        layout.addWidget(content_pane)

    # ***************************************************************************

    def show_password_dialog(self):
        dialog = ChangePasswordDialog()
        # dialog.exec()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            passwords = dialog.getPasswords()
            [old_pwd, new_pwd, conf_pwd] = passwords
            msg = QMessageBox()
            if new_pwd == '':
                msg.setText('New Password can not be blank')
                msg.exec()
            elif self.password != old_pwd:
                msg.setText('Old password was not correct')
                msg.exec()
            elif new_pwd != conf_pwd:
                msg.setText('New passwords must match')
                msg.exec()
            else:
                self.password = new_pwd
                self.file_storage.initialize(self.password)
                self.file_storage.writeToFile()

                msg.setText("Password Changed")
                msg.exec()


    def on_date_click(self):
        selected_date = self.calendar_widget.selectedDate().toString('yyyyMMdd')
        
        self.date_box.setText(self.calendar_widget.selectedDate().toString('d MMMM yyyy'))

        existing_content = ''
        try:
            existing_content = self.file_storage.content_dict[selected_date]
        except KeyError:
            existing_content = ''
        
        if self.content_text_edit_widget.isHtmlView:
            # md.render converts existing_content which is in md view to Html view
            existing_content = self.md.render(existing_content)
            self.content_text_edit_widget.setHtml(existing_content)
        else:
            self.content_text_edit_widget.setPlainText(existing_content)
            

    def closeEvent(self, event):
        print('Close event called')
        if self.editsMade:
            self.hard_save()
        super().closeEvent(event)


    def on_today_button_click (self):
        # print('Today click handler invoked')
        self.calendar_widget.setSelectedDate(QDate.currentDate())
        self.on_date_click()

    
    def save_to_content_dict(self):
        # print('save_to_content_dict invoked')
        if self.editsMade:
            self.set_star_in_date_box()
        # self.editsMade = True
        entry_date = self.calendar_widget.selectedDate().toString("yyyyMMdd")
        html_content = self.content_text_edit_widget.toHtml()
        markdown_content = html2text.html2text(html_content).strip()
        markdown_content = self.file_storage.preprocess(markdown_content)
        existing_content = ''
        try:
            existing_content = self.file_storage.content_dict[entry_date]
        except:
            existing_content = ''

        if markdown_content != existing_content:
            self.file_storage.upsert_without_write(entry_date, markdown_content)
            self.editsMade = True
            self.set_star_in_date_box()

    def set_star_in_date_box(self):
        current_date_text = self.date_box.text()
        if current_date_text.endswith('*'):
            pass
        else:
            current_date_text += '*'
            self.date_box.setText(current_date_text)

        
    def hard_save(self):
        print('hard_save invoked')        
        if self.editsMade == True:
            self.current_date = self.calendar_widget.selectedDate()
            self.file_storage.writeToFile()
            self.index_widget.populate_indices(self.file_storage.content_dict)
            self.calendar_widget.setSelectedDate(self.current_date)
            self.editsMade = False
            self.date_box.setText(self.date_box.text()[:-1])
        else:
            print('No changes detected')
            self.calendar_widget.setSelectedDate(self.current_date)


    def fetch_latest_list_view(self, results=None):
        print('Fetch latest view invoked')
        print('**RESULTS: ', results)
        # self.file_storage.readFromFile()
        if results == None:
            results = self.file_storage.content_dict

    def search(self):
        search_phrase = self.search_widget.text()
        search_phrase = search_phrase.strip()
        results = self.file_storage.search(search_phrase)
        self.index_widget.populate_indices(results)
        # self.fetch_latest_list_view(results)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.content_text_edit_widget.isHtmlView:
                html_content = self.content_text_edit_widget.toHtml()
                self.date_box.setStyleSheet('background-color: blanchedalmond')
                self.content_text_edit_widget.setPlainText(html2text.html2text(html_content))
            else:
                self.date_box.setStyleSheet('background-color: lightgreen')
                self.content_text_edit_widget.setHtml(self.md.render(self.content_text_edit_widget.toPlainText()))
        else:
            return super().keyPressEvent(event)
    
    def on_index_item_click(self):
        selected_item = self.index_widget.selectedItems()[0]
        date_str = selected_item.text().split(":")[0].strip()
        date = QDate.fromString(date_str, "yyyyMMdd")

        if self.calendar_widget.selectedDate() == date:
            tempDate = date.addDays(1)
            self.calendar_widget.setSelectedDate(tempDate)

        self.calendar_widget.setSelectedDate(date)



    
    # def fix_calendar_view_issue(self):
    #     ''' The calendar is rendered with week num column replacing the saturday col.
    #     This fix finds the next saturday and sets it in focus. By doing this the weeknum col is pushed out of view. 
    #     '''
    #     today = QDate.currentDate()
    #     days_to_next_saturday = 6 - today.dayOfWeek()
    #     next_saturday = today.addDays(days_to_next_saturday)
    #     self.calendar_widget.setSelectedDate(next_saturday)
        