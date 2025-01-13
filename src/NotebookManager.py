from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QDialog, QLineEdit, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import os
import json

from PyQt6.QtWidgets import QSpacerItem, QSizePolicy

class NotebookManager(QMainWindow):
    def __init__(self, file_storage):
        super().__init__()
        self.file_storage = file_storage
        self.notebooks_metadata_path = "./notebooks_metadata.json"
        self.notebooks = self.load_notebooks()
        self.opened_windows = []  # Keep references to open notebook windows
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Notebook Manager")
        self.resize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Add stretch at the top to push content downward
        layout.addStretch(1)

        # Grid layout for notebooks
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        layout.addLayout(self.grid_layout)

        # "Add New Notebook" Button
        self.add_new_button = QPushButton("Add New Notebook")
        self.add_new_button.setIcon(QIcon("./assets/add.png"))  # Icon for "Add"
        self.add_new_button.setIconSize(QSize(24, 24))
        self.add_new_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745; 
                color: white; 
                border-radius: 10px; 
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.add_new_button.clicked.connect(self.add_new_notebook)
        layout.addWidget(self.add_new_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add stretch at the bottom to push content upward
        layout.addStretch(1)

        self.render_notebooks()

    def load_notebooks(self):
        if os.path.exists(self.notebooks_metadata_path):
            with open(self.notebooks_metadata_path, "r") as file:
                return json.load(file)
        return []

    def save_notebooks(self):
        with open(self.notebooks_metadata_path, "w") as file:
            json.dump(self.notebooks, file, indent=4)

    def render_notebooks(self):
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add each notebook to the grid
        for idx, notebook in enumerate(self.notebooks):
            notebook_button = QPushButton()
            notebook_button.setText(notebook["name"])
            icon_path = "./assets/notebook.png" if not notebook["password_protected"] else "./assets/secure.png"
            notebook_button.setIcon(QIcon(icon_path))
            notebook_button.setIconSize(QSize(64, 64))
            notebook_button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa; 
                    border: 1px solid #dee2e6; 
                    border-radius: 10px; 
                    padding: 10px; 
                    font-size: 14px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e2e6ea;
                }
            """)
            notebook_button.clicked.connect(lambda _, n=notebook: self.open_notebook(n))
            self.grid_layout.addWidget(notebook_button, idx // 3, idx % 3)

    def add_new_notebook(self):
        # Dialog for creating a new notebook
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Notebook")
        dialog.resize(300, 150)

        layout = QVBoxLayout(dialog)

        name_label = QLabel("Notebook Name:")
        layout.addWidget(name_label)
        name_edit = QLineEdit()
        layout.addWidget(name_edit)

        password_label = QLabel("Set Password (Optional):")
        layout.addWidget(password_label)
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(password_edit)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.create_notebook(name_edit, password_edit, dialog))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        dialog.exec()

    def create_notebook(self, name_edit, password_edit, dialog):
        name = name_edit.text().strip()
        password = password_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Notebook name cannot be empty.")
            return

        notebook_path = f"./data/{name}.json"
        if os.path.exists(notebook_path):
            QMessageBox.warning(self, "Error", "Notebook with this name already exists.")
            return

        notebook = {"name": name, "path": notebook_path, "password_protected": bool(password)}
        self.notebooks.append(notebook)
        self.save_notebooks()

        if password:
            # Initialize as secure notebook
            self.file_storage.initialize(password)
            self.file_storage.set_file_path(notebook_path)
            self.file_storage.content_dict = {}
            self.file_storage.writeToFile()
        else:
            # Create an empty file for regular notebook
            self.file_storage.set_file_path(notebook_path)
            with open(notebook_path, "w") as file:
                json.dump({}, file)

        dialog.accept()
        self.render_notebooks()

    def open_notebook(self, notebook):
        self.file_storage.set_file_path(notebook["path"])

        if notebook["password_protected"]:
            # Secure notebook logic
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Enter Password for {notebook['name']}")
            dialog.resize(300, 100)

            layout = QVBoxLayout(dialog)
            label = QLabel("Enter Password:")
            layout.addWidget(label)
            password_edit = QLineEdit()
            password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(password_edit)

            buttons_layout = QHBoxLayout()
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(lambda: self.verify_password(password_edit.text(), notebook, dialog))
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout.addWidget(ok_button)
            buttons_layout.addWidget(cancel_button)

            layout.addLayout(buttons_layout)
            dialog.exec()
        else:
            # Open regular notebook directly
            self.file_storage.reset_storage()
            self.file_storage.readFromFile()
            self.load_notebook(notebook)

    def verify_password(self, password, notebook, dialog):
        try:
            self.file_storage.initialize(password)
            self.file_storage.file_path = notebook["path"]
            self.file_storage.readFromFile()
            dialog.accept()
            self.load_notebook(notebook)
        except Exception as e:
            QMessageBox.warning(self, "Error", "Invalid password!")

    def load_notebook(self, notebook):
        from src.Controls import MainWindow  # Import dynamically to avoid circular dependencies
        main_window = MainWindow(self.file_storage)
        main_window.show()
        self.opened_windows.append(main_window)  # Keep a reference to prevent garbage collection
