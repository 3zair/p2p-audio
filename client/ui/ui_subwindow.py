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

        sub_form.setObjectName("sub_form")
        sub_form.resize(800, 800)
        sub_form.setMinimumSize(QtCore.QSize(800, 800))
        sub_form.setMaximumSize(QtCore.QSize(800, 800))
        sub_form.setStyleSheet("background-color:rgb(179, 179, 179);")

        sub_form.setWindowTitle("sub_form")

        self.change_device_btn(sub_form)
        self.exit_btn()

    # def setupUi(self, Form, text):
    #     self.label = QtWidgets.QLabel(Form)
    #     self.label.setText(text)

    def change_device_btn(self, sub_form):
        # 新建一个frame
        top_frame = QtWidgets.QFrame(sub_form)
        # top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        top_frame.setGeometry(QtCore.QRect(0, 0, 300, 300))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        self.label = QtWidgets.QLabel(top_frame)
        self.label.setGeometry(QtCore.QRect(0, 0, 15, 20))
        self.label.setText("音频输出设备为：")
        self.label.setObjectName("label_1")

        change_btn = QtWidgets.QPushButton(top_frame)
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