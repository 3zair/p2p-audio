from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from .ui_mainwindow import UIForm
from .ui_subwindow import UiForm2
from PyQt5.QtCore import Qt


class MainWindow(QtWidgets.QWidget, UIForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_ui(self)


    def on_world_clicked(self, remark):
        print(remark)
        self.Title.setText("Hello World")

    def on_china_clicked(self):
        self.Title.setText("Hello China")

    def online_edit_text_changed(self, p_str):
        self.Title.setText(p_str)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.ignore()
        self.exit_click_handle()
