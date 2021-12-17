import sys
import typing
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi, loadUiType

import MySQLdb


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi("library.ui", self)
        self.setWindowTitle("Library Management System")

        self.handle_UI_changes()
        self.handle_buttons()

    def handle_UI_changes(self):
        self.show_themes(False)

    def handle_buttons(self):
        self.btn_daily_operations.clicked.connect(self.open_daily_operations_tab)
        self.btn_books.clicked.connect(self.open_books_tab)
        self.btn_users.clicked.connect(self.open_users_tab)
        self.btn_settings.clicked.connect(self.open_settings_tab)

        self.btn_show_themes.clicked.connect(lambda: self.show_themes(True))
        self.btn_hide_themes.clicked.connect(lambda: self.show_themes(False))

    def show_themes(self, show_flag=True):
        if show_flag:
            self.themes_box.show()
        else:
            self.themes_box.hide()

    def open_daily_operations_tab(self):
        print("daily")
        self.main_tab_widget.setCurrentIndex(0)

    def open_books_tab(self):
        self.main_tab_widget.setCurrentIndex(1)

    def open_users_tab(self):
        self.main_tab_widget.setCurrentIndex(2)

    def open_settings_tab(self):
        self.main_tab_widget.setCurrentIndex(3)


def app_main():
    app = QApplication(sys.argv)

    window = MainApp()
    window.show()

    app.exec()


if __name__ == "__main__":
    app_main()

