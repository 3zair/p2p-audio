import os.path
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QSlider, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
# from volume_control_utils import MyAudioUtilities
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, EDataFlow, \
#     ERole
# from ctypes import POINTER, cast

# TODO:此处为模拟子页面配置
cus = {'1': [0, 50], '2': [1, 60], '3': [0, 70], '4': [1, 80], '5': [0, 90], '6': [1, 10], '7': [0, 20], '8': [1, 30]}


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

        self.change_device_btn(channel_id)
        self.volume_control(channel_id)
        self.exit_btn()

    def change_device_btn(self, channel_id):
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
        self.change_btn.setChecked(cus[channel_id][0])
        self.change_btn.setStyleSheet("background-color:rgb(245, 245, 245)")
        self.change_btn.setObjectName("change_btn")
        # change_btn.setText("device")
        self.change_btn.clicked.connect(lambda: self.change_device(channel_id))
        if self.change_btn.isChecked():
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
        else:
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))
        self.change_btn.setIconSize(QtCore.QSize(50, 50))

    def volume_control(self, channel_id):
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
        self.volume_slider.setMaximum(32767)
        self.volume_slider.setPageStep(1024)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(cus[channel_id][1])
        # TODO：self.change_volume没办法传channel_id进去，无法修改cus里面存的音量值，所以将channel_id设置成了self属性
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
        cus[self.channel_id][1] = self.volume
        print("current volum is: ", cus[self.channel_id][1])

        # # 打印所有音频设备
        # devicelist = MyAudioUtilities.GetAllDevices()
        # i = 0
        # for device in devicelist:
        #     print(i, device)
        #     i += 1
        # print(i, "Default Output")
        # i += 1
        # print(i, "Default Input")
        # i += 1
        #
        # # TODO:deviceSel是需要设置的device的id,此处需要修改为对应的输出设备的id
        # if cus[self.channel_id][0] == 0:
        #     # 此处填写扬声器id
        #     device_id = None
        # else:
        #     # 此处填写耳机输出的id，多耳机输出需要重复操作
        #     device_id = None
        # deviceSel = device_id
        # mixer_output = devicelist[deviceSel]
        # print(mixer_output)
        # tmp = mixer_output.id
        # devices = MyAudioUtilities.GetDevice(tmp)
        #
        # # set音量值
        # interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        # volume = cast(interface, POINTER(IAudioEndpointVolume))
        # volume.SetMasterVolumeLevelScalar(self.volume / 100.0, None)

    # 子页面的设备切换按钮
    def change_device(self, channel_id):
        if self.change_btn.isChecked():
            # 此时是耳机播放
            # 通过cus[channel_id][0]参数设置当前通道音频的播放设备，cus[channel_id][0]为1表示是耳机播放，为0表示是扬声器播放
            cus[channel_id][0] = 1
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'headset.svg')))
            print("current play device is : headset")
        else:
            # 此时是扬声器播放
            cus[channel_id][0] = 0
            self.change_btn.setIcon(QIcon(os.path.join(self.static_dir, 'speaker.png')))
            print("current play device is : speaker")

    # 子页面的退出按钮
    def exit(self):
        self.close()
