from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from .ui_mainwindow import UIForm
from .ui_subwindow import UiForm2
from PyQt5.QtCore import Qt


class MainWindow(QtWidgets.QWidget, UIForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_ui(self)
