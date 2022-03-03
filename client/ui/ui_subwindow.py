import os.path
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QSlider, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# TODO:此处为模拟子页面配置
cus = {'1': [0, 50], '2': [1, 60], '3': [0, 70], '4': [1, 80], '5': [0, 90], '6': [1, 10], '7': [0, 20], '8': [1, 30]}


class UiForm2(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.static_dir = os.path.join(os.getcwd(), "statics")

    def initUI(self, channel_id):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('子窗口')
        self.setStyleSheet("background-color:rgb(159, 159, 159);")
        self.resize(350, 350)
        self.setMinimumSize(QtCore.QSize(350, 350))
        self.setMaximumSize(QtCore.QSize(350, 350))

        self.change_device_btn(cus[channel_id][0])
        self.volume_control(cus[channel_id][1])
        self.exit_btn()

    def change_device_btn(self, btn_flag):
        # 新建一个frame
        top_frame = QtWidgets.QFrame(self)
        top_frame.setGeometry(QtCore.QRect(0, 0, 350, 120))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        self.label = QtWidgets.QLabel(top_frame)
        self.label.setGeometry(QtCore.QRect(30, 50, 100, 20))
        self.label.setText("音频输出设备为：")
        self.label.setObjectName("label_1")

        self.change_btn = QtWidgets.QPushButton(top_frame)
        self.change_btn.setGeometry(QtCore.QRect(150, 30, 80, 80))
        self.change_btn.setMinimumSize(QtCore.QSize(80, 80))
        self.change_btn.setMaximumSize(QtCore.QSize(80, 80))
        self.change_btn.setCheckable(True)
        self.change_btn.setChecked(btn_flag)
        self.change_btn.setStyleSheet("background-color:rgb(245, 245, 245)")
        self.change_btn.setObjectName("change_btn")
        # change_btn.setText("device")
        self.change_btn.clicked.connect(self.change_device)
        if self.change_btn.isChecked():
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
        else:
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))
        self.change_btn.setIconSize(QtCore.QSize(50, 50))

    def volume_control(self, vo):
        # 新建一个frame
        mid_frame = QtWidgets.QFrame(self)
        mid_frame.setGeometry(QtCore.QRect(0, 120, 350, 120))
        mid_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        mid_frame.setObjectName("mid_frame")

        self.label2 = QtWidgets.QLabel(mid_frame)
        self.label2.setGeometry(QtCore.QRect(30, 50, 100, 20))
        self.label2.setText("音量调节：")
        self.label2.setObjectName("label_2")

        self.volume_slider = QSlider(Qt.Horizontal, mid_frame)
        self.volume_slider.setGeometry(QtCore.QRect(150, 40, 180, 45))
        self.volume_slider.setMaximum(32767)
        self.volume_slider.setPageStep(1024)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(vo)
        self.volume_slider.valueChanged.connect(self.change_volume)

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

    def change_volume(self, value):
        self.volume = value

    def change_device(self):
        if self.change_btn.isChecked():
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
        else:
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))

    def exit(self):
        self.close()
