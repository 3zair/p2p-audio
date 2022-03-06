import logging
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSlider, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from udp_client.client import change_output_volume, get_channel_volume_conf


#
# # TODO:此处为模拟子页面配置
# volumeConf = {'1': [0, 50], '2': [1, 60], '3': [0, 70], '4': [1, 80], '5': [0, 90], '6': [1, 10], '7': [0, 20],
#               '8': [1, 30]}


class UiForm2(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.static_dir = os.path.join(os.getcwd(), "statics")
        self.channel_id = None

    def initUI(self, channel_id):
        # 设置无边框的话就不能设置窗口模态
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle('子窗口')
        self.setStyleSheet("background-color:rgb(159, 159, 159);")
        self.resize(350, 350)
        self.setMinimumSize(QtCore.QSize(350, 350))
        self.setMaximumSize(QtCore.QSize(350, 350))
        # TODO：设置成self属性后，需要设置每次只能弹出一个通道的子页面。不设置成self属性的话，后面的音量调节是自有的方法传不进去通道参数
        self.channel_id = channel_id

        self.change_device_btn_init()
        self.volume_control_btn_init()
        self.exit_btn_init()

    def change_device_btn_init(self):
        # 新建一个frame
        top_frame = QtWidgets.QFrame(self)
        top_frame.setGeometry(QtCore.QRect(0, 0, 350, 120))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        self.label = QtWidgets.QLabel(top_frame)
        self.label.setGeometry(QtCore.QRect(30, 50, 150, 20))
        self.label.setStyleSheet("font-size:15px;")
        self.label.setText("音频输出设备为：")
        self.label.setObjectName("label_1")

        self.change_btn = QtWidgets.QPushButton(top_frame)
        self.change_btn.setGeometry(QtCore.QRect(180, 30, 80, 80))
        self.change_btn.setMinimumSize(QtCore.QSize(80, 80))
        self.change_btn.setMaximumSize(QtCore.QSize(80, 80))
        self.change_btn.setCheckable(True)
        self.change_btn.setStyleSheet("background-color:rgb(245, 245, 245)")
        self.change_btn.setObjectName("change_btn")
        device = get_channel_volume_conf()[self.channel_id][0]
        if device == 2:
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
            self.change_btn.setChecked(True)
            logging.info("init header")
        elif device == 1:
            self.change_btn.setChecked(False)
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))
            logging.info("init pc")
        else:
            logging.error("change_device_btn init, invalid device id:{}".format(device))
        self.change_btn.setIconSize(QtCore.QSize(50, 50))
        self.change_btn.clicked.connect(self.change_device_handle)

    def volume_control_btn_init(self):
        # 新建一个frame
        mid_frame = QtWidgets.QFrame(self)
        mid_frame.setGeometry(QtCore.QRect(0, 120, 350, 120))
        mid_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        mid_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        mid_frame.setObjectName("mid_frame")

        self.label2 = QtWidgets.QLabel(mid_frame)
        self.label2.setGeometry(QtCore.QRect(30, 50, 100, 20))
        self.label2.setStyleSheet("font-size:15px;")
        self.label2.setText("音量调节：")
        self.label2.setObjectName("label_2")

        self.volume_slider = QSlider(Qt.Horizontal, mid_frame)
        self.volume_slider.setGeometry(QtCore.QRect(150, 40, 180, 45))
        # self.volume_slider.setMaximum(32767)
        # self.volume_slider.setPageStep(1024)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setPageStep(1)
        self.volume_slider.setRange(0, 100)
        output_device = get_channel_volume_conf()[self.channel_id][0]
        self.volume_slider.setValue(get_channel_volume_conf()[self.channel_id][output_device])
        # TODO：self.change_volume没办法传channel_id进去，无法修改cus里面存的音量值，所以将channel_id设置成了self属性
        #self.volume_slider.valueChanged.connect(self.change_volume_handle)
        self.volume_slider.sliderReleased.connect(self.change_volume_handle)

    def exit_btn_init(self):
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
        ex_btn.clicked.connect(self.exit_handle)

    def change_volume_handle(self):
        if self.change_btn.isChecked():
            # 耳机
            change_output_volume(self.channel_id, device=2, usb_volume=self.volume_slider.value())
        else:
            # 默认扬声器
            change_output_volume(self.channel_id, device=1, pc_volume=self.volume_slider.value())

    # 子页面的设备切换按钮
    def change_device_handle(self):
        if self.change_btn.isChecked():
            # 此时是耳机播放
            # 通过cus[channel_id][0]参数设置当前通道音频的播放设备，cus[channel_id][0]为1表示是耳机播放，为0表示是扬声器播放
            change_output_volume(self.channel_id, device=2)
            self.volume_slider.setValue(get_channel_volume_conf()[self.channel_id][2])
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
            print("current play device is : usb")
        else:
            # 此时是扬声器播放
            change_output_volume(self.channel_id, device=1)
            self.volume_slider.setValue(get_channel_volume_conf()[self.channel_id][1])
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))
            print("current play device is : pc")

    # 子页面的退出按钮
    def exit_handle(self):
        self.close()
