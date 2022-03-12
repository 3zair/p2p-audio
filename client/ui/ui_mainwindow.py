import logging
import threading
import time
import os

from udp_client.client import ChatClient, get_speaking_users, get_speaking_channels, pop_speaking_channels, \
    pop_speaking_users
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QLabel, QFrame, QToolButton, QButtonGroup, QStackedLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QDateTime, QSize, QAbstractAnimation, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from .button_utils import QPushButtonWithColor, QToolButtonWithColor
from .ui_subwindow import UiForm2
from conf.conf import get_host, get_port

# 取消消息闪烁的队列
channels_to_stop = []
users_to_stop = []


# 设置按钮变色效果
def new_animation(parent):
    ani = QPropertyAnimation(parent, b'color')
    ani.setDuration(700)
    ani.setLoopCount(3)
    ani.setStartValue(QColor(204, 255, 204))
    ani.setEndValue(QColor(210, 210, 210))
    return ani


# 消息闪烁的线程类
class AnimaThread(QThread):
    flash_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    # 触发函数
    def run(self):
        while 1:
            time.sleep(2)
            # 需要启动闪烁动画的时候就发送信号出去
            if len(get_speaking_channels()) > 0:
                self.flash_signal.emit("channel_start")
                time.sleep(0.1)
            if len(get_speaking_users()) > 0:
                self.flash_signal.emit("user_start")
                time.sleep(0.1)
            if len(channels_to_stop) > 0:
                self.flash_signal.emit("channel_stop")
                time.sleep(0.1)
            if len(users_to_stop) > 0:
                self.flash_signal.emit("user_stop")


# 动态显示当前时间的线程类
class CurrTime(QThread):
    update_date = pyqtSignal(str)

    def run(self):
        while True:
            date = QDateTime.currentDateTime()
            current = date.toString("yyyy-MM-dd hh:mm:ss dddd")
            self.update_date.emit(str(current))
            time.sleep(1)


class UIForm(object):
    def __init__(self):
        self.btn_group = None
        self.channel_push_buttons = {}
        self.channel_rx_animation = {}
        self.channel_frames = {}

        self.user_push_buttons = []
        self.user_animation = {}
        self.phone_book_animation = {}
        self.client = ChatClient(get_host(), get_port())
        self.users = self.client.users_info
        self.channels = self.client.ChannelsInfo
        self.volume = 50
        self.chile_Win = None
        # 限制每次只能打开一个子页面
        # self.sub_window_flag = False

        # 输入设备提示框是否在展示中
        self.waring_flags = [False, False, False]
        self.static_dir = os.path.join(os.getcwd(), "statics")

    def setup_ui(self, main_form):
        print(self.client.user)
        main_form.setObjectName("main_form")
        main_form.resize(1024, 768)
        # main_form.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏的代码，注释掉是因为隐藏后无法拖动
        main_form.setMinimumSize(QtCore.QSize(1024, 768))
        main_form.setMaximumSize(QtCore.QSize(1024, 768))
        main_form.setStyleSheet("background-color:rgb(235, 235, 235);")

        main_form.setWindowTitle("Form")

        # 各个frame的初始化
        self.show_time_frame_init(main_form)
        self.channel_frame_init(main_form)
        self.top_frame_init(main_form)
        self.bottom_frame_init(main_form)
        self.user_frame_init(main_form)
        self.phone_book_change_init(main_form)
        self.right_frame_init(main_form)

        QtCore.QMetaObject.connectSlotsByName(main_form)

        threading.Thread(target=self.micro_phone_control).start()

        # 启动动态时间显示线程
        self.backend = CurrTime()
        self.backend.update_date.connect(self.showtime)
        self.backend.start()

        # 重写版动画线程启动
        self.animation_thread = AnimaThread()
        # 链接通道闪烁函数
        self.animation_thread.flash_signal.connect(self.btn_flash)
        self.animation_thread.start()

    # 顶部时间显示frame初始化
    def show_time_frame_init(self, main_form):
        show_time_frame = QtWidgets.QFrame(main_form)
        show_time_frame.setGeometry(QtCore.QRect(0, 0, 1024, 40))
        show_time_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        show_time_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        show_time_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        show_time_frame.setObjectName("show_time_frame")

        self.time_label = QLabel(show_time_frame)
        self.time_label.setFixedWidth(600)
        self.time_label.move(20, 12)

    # 时间label动态赋值
    def showtime(self, data):
        self.time_label.setText(data)
        self.time_label.setStyleSheet("font-size:18px")

    # 通道按钮的点击事件（音量控制子页面）
    def btnClicked(self, main_form):
        # 如果当前没有子窗口打开
        btn = self.sender()
        c_id = btn.objectName()
        # 实例化子窗口
        self.chile_Win = UiForm2(main_form)
        self.chile_Win.setWindowModality(Qt.ApplicationModal)
        # 初始化子窗口参数
        self.chile_Win.initUI(c_id[-1])
        # 子窗口位置
        if c_id[-1] == '1':
            self.chile_Win.move(40, 160)
        elif c_id[-1] == '2':
            self.chile_Win.move(230, 160)
        elif c_id[-1] == '3':
            self.chile_Win.move(420, 160)
        elif c_id[-1] == '4':
            self.chile_Win.move(40, 280)
        elif c_id[-1] == '5':
            self.chile_Win.move(230, 280)
        elif c_id[-1] == '6':
            self.chile_Win.move(420, 280)
        elif c_id[-1] == '7':
            self.chile_Win.move(40, 400)
        elif c_id[-1] == '8':
            self.chile_Win.move(230, 400)
        self.chile_Win.show()
        # self.chile_Win.exec_()

    # 通道按钮frame初始化
    def channel_frame_init(self, main_form):
        channels_frame = QtWidgets.QFrame(main_form)
        channels_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        channels_frame.setGeometry(QtCore.QRect(0, 145, 617, 508))
        channels_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        channels_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        channels_frame.setObjectName("channel_frame")

        i = 0

        for channel_id in self.channels.keys():
            x = 17 + (i % 3) * 200
            y = 14 + int(i / 3) * 120
            channel_frame_name = "channel_frame_{}".format(channel_id)
            self.channel_frames[channel_frame_name] = (QtWidgets.QFrame(channels_frame))
            self.channel_frames[channel_frame_name].setGeometry(QtCore.QRect(x, y, 190, 120))
            self.channel_frames[channel_frame_name].setMinimumSize(QtCore.QSize(190, 120))
            self.channel_frames[channel_frame_name].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.channel_frames[channel_frame_name].setFrameShadow(QtWidgets.QFrame.Raised)
            self.channel_frames[channel_frame_name].setObjectName(channel_frame_name)
            i += 1

            self.channel_push_buttons[channel_frame_name] = []
            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][0].setGeometry(QtCore.QRect(0, 0, 110, 120))
            self.channel_push_buttons[channel_frame_name][0].setMinimumSize(QtCore.QSize(110, 120))
            self.channel_push_buttons[channel_frame_name][0].setMaximumSize(QtCore.QSize(110, 120))
            self.channel_push_buttons[channel_frame_name][0].setStyleSheet(
                "background-color:rgb(210, 210, 210);font-size:15px;")
            self.channel_push_buttons[channel_frame_name][0].setObjectName("pushButton_name_{}".format(channel_id))
            # self.channel_push_buttons[channel_frame_name][0].setCheckable(True)

            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][0].setText("通道_{}".format(channel_id))
                self.channel_push_buttons[channel_frame_name][0].clicked.connect(lambda: self.btnClicked(main_form))
            else:
                self.channel_push_buttons[channel_frame_name][0].setEnabled(False)

            self.channel_push_buttons[channel_frame_name].append(
                QPushButtonWithColor(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][1].setGeometry(QtCore.QRect(110, 0, 80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setStyleSheet(
                "background-color:rgb(210, 210, 210);font-size:15px;")
            self.channel_push_buttons[channel_frame_name][1].setObjectName(channel_id)
            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][1].setText("RX")
                self.channel_push_buttons[channel_frame_name][1].setCheckable(True)
                self.channel_push_buttons[channel_frame_name][1].clicked.connect(self.channel_rx_click_handle)
                # 增加RX按钮闪烁动画，等有消息时会闪烁
                self.channel_rx_animation[channel_id] = new_animation(self.channel_push_buttons[channel_frame_name][1])
            else:
                self.channel_push_buttons[channel_frame_name][1].setEnabled(False)

            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][2].setGeometry(QtCore.QRect(110, 60, 80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setStyleSheet(
                "background-color:rgb(210, 210, 210);font-size:15px;")
            self.channel_push_buttons[channel_frame_name][2].setObjectName(channel_id)

            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][2].setText("TX")
                self.channel_push_buttons[channel_frame_name][2].setCheckable(True)
                self.channel_push_buttons[channel_frame_name][2].clicked.connect(self.channel_tx_click_handle)
            else:
                self.channel_push_buttons[channel_frame_name][2].setEnabled(False)

            print(channel_id, self.channels[channel_id])

    # 顶部按钮frame初始化
    def top_frame_init(self, main_form):
        # top frame
        top_frame = QtWidgets.QFrame(main_form)
        top_frame.setGeometry(QtCore.QRect(0, 40, 1024, 105))
        top_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        # top_frame.setGeometry(QtCore.QRect(20, 40, 900, 95))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        top_1 = QtWidgets.QPushButton(top_frame)
        top_1.setGeometry(QtCore.QRect(17, 8, 90, 89))
        top_1.setMinimumSize(QtCore.QSize(90, 89))
        top_1.setMaximumSize(QtCore.QSize(90, 89))
        top_1.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        top_1.setObjectName("top_1")
        top_1.setText("更多功能")
        top_1.clicked.connect(self.show_message)

        top_2 = QtWidgets.QPushButton(top_frame)
        top_2.setGeometry(QtCore.QRect(117, 8, 90, 89))
        top_2.setMinimumSize(QtCore.QSize(90, 89))
        top_2.setMaximumSize(QtCore.QSize(90, 89))
        top_2.setStyleSheet("background-color:rgb(208, 237, 251);")
        top_2.setObjectName("top_2")
        top_2.setText("扬声通话")
        top_2.setEnabled(False)
        #
        top_3 = QtWidgets.QPushButton(top_frame)
        top_3.setGeometry(QtCore.QRect(217, 8, 90, 89))
        top_3.setMinimumSize(QtCore.QSize(90, 89))
        top_3.setMaximumSize(QtCore.QSize(90, 89))
        top_3.setStyleSheet("background-color:rgb(208, 237, 251);")
        top_3.setObjectName("top_3")
        top_3.setText("音量调节")
        top_3.clicked.connect(self.show_message)
        top_3.setEnabled(False)

        top_4 = QtWidgets.QPushButton(top_frame)
        top_4.setGeometry(QtCore.QRect(317, 8, 90, 89))
        top_4.setMinimumSize(QtCore.QSize(90, 89))
        top_4.setMaximumSize(QtCore.QSize(90, 89))
        top_4.setStyleSheet("background-color:rgb(208, 237, 251);")
        top_4.setObjectName("top_4")
        top_4.setText("亮度调节")
        top_4.setEnabled(False)

        top_5 = QtWidgets.QPushButton(top_frame)
        top_5.setGeometry(QtCore.QRect(417, 8, 90, 89))
        top_5.setMinimumSize(QtCore.QSize(90, 89))
        top_5.setMaximumSize(QtCore.QSize(90, 89))
        top_5.setStyleSheet("background-color:rgb(208, 237, 251);")
        top_5.setObjectName("top_5")
        top_5.setText("PTT电话")
        top_5.setEnabled(False)

        top_6 = QtWidgets.QPushButton(top_frame)
        top_6.setGeometry(QtCore.QRect(517, 8, 90, 89))
        top_6.setMinimumSize(QtCore.QSize(90, 89))
        top_6.setMaximumSize(QtCore.QSize(90, 89))
        top_6.setStyleSheet("background-color:rgb(208, 237, 251);")
        top_6.setObjectName("top_6")
        top_6.setText("通话日志")
        top_6.setEnabled(False)

        top_7 = QtWidgets.QPushButton(top_frame)
        top_7.setGeometry(QtCore.QRect(617, 8, 90, 89))
        top_7.setMinimumSize(QtCore.QSize(90, 89))
        top_7.setMaximumSize(QtCore.QSize(90, 89))
        top_7.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        top_7.setObjectName("top_7")
        # bottom_7.setText("f7")
        top_7.setEnabled(False)

        top_8 = QtWidgets.QPushButton(top_frame)
        top_8.setGeometry(QtCore.QRect(717, 8, 90, 89))
        top_8.setMinimumSize(QtCore.QSize(90, 89))
        top_8.setMaximumSize(QtCore.QSize(90, 89))
        top_8.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        top_8.setObjectName("top_8")
        # bottom_8.setText("f8")
        top_8.setEnabled(False)

        top_9 = QtWidgets.QPushButton(top_frame)
        top_9.setGeometry(QtCore.QRect(817, 8, 90, 89))
        top_9.setMinimumSize(QtCore.QSize(90, 89))
        top_9.setMaximumSize(QtCore.QSize(90, 89))
        top_9.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        top_9.setObjectName("top_9")
        # bottom_9.setText("f9")
        top_9.setEnabled(False)

        top_10 = QtWidgets.QPushButton(top_frame)
        top_10.setGeometry(QtCore.QRect(917, 8, 90, 89))
        top_10.setMinimumSize(QtCore.QSize(90, 89))
        top_10.setMaximumSize(QtCore.QSize(90, 89))
        top_10.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        top_10.setObjectName("top_10")
        top_10.clicked.connect(self.show_message)
        top_10.setIcon(QIcon(os.path.join(self.static_dir, 'settings.svg')))
        top_10.setIconSize(QSize(60, 60))

    # 顶部按钮frame初始化
    def right_frame_init(self, main_form):
        # top frame
        right_frame = QtWidgets.QFrame(main_form)
        right_frame.setGeometry(QtCore.QRect(907, 145, 117, 508))
        right_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        # top_frame.setGeometry(QtCore.QRect(20, 40, 900, 95))
        right_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        right_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        right_frame.setObjectName("right_frame")

        right_1 = QtWidgets.QPushButton(right_frame)
        right_1.setGeometry(QtCore.QRect(10, 14, 90, 90))
        right_1.setMinimumSize(QtCore.QSize(90, 90))
        right_1.setMaximumSize(QtCore.QSize(90, 90))
        right_1.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        right_1.setObjectName("right_1")
        # right_1.setText("fun_1")
        right_1.clicked.connect(self.show_message)

        right_2 = QtWidgets.QPushButton(right_frame)
        right_2.setGeometry(QtCore.QRect(10, 114, 90, 90))
        right_2.setMinimumSize(QtCore.QSize(90, 90))
        right_2.setMaximumSize(QtCore.QSize(90, 90))
        right_2.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        right_2.setObjectName("right_2")
        # right_2.setText("fun_2")
        right_2.setEnabled(False)

        right_3 = QtWidgets.QPushButton(right_frame)
        right_3.setGeometry(QtCore.QRect(10, 214, 90, 90))
        right_3.setMinimumSize(QtCore.QSize(90, 90))
        right_3.setMaximumSize(QtCore.QSize(90, 90))
        right_3.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        right_3.setObjectName("right_3")
        # right_3.setText("fun_3")
        right_3.setEnabled(False)

        right_4 = QtWidgets.QPushButton(right_frame)
        right_4.setGeometry(QtCore.QRect(10, 314, 90, 90))
        right_4.setMinimumSize(QtCore.QSize(90, 90))
        right_4.setMaximumSize(QtCore.QSize(90, 90))
        right_4.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        right_4.setObjectName("right_4")
        # right_4.setText("fun_4")
        right_4.setEnabled(False)

        right_5 = QtWidgets.QPushButton(right_frame)
        right_5.setGeometry(QtCore.QRect(10, 412, 90, 88))
        right_5.setMinimumSize(QtCore.QSize(90, 88))
        right_5.setMaximumSize(QtCore.QSize(90, 88))
        right_5.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        right_5.setObjectName("right_5")
        # right_5.setText("fun_5")
        right_5.setEnabled(False)

    # 底部按钮frame初始化
    def bottom_frame_init(self, main_form):
        # bottom frame
        bottom_frame = QtWidgets.QFrame(main_form)
        bottom_frame.setGeometry(QtCore.QRect(0, 653, 1024, 115))
        bottom_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        bottom_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        bottom_frame.setObjectName("bottom_frame")

        bottom_1 = QtWidgets.QPushButton(bottom_frame)
        bottom_1.setGeometry(QtCore.QRect(17, 10, 90, 89))
        bottom_1.setMinimumSize(QtCore.QSize(90, 89))
        bottom_1.setMaximumSize(QtCore.QSize(90, 89))
        bottom_1.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_1.setObjectName("bottom_1")
        bottom_1.setText("换页")

        bottom_2 = QtWidgets.QPushButton(bottom_frame)
        bottom_2.setGeometry(QtCore.QRect(117, 10, 90, 89))
        bottom_2.setMinimumSize(QtCore.QSize(90, 89))
        bottom_2.setMaximumSize(QtCore.QSize(90, 89))
        bottom_2.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_2.setObjectName("bottom_2")
        # bottom_2.setText("f2")
        bottom_2.setEnabled(False)

        bottom_3 = QtWidgets.QPushButton(bottom_frame)
        bottom_3.setGeometry(QtCore.QRect(217, 10, 90, 89))
        bottom_3.setMinimumSize(QtCore.QSize(90, 89))
        bottom_3.setMaximumSize(QtCore.QSize(90, 89))
        bottom_3.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_3.setObjectName("bottom_3")
        # bottom_3.setText("f3")
        bottom_3.setEnabled(False)

        bottom_4 = QtWidgets.QPushButton(bottom_frame)
        bottom_4.setGeometry(QtCore.QRect(317, 10, 90, 89))
        bottom_4.setMinimumSize(QtCore.QSize(90, 89))
        bottom_4.setMaximumSize(QtCore.QSize(90, 89))
        bottom_4.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_4.setObjectName("bottom_4")
        # bottom_4.setText("f4")
        bottom_4.setEnabled(False)

        bottom_5 = QtWidgets.QPushButton(bottom_frame)
        bottom_5.setGeometry(QtCore.QRect(417, 10, 90, 89))
        bottom_5.setMinimumSize(QtCore.QSize(90, 89))
        bottom_5.setMaximumSize(QtCore.QSize(90, 89))
        bottom_5.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_5.setObjectName("bottom_5")
        # bottom_5.setText("f5")
        bottom_5.setEnabled(False)

        bottom_6 = QtWidgets.QPushButton(bottom_frame)
        bottom_6.setGeometry(QtCore.QRect(517, 10, 90, 89))
        bottom_6.setMinimumSize(QtCore.QSize(90, 89))
        bottom_6.setMaximumSize(QtCore.QSize(90, 89))
        bottom_6.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_6.setObjectName("bottom_6")
        # bottom_6.setText("f6")
        bottom_6.setEnabled(False)

        bottom_7 = QtWidgets.QPushButton(bottom_frame)
        bottom_7.setGeometry(QtCore.QRect(617, 10, 90, 89))
        bottom_7.setMinimumSize(QtCore.QSize(90, 89))
        bottom_7.setMaximumSize(QtCore.QSize(90, 89))
        bottom_7.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_7.setObjectName("bottom_7")
        # bottom_7.setText("f7")
        bottom_7.setEnabled(False)

        bottom_8 = QtWidgets.QPushButton(bottom_frame)
        bottom_8.setGeometry(QtCore.QRect(717, 10, 90, 89))
        bottom_8.setMinimumSize(QtCore.QSize(90, 89))
        bottom_8.setMaximumSize(QtCore.QSize(90, 89))
        bottom_8.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_8.setObjectName("bottom_8")
        # bottom_8.setText("f8")
        bottom_8.setEnabled(False)

        bottom_9 = QtWidgets.QPushButton(bottom_frame)
        bottom_9.setGeometry(QtCore.QRect(817, 10, 90, 89))
        bottom_9.setMinimumSize(QtCore.QSize(90, 89))
        bottom_9.setMaximumSize(QtCore.QSize(90, 89))
        bottom_9.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_9.setObjectName("exit")
        # bottom_9.setText("退出")

        bottom_10 = QtWidgets.QPushButton(bottom_frame)
        bottom_10.setGeometry(QtCore.QRect(917, 10, 90, 89))
        bottom_10.setMinimumSize(QtCore.QSize(90, 89))
        bottom_10.setMaximumSize(QtCore.QSize(90, 89))
        bottom_10.setStyleSheet("background-color:rgb(208, 237, 251);font-size:15px;")
        bottom_10.setObjectName("company_logo")
        bottom_10.setIcon(QIcon(os.path.join(self.static_dir, 'logo.png')))
        bottom_10.clicked.connect(self.exit_click_handle)
        bottom_10.setIconSize(QSize(60, 60))

    # 电话簿frame初始化
    def user_frame_init(self, main_form):
        # todo
        user_frame = QtWidgets.QFrame(main_form)
        user_frame.setGeometry(QtCore.QRect(617, 145, 290, 428))
        user_frame.setStyleSheet("background-color:rgb(235, 235, 235);")
        user_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        user_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        user_frame.setObjectName("user_frame")

        # 创建堆叠布局
        self.stacked_layout = QStackedLayout(user_frame)

        for page in range(3):
            main_frame = QtWidgets.QWidget()
            rom_frame = QFrame(main_frame)
            rom_frame.setGeometry(0, 0, 290, 428)
            rom_frame.setFrameShape(QFrame.Panel)
            rom_frame.setFrameShadow(QFrame.Raised)

            self.stacked_layout.addWidget(main_frame)
            page_user_btns = []
            i = 0
            for user_num in range(1, 13):
                x = 6 + (i % 3) * 96
                y = 14 + int(i / 3) * 100
                user_btn = QPushButtonWithColor(rom_frame)
                user_btn.setGeometry(QtCore.QRect(x, y, 86, 88))
                user_btn.setMinimumSize(QtCore.QSize(86, 88))
                user_btn.setMaximumSize(QtCore.QSize(86, 88))
                user_btn.setCheckable(True)
                user_btn.setStyleSheet("background-color:rgb(210, 210, 210);font-size:15px;")
                user_btn.setEnabled(False)
                page_user_btns.append(user_btn)
                i += 1
            self.user_push_buttons.append(page_user_btns)

        logging.info("user:{} l:{}".format(self.client.users_info, len(self.user_push_buttons)))
        for user in self.client.users_info.values():
            page_id = user["page"] - 1
            if 2 >= page_id >= 0:
                for k in range(len(self.user_push_buttons[page_id])):
                    if not self.user_push_buttons[page_id][k].isEnabled():
                        self.user_push_buttons[page_id][k].setText(user["name"])
                        self.user_push_buttons[page_id][k].setObjectName(user["id"])
                        self.user_push_buttons[page_id][k].setStyleSheet(
                            "background-color:rgb(210, 210, 210);font-size:15px;")
                        self.user_push_buttons[page_id][k].setEnabled(True)
                        self.user_push_buttons[page_id][k].clicked.connect(self.user_click_handle)
                        # 增加RX按钮闪烁动画，等有消息时会闪烁
                        self.user_animation[user["id"]] = new_animation(self.user_push_buttons[page_id][k])
                        break

    # 电话簿换页frame初始化
    def phone_book_change_init(self, main_form):
        self.frame_tool = QFrame(main_form)
        self.frame_tool.setObjectName("frame_tool")
        self.frame_tool.setGeometry(QtCore.QRect(617, 559, 290, 94))
        self.frame_tool.setStyleSheet("background-color:rgb(235, 235, 235);")
        self.frame_tool.setFrameShape(QFrame.Panel)
        self.frame_tool.setFrameShadow(QFrame.Raised)

        self.btn_group = QButtonGroup(self.frame_tool)
        btn_size = [91, 96, 93]
        locations = [6, 97, 193]
        for i in range(3):
            phone_book_btn = QToolButtonWithColor(self.frame_tool)
            phone_book_btn.setStyleSheet(
                "background-color:rgb(183, 183, 183);font-size:14px;border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
            phone_book_btn.setCheckable(True)
            phone_book_btn.setText("电话本_{}".format(i + 1))
            phone_book_btn.setObjectName("menu_btn_{}".format(i))
            phone_book_btn.resize(btn_size[i], 80)
            phone_book_btn.move(locations[i], 0)
            phone_book_btn.setAutoRaise(True)
            self.phone_book_animation[i] = new_animation(phone_book_btn)
            self.btn_group.addButton(phone_book_btn, i)
            self.btn_group.buttonClicked.connect(self.phone_book_click_handle)
        # 默认为第一页
        self.btn_group.button(0).setStyleSheet(
            "background-color:rgb(210, 210, 210);font-size:14px;border-bottom-right-radius:15px;border-bottom-left-radius:15px;")

    # message提示框
    def show_message(self):
        QMessageBox.information(self, "标题", "更多功能正在开发中",
                                QMessageBox.Yes)

    # 错误提示框
    def show_error_message(self, err_msg):
        QMessageBox.critical(self, "错误", err_msg)

    # 系统退出按钮点击事件
    def exit_click_handle(self):
        reply = QMessageBox.question(self, '警告', "系统将退出，是否确认?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()
            self.client.exit()
            del self.client

    # 通道的rx按钮的点击事件
    def channel_rx_click_handle(self):
        rx_button = self.sender()
        checked = rx_button.isChecked()
        channel_id = rx_button.objectName()

        if not checked and channel_id in self.client.cur_listening_channels:
            rx_button.setStyleSheet("background-color:rgb(210, 210, 210);")

            self.client.del_listening_channel(channel_id)
            # 取消
            tx_button = self.channel_push_buttons["channel_frame_{}".format(channel_id)][2]
            tx_checked = tx_button.isChecked()
            if tx_checked:
                if self.client.cur_speaking_channel is not None and self.client.cur_speaking_channel == channel_id:
                    ret = self.cancel_occupy_channel(channel_id)
                    if ret is True:
                        self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setStyleSheet(
                            "background-color:rgb(210, 210, 210);font-size:15px;")
                        self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setChecked(False)
                    else:
                        self.client.cur_speaking_channel = channel_id
                        logging.error("取消占用channel {} err: {}".format(channel_id, ret))
                        self.show_error_message("通道{}释放失败".format(channel_id))

        if checked and channel_id not in self.client.cur_listening_channels:
            rx_button.setStyleSheet("background-color:rgb(128, 255, 128);")
            self.client.add_listening_channel(channel_id)
            # 按钮闪烁停止
            global channels_to_stop
            channels_to_stop.append(channel_id)

    # 通道的tx按钮的点击事件
    def channel_tx_click_handle(self):
        tx_button = self.sender()
        checked = tx_button.isChecked()
        channel_id = tx_button.objectName()
        if checked:
            # 开始占用通道 channel_id
            # 检测当前是否占用其他某个信道
            cur_channel = self.client.cur_speaking_channel
            if self.client.cur_speaking_channel is not None:
                ret = self.cancel_occupy_channel(cur_channel)
                if ret is True:
                    self.channel_push_buttons["channel_frame_{}".format(cur_channel)][2].setStyleSheet(
                        "background-color:rgb(210, 210, 210);font-size:15px;")
                    self.channel_push_buttons["channel_frame_{}".format(cur_channel)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败

                    tx_button.setStyleSheet("background-color:rgb(128, 255, 128);")
                    self.client.cur_speaking_channel = cur_channel

                    tx_button.setChecked(False)
                    logging.error("释放channel {} err: {}".format(cur_channel, ret))
                    self.show_error_message("通道{}释放失败".format(cur_channel))

            # 去占用
            ret = self.client.choose_channel(channel_id)
            if ret is True:
                self.client.start_send_to_channel()
                tx_button.setStyleSheet("background-color:rgb(128, 255, 128);font-size:15px;")
                # 监听当前通道
                rx_button = self.channel_push_buttons["channel_frame_{}".format(channel_id)][1]
                checked = rx_button.isChecked()
                if channel_id not in self.client.cur_listening_channels:
                    self.client.add_listening_channel(channel_id)
                if not checked:
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][1].setChecked(True)
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][1].setStyleSheet(
                        "background-color:rgb(128, 255, 128);font-size:15px;")
            else:
                tx_button.setChecked(False)
                logging.error("choose_channel err: {}".format(ret))
                self.show_error_message("通道{}占用失败".format(channel_id))
        else:
            # 取消占用通道 channel_id
            if self.client.cur_speaking_channel is not None:
                ret = self.cancel_occupy_channel(channel_id)
                if ret is True:
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setStyleSheet(
                        "background-color:rgb(210, 210, 210);font-size:15px;")
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败
                    tx_button.setStyleSheet("background-color:rgb(128, 255, 128);")
                    self.client.cur_speaking_channel = channel_id
                    tx_button.setChecked(True)
                    logging.error("取消占用channel {} err: {}".format(channel_id, ret))
                    self.show_error_message("通道{}释放失败".format(channel_id))

    # 单对单通话点击事件
    def user_click_handle(self):
        user_btn = self.sender()
        checked = user_btn.isChecked()
        user_id = user_btn.objectName()
        if checked:

            if self.client.cur_connect_user is not None and not self.client.cur_connect_user == user_id:
                self.client.stop_send_to_user()
            user_btn.setStyleSheet("background-color:rgb(128, 255, 128);font-size:15px;")
            self.client.send_to_user(user_id)
            # 停止闪烁
            # 按钮闪烁停止
            global users_to_stop
            users_to_stop.append(user_id)
        else:
            user_btn.setStyleSheet("background-color:rgb(210, 210, 210);font-size:15px;")
            self.client.stop_send_to_user()

    # 取消占用通道
    def cancel_occupy_channel(self, channel_id, retry=3):
        cancel_ret = self.client.cancel_channel(channel_id)
        i = 0
        while cancel_ret is not True and i < retry:
            time.sleep(1)
            if cancel_ret is True:
                return True
            i += 1
        return cancel_ret

    # 电话簿换页按钮1
    def phone_book_click_handle(self):
        index = self.btn_group.checkedId()
        if self.stacked_layout.currentIndex() != index:
            self.stacked_layout.setCurrentIndex(index)
            for btn in self.btn_group.buttons():
                btn.setStyleSheet(
                    "background-color:rgb(183, 183, 183);font-size:14px;border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
            if self.btn_group.button(index).isChecked():
                self.btn_group.button(index).setStyleSheet(
                    "background-color:rgb(210, 210, 210);font-size:14px;border-bottom-right-radius:15px;border-bottom-left-radius:15px;")

    # channel闪烁动画线程的槽函数，接收到信号启动闪烁动画
    def btn_flash(self, data):
        if data == "channel_start":
            channel_id = pop_speaking_channels()
            logging.info("channel_start{}".format(channel_id))
            self.channel_rx_animation[channel_id].start(QAbstractAnimation.KeepWhenStopped)

        elif data == "user_start":
            user_id = pop_speaking_users()
            logging.info("user_start{}".format(user_id))
            self.user_animation[user_id].start(QAbstractAnimation.KeepWhenStopped)
            self.phone_book_animation[self.users[user_id]["page"] - 1].start(QAbstractAnimation.KeepWhenStopped)
        elif data == "channel_stop":
            global channels_to_stop
            channel_id = channels_to_stop.pop()
            logging.info("channel_stop{}".format(channel_id))
            self.channel_rx_animation[channel_id].stop()
            self.channel_rx_animation[channel_id].setCurrentTime(700)

        elif data == "user_stop":
            global users_to_stop
            user_id = users_to_stop.pop()
            logging.info("user_stop{}".format(user_id))
            self.user_animation[user_id].stop()
            self.user_animation[user_id].setCurrentTime(700)
            self.phone_book_animation[self.users[user_id]["page"] - 1].stop()
            self.phone_book_animation[self.users[user_id]["page"] - 1].setCurrentTime(700)

    # 麦克风控制
    def micro_phone_control(self):
        while self.client and not self.client.exit_flag:
            # print(" DTR:", self.client.ser.dtr, " CD:", self.client.ser.cd, " DSR:", self.client.ser.dsr, " CTS:",
            #       self.client.ser.cts)
            # level 1
            if self.client.ser.cd:
                if len(self.client.devices["inputs"]) < 1:
                    logging.info("请插入输入设备1(CD)")
                elif not self.client.input_device_flags[self.client.devices["inputs"][0]]:
                    self.client.start_record_voice_data_for_channel(self.client.devices["inputs"][0])
            if not self.client.ser.cd and len(self.client.devices["inputs"]) >= 1 \
                    and self.client.input_device_flags[self.client.devices["inputs"][0]]:
                self.client.stop_record_voice_data_for_channel(self.client.devices["inputs"][0])
            # level 2
            if self.client.ser.cts:
                if len(self.client.devices["inputs"]) < 2:
                    logging.info("请插入输入设备2(DSR)")
                elif not self.client.input_device_flags[self.client.devices["inputs"][1]]:
                    self.client.start_record_voice_data_for_channel(self.client.devices["inputs"][1])
            if not self.client.ser.cts and len(self.client.devices["inputs"]) >= 2 \
                    and self.client.input_device_flags[self.client.devices["inputs"][1]]:
                self.client.stop_record_voice_data_for_channel(self.client.devices["inputs"][1])
            # # level 3
            # if self.client.ser.dsr:
            #     if len(self.client.devices["inputs"]) < 3:
            #         # self.show_error_message("请插入输入设备3(CTS)")
            #         logging.info("请插入输入设备3(CTS)")
            #     elif not self.client.input_device_flags[self.client.devices["inputs"][2]]:
            #         self.client.start_record_voice_data_for_channel(self.client.devices["inputs"][2])
            # if not self.client.ser.dsr and len(self.client.devices["inputs"]) >= 3 \
            #         and self.client.input_device_flags[self.client.devices["inputs"][2]]:
            #     self.client.stop_record_voice_data_for_channel(self.client.devices["inputs"][2])
            time.sleep(0.22)
