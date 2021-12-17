import sys
import typing
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Library Management System")
        ui = loadUi("library.ui", self)
        


def app_main():
    app = QApplication(sys.argv)

    window = MainApp()
    window.show()

    app.exec()


if __name__ == "__main__":
    app_main()

