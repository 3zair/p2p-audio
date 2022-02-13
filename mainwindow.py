from PyQt5 import QtCore, QtGui, QtWidgets
from ui_mainwindow import UIForm


class MainWindow(QtWidgets.QWidget, UIForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_ui(self)

        # self.Title.setText("hello Python")
        # self.World.clicked.connect(self.on_world_clicked())
        # self.China.clicked.connect(self.on_china_clicked())
        # self.lineEdit.textChanged.connect(self.online_edit_text_changed())

    def on_world_clicked(self, remark):
        print(remark)
        self.Title.setText("Hello World")

    def on_china_clicked(self):
        self.Title.setText("Hello China")

    def online_edit_text_changed(self, p_str):
        self.Title.setText(p_str)
