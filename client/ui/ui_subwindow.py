from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QSlider, QDialog
from PyQt5.QtCore import Qt


class UiForm2(QDialog):
    def __init__(self):
        super().__init__()

    def initUI(self, sub_form):
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('子窗口')

        sub_form.setObjectName("sub form")
        sub_form.resize(300, 300)
        sub_form.setMinimumSize(QtCore.QSize(300, 300))
        sub_form.setMaximumSize(QtCore.QSize(300, 300))
        sub_form.setStyleSheet("background-color:rgb(179, 179, 179);")

        sub_form.setWindowTitle("sub_form")

        self.change_device_btn()
        self.exit_btn()

    # def setupUi(self, Form, text):
    #     self.label = QtWidgets.QLabel(Form)
    #     self.label.setText(text)

    def change_device_btn(self):
        change_btn = QtWidgets.QPushButton(self)
        change_btn.setGeometry(QtCore.QRect(30, 30, 100, 100))
        change_btn.setMinimumSize(QtCore.QSize(100, 100))
        change_btn.setMaximumSize(QtCore.QSize(100, 100))
        change_btn.setCheckable(True)
        change_btn.setStyleSheet("background-color:rgb(111, 255, 248);")
        change_btn.setObjectName("change_btn")
        change_btn.setText("change_device")

    def exit_btn(self):
        ex_btn = QtWidgets.QPushButton(self)
        ex_btn.setGeometry(QtCore.QRect(150, 130, 100, 100))
        ex_btn.setMinimumSize(QtCore.QSize(100, 100))
        ex_btn.setMaximumSize(QtCore.QSize(100, 100))
        ex_btn.setStyleSheet("background-color:rgb(111, 255, 248);")
        ex_btn.setObjectName("ex_btn")
        ex_btn.setText("exit")
        ex_btn.clicked.connect(self.exit)

    def exit(self):
        self.close()