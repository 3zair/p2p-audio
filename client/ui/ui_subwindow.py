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
        self.setStyleSheet("background-color:rgb(179, 179, 179);")
        self.resize(350, 350)
        self.setMinimumSize(QtCore.QSize(350, 350))
        self.setMaximumSize(QtCore.QSize(350, 350))

        sub_form.setObjectName("sub_form")
        # sub_form.resize(500, 500)
        # sub_form.setMinimumSize(QtCore.QSize(500, 500))
        # sub_form.setMaximumSize(QtCore.QSize(500, 500))

        sub_form.setWindowTitle("sub_form")

        self.change_device_btn()
        self.volume_control()
        self.exit_btn()

    # def setupUi(self, Form, text):
    #     self.label = QtWidgets.QLabel(Form)
    #     self.label.setText(text)

    def change_device_btn(self):
        # 新建一个frame
        top_frame = QtWidgets.QFrame(self)
        # top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        top_frame.setGeometry(QtCore.QRect(0, 0, 350, 120))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        self.label = QtWidgets.QLabel(top_frame)
        self.label.setGeometry(QtCore.QRect(30, 50, 100, 20))
        self.label.setText("音频输出设备为：")
        self.label.setObjectName("label_1")

        change_btn = QtWidgets.QPushButton(top_frame)
        change_btn.setGeometry(QtCore.QRect(150, 30, 80, 80))
        change_btn.setMinimumSize(QtCore.QSize(80, 80))
        change_btn.setMaximumSize(QtCore.QSize(80, 80))
        change_btn.setCheckable(True)
        change_btn.setStyleSheet("background-color:rgb(245, 245, 245);")
        change_btn.setObjectName("change_btn")
        change_btn.setText("device")

    def volume_control(self):
        # 新建一个frame
        mid_frame = QtWidgets.QFrame(self)
        # top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        mid_frame.setGeometry(QtCore.QRect(0, 120, 350, 120))
        mid_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        mid_frame.setObjectName("mid_frame")

        self.label2 = QtWidgets.QLabel(mid_frame)
        self.label2.setGeometry(QtCore.QRect(30, 50, 100, 20))
        self.label2.setText("音量调节：")
        self.label2.setObjectName("label_2")

    def exit_btn(self):
        bot_frame = QtWidgets.QFrame(self)
        # top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        bot_frame.setGeometry(QtCore.QRect(0, 240, 350, 120))
        bot_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bot_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        bot_frame.setObjectName("bot_frame")

        ex_btn = QtWidgets.QPushButton(bot_frame)
        ex_btn.setGeometry(QtCore.QRect(250, 10, 80, 80))
        ex_btn.setMinimumSize(QtCore.QSize(80, 80))
        ex_btn.setMaximumSize(QtCore.QSize(80, 80))
        ex_btn.setStyleSheet("background-color:rgb(245, 245, 245);")
        ex_btn.setObjectName("ex_btn")
        ex_btn.setText("exit")
        ex_btn.clicked.connect(self.exit)

    def exit(self):
        self.close()