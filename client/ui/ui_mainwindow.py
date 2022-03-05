import logging
import threading
import time

from udp_client.client import ChatClient
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QSlider, QDialog, QFrame, QToolButton, QButtonGroup, QStackedLayout, QStatusBar
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QColor
from .ui_subwindow import UiForm2
from conf.conf import get_host, get_port


class UIForm(object):
    def __init__(self):
        self.channel_push_buttons = {}
        self.channel_frames = {}
        self.client = ChatClient(get_host(), get_port())
        self.users = self.client.ClientsInfo
        self.channels = self.client.ChannelsInfo
        self.volume = 50
        self.chile_Win = None

        # 输入设备提示框是否在展示中
        self.waring_flags = [False, False, False]

    def setup_ui(self, main_form):
        print(self.client.user)
        main_form.setObjectName("main_form")
        main_form.resize(1024, 768)
        # main_form.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏的代码，注释掉是因为隐藏后无法拖动
        main_form.setMinimumSize(QtCore.QSize(1024, 768))
        main_form.setMaximumSize(QtCore.QSize(1024, 768))
        main_form.setStyleSheet("background-color:rgb(179, 179, 179);")

        main_form.setWindowTitle("Form")

        self.channel_frame_init(main_form)
        self.top_frame_init(main_form)
        self.bottom_frame_init(main_form)
        self.user_frame_init(main_form)
        self.phone_book_change_init(main_form)

        # self.retranslateUi(main_form)
        QtCore.QMetaObject.connectSlotsByName(main_form)
        #threading.Thread(target=self.micro_phone_control).start()

    def btnClicked(self, main_form):
        btn = self.sender()
        c_id = btn.objectName()
        # 实例化子窗口
        self.chile_Win = UiForm2(main_form)
        # 初始化子窗口参数
        self.chile_Win.initUI(c_id[-1])
        self.chile_Win.setWindowModality(Qt.NonModal)
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
        # self.chile_Win.show()
        self.chile_Win.exec_()

    def channel_frame_init(self, main_form):
        channels_frame = QtWidgets.QFrame(main_form)
        channels_frame.setGeometry(QtCore.QRect(20, 145, 570, 480))
        channels_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        channels_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        channels_frame.setObjectName("channel_frame")

        i = 0

        for channel_id in self.channels.keys():
            x = 0 + (i % 3) * 190
            y = 0 + int(i / 3) * 120
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
            self.channel_push_buttons[channel_frame_name][0].setStyleSheet("background-color:rgb(245, 245, 245);")
            self.channel_push_buttons[channel_frame_name][0].setObjectName("pushButton_name_{}".format(channel_id))
            # self.channel_push_buttons[channel_frame_name][0].setCheckable(True)

            self.channel_push_buttons[channel_frame_name][0].setText("通道_{}".format(channel_id))
            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][0].clicked.connect(lambda: self.btnClicked(main_form))
            else:
                self.channel_push_buttons[channel_frame_name][0].setEnabled(False)


            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][1].setGeometry(QtCore.QRect(110, 0, 80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setStyleSheet("background-color:rgb(245, 245, 245);")

            self.channel_push_buttons[channel_frame_name][1].setObjectName(channel_id)

            self.channel_push_buttons[channel_frame_name][1].setText("RX")
            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][1].setCheckable(True)
                self.channel_push_buttons[channel_frame_name][1].clicked.connect(self.channel_rx_click_handle)
            else:
                self.channel_push_buttons[channel_frame_name][1].setEnabled(False)

            # TODO:某通道有消息时，对应的RX按钮变色

            # self.channel_push_buttons[channel_frame_name][1].animation.setKeyValueAt(0.1, QColor(0, 255, 0))


            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][2].setGeometry(QtCore.QRect(110, 60, 80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setStyleSheet("background-color:rgb(245, 245, 245);")
            self.channel_push_buttons[channel_frame_name][2].setObjectName(channel_id)

            self.channel_push_buttons[channel_frame_name][2].setText("TX")
            if self.channels[channel_id]["status"] == 1:
                self.channel_push_buttons[channel_frame_name][2].setCheckable(True)
                self.channel_push_buttons[channel_frame_name][2].clicked.connect(self.channel_tx_click_handle)
            else:
                self.channel_push_buttons[channel_frame_name][2].setEnabled(False)

            print(channel_id, self.channels[channel_id])


    def top_frame_init(self, main_form):
        # top frame
        top_frame = QtWidgets.QFrame(main_form)
        top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        # top_frame.setGeometry(QtCore.QRect(20, 40, 900, 95))
        top_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        top_frame.setObjectName("top_frame")

        top_1 = QtWidgets.QPushButton(top_frame)
        top_1.setGeometry(QtCore.QRect(0, 0, 98, 95))
        top_1.setMinimumSize(QtCore.QSize(98, 95))
        top_1.setMaximumSize(QtCore.QSize(98, 95))
        top_1.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_1.setObjectName("top_1")
        top_1.setText("更多功能")
        top_1.clicked.connect(self.show_message)

        # top_2 = QtWidgets.QPushButton(top_frame)
        # top_2.setGeometry(QtCore.QRect(98, 0, 98, 95))
        # top_2.setMinimumSize(QtCore.QSize(98, 95))
        # top_2.setMaximumSize(QtCore.QSize(98, 95))
        # top_2.setStyleSheet("background-color:rgb(111, 255, 248);")
        # top_2.setObjectName("top_2")
        # top_2.setText("扬声通话")
        #
        # top_3 = QtWidgets.QPushButton(top_frame)
        # top_3.setGeometry(QtCore.QRect(196, 0, 98, 95))
        # top_3.setMinimumSize(QtCore.QSize(98, 95))
        # top_3.setMaximumSize(QtCore.QSize(98, 95))
        # top_3.setStyleSheet("background-color:rgb(111, 255, 248);")
        # top_3.setObjectName("top_3")
        # top_3.setText("音量调节")
        # top_3.clicked.connect(self.show_message)
        #
        # top_4 = QtWidgets.QPushButton(top_frame)
        # top_4.setGeometry(QtCore.QRect(294, 0, 98, 95))
        # top_4.setMinimumSize(QtCore.QSize(98, 95))
        # top_4.setMaximumSize(QtCore.QSize(98, 95))
        # top_4.setStyleSheet("background-color:rgb(111, 255, 248);")
        # top_4.setObjectName("top_4")
        # top_4.setText("亮度调节")
        #
        # top_5 = QtWidgets.QPushButton(top_frame)
        # top_5.setGeometry(QtCore.QRect(392, 0, 98, 95))
        # top_5.setMinimumSize(QtCore.QSize(98, 95))
        # top_5.setMaximumSize(QtCore.QSize(98, 95))
        # top_5.setStyleSheet("background-color:rgb(111, 255, 248);")
        # top_5.setObjectName("top_5")
        # top_5.setText("PTT电话")
        #
        # top_6 = QtWidgets.QPushButton(top_frame)
        # top_6.setGeometry(QtCore.QRect(490, 0, 98, 95))
        # top_6.setMinimumSize(QtCore.QSize(98, 95))
        # top_6.setMaximumSize(QtCore.QSize(98, 95))
        # top_6.setStyleSheet("background-color:rgb(111, 255, 248);")
        # top_6.setObjectName("top_6")
        # top_6.setText("通话日志")

    def bottom_frame_init(self, main_form):
        # bottom frame
        bottom_frame = QtWidgets.QFrame(main_form)
        bottom_frame.setGeometry(QtCore.QRect(20, 660, 980, 100))
        bottom_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        bottom_frame.setObjectName("bottom_frame")

        bottom_1 = QtWidgets.QPushButton(bottom_frame)
        bottom_1.setGeometry(QtCore.QRect(0, 0, 98, 100))
        bottom_1.setMinimumSize(QtCore.QSize(98, 100))
        bottom_1.setMaximumSize(QtCore.QSize(98, 100))
        bottom_1.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_1.setObjectName("bottom_1")
        bottom_1.setText("换页")

        bottom_2 = QtWidgets.QPushButton(bottom_frame)
        bottom_2.setGeometry(QtCore.QRect(98, 0, 98, 100))
        bottom_2.setMinimumSize(QtCore.QSize(98, 100))
        bottom_2.setMaximumSize(QtCore.QSize(98, 100))
        bottom_2.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_2.setObjectName("bottom_2")
        bottom_2.setText("f2")

        bottom_3 = QtWidgets.QPushButton(bottom_frame)
        bottom_3.setGeometry(QtCore.QRect(196, 0, 98, 100))
        bottom_3.setMinimumSize(QtCore.QSize(98, 100))
        bottom_3.setMaximumSize(QtCore.QSize(98, 100))
        bottom_3.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_3.setObjectName("bottom_3")
        bottom_3.setText("f3")

        bottom_4 = QtWidgets.QPushButton(bottom_frame)
        bottom_4.setGeometry(QtCore.QRect(294, 0, 98, 100))
        bottom_4.setMinimumSize(QtCore.QSize(98, 100))
        bottom_4.setMaximumSize(QtCore.QSize(98, 100))
        bottom_4.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_4.setObjectName("bottom_4")
        bottom_4.setText("f4")

        bottom_5 = QtWidgets.QPushButton(bottom_frame)
        bottom_5.setGeometry(QtCore.QRect(392, 0, 98, 100))
        bottom_5.setMinimumSize(QtCore.QSize(98, 100))
        bottom_5.setMaximumSize(QtCore.QSize(98, 100))
        bottom_5.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_5.setObjectName("bottom_5")
        bottom_5.setText("f5")

        bottom_6 = QtWidgets.QPushButton(bottom_frame)
        bottom_6.setGeometry(QtCore.QRect(490, 0, 98, 100))
        bottom_6.setMinimumSize(QtCore.QSize(98, 100))
        bottom_6.setMaximumSize(QtCore.QSize(98, 100))
        bottom_6.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_6.setObjectName("bottom_6")
        bottom_6.setText("f6")

        bottom_7 = QtWidgets.QPushButton(bottom_frame)
        bottom_7.setGeometry(QtCore.QRect(588, 0, 98, 100))
        bottom_7.setMinimumSize(QtCore.QSize(98, 100))
        bottom_7.setMaximumSize(QtCore.QSize(98, 100))
        bottom_7.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_7.setObjectName("bottom_7")
        bottom_7.setText("f7")

        bottom_8 = QtWidgets.QPushButton(bottom_frame)
        bottom_8.setGeometry(QtCore.QRect(686, 0, 98, 100))
        bottom_8.setMinimumSize(QtCore.QSize(98, 100))
        bottom_8.setMaximumSize(QtCore.QSize(98, 100))
        bottom_8.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_8.setObjectName("bottom_8")
        bottom_8.setText("f8")

        bottom_9 = QtWidgets.QPushButton(bottom_frame)
        bottom_9.setGeometry(QtCore.QRect(784, 0, 98, 100))
        bottom_9.setMinimumSize(QtCore.QSize(98, 100))
        bottom_9.setMaximumSize(QtCore.QSize(98, 100))
        bottom_9.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_9.setObjectName("bottom_9")
        bottom_9.setText("f9")

        bottom_10 = QtWidgets.QPushButton(bottom_frame)
        bottom_10.setGeometry(QtCore.QRect(882, 0, 98, 100))
        bottom_10.setMinimumSize(QtCore.QSize(98, 100))
        bottom_10.setMaximumSize(QtCore.QSize(98, 100))
        bottom_10.setStyleSheet("background-color:rgb(196, 255, 216);")
        bottom_10.setObjectName("exit")
        bottom_10.clicked.connect(self.exit_click_handle)
        bottom_10.setText("退出")

    def user_frame_init(self, main_form):
        # todo
        user_frame = QtWidgets.QFrame(main_form)
        user_frame.setGeometry(QtCore.QRect(600, 145, 400, 400))
        user_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        user_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        user_frame.setObjectName("user_frame")

        # 创建堆叠布局
        self.stacked_layout = QStackedLayout(user_frame)

        # 第一个布局界面
        self.main_frame1 = QtWidgets.QWidget()

        rom_frame_1 = QFrame(self.main_frame1)
        rom_frame_1.setGeometry(0, 0, 400, 400)
        rom_frame_1.setFrameShape(QFrame.Panel)
        rom_frame_1.setFrameShadow(QFrame.Raised)

        # 第二个布局界面
        self.main_frame2 = QtWidgets.QWidget()

        rom_frame_2 = QFrame(self.main_frame2)
        rom_frame_2.setGeometry(0, 0, 400, 400)
        rom_frame_2.setFrameShape(QFrame.Panel)
        rom_frame_2.setFrameShadow(QFrame.Raised)

        # 第3个布局界面
        self.main_frame3 = QtWidgets.QWidget()

        rom_frame_3 = QFrame(self.main_frame3)
        rom_frame_3.setGeometry(0, 0, 400, 400)
        rom_frame_3.setFrameShape(QFrame.Panel)
        rom_frame_3.setFrameShadow(QFrame.Raised)

        # 第4个布局界面
        self.main_frame4 = QtWidgets.QWidget()

        rom_frame_4 = QFrame(self.main_frame4)
        rom_frame_4.setGeometry(0, 0, 400, 400)
        rom_frame_4.setFrameShape(QFrame.Panel)
        rom_frame_4.setFrameShadow(QFrame.Raised)

        # 把两个布局界面放进去
        self.stacked_layout.addWidget(self.main_frame1)
        self.stacked_layout.addWidget(self.main_frame2)
        self.stacked_layout.addWidget(self.main_frame3)
        self.stacked_layout.addWidget(self.main_frame4)

        # 页面1的按钮
        user_1 = QtWidgets.QPushButton(rom_frame_1)
        user_1.setGeometry(QtCore.QRect(0, 0, 90, 90))
        user_1.setMinimumSize(QtCore.QSize(90, 90))
        user_1.setMaximumSize(QtCore.QSize(90, 90))
        user_1.setCheckable(True)
        user_1.setStyleSheet("background-color:rgb(245, 245, 245);")
        user_1.setObjectName("top_1")
        user_1.setText("User 001")

        user_2 = QtWidgets.QPushButton(rom_frame_2)
        user_2.setGeometry(QtCore.QRect(0, 0, 90, 90))
        user_2.setMinimumSize(QtCore.QSize(90, 90))
        user_2.setMaximumSize(QtCore.QSize(90, 90))
        user_2.setCheckable(True)
        user_2.setStyleSheet("background-color:rgb(245, 245, 245);")
        user_2.setObjectName("top_2")
        user_2.setText("User 002")

    def phone_book_change_init(self, main_form):
        self.frame_tool = QFrame(main_form)
        self.frame_tool.setObjectName("frame_tool")
        self.frame_tool.setGeometry(QtCore.QRect(600, 545, 400, 80))
        self.frame_tool.setStyleSheet("border-color:rgb(196, 255, 216);")
        self.frame_tool.setFrameShape(QFrame.Panel)
        self.frame_tool.setFrameShadow(QFrame.Raised)

        self.window1_btn = QToolButton(self.frame_tool)
        self.window1_btn.setStyleSheet(
            "background-color:rgb(196, 255, 216);")
        # self.window1_btn.setStyleSheet(
        #     "background-color:rgb(196, 255, 216);border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
        self.window1_btn.setCheckable(True)
        self.window1_btn.setText("电话簿1")
        self.window1_btn.setObjectName("menu_btn")
        self.window1_btn.resize(100, 80)
        self.window1_btn.clicked.connect(self.phone_book_click_1)
        self.window1_btn.setAutoRaise(True)
        self.window1_btn.setChecked(True)

        self.window2_btn = QToolButton(self.frame_tool)
        self.window2_btn.setStyleSheet(
            "background-color:rgb(196, 255, 216);")
        # self.window2_btn.setStyleSheet(
        #     "background-color:rgb(196, 255, 216);border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
        self.window2_btn.setCheckable(True)
        self.window2_btn.setText("电话簿2")
        self.window2_btn.setObjectName("menu_btn")
        self.window2_btn.resize(100, 80)
        self.window2_btn.move(100, 0)
        self.window2_btn.clicked.connect(self.phone_book_click_2)
        self.window2_btn.setAutoRaise(True)

        self.window3_btn = QToolButton(self.frame_tool)
        self.window3_btn.setStyleSheet(
            "background-color:rgb(196, 255, 216);")
        # self.window3_btn.setStyleSheet(
        #     "background-color:rgb(196, 255, 216);border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
        self.window3_btn.setCheckable(True)
        self.window3_btn.setText("电话簿3")
        self.window3_btn.setObjectName("menu_btn")
        self.window3_btn.resize(100, 80)
        self.window3_btn.move(200, 0)
        self.window3_btn.clicked.connect(self.phone_book_click_3)
        self.window3_btn.setAutoRaise(True)

        self.window4_btn = QToolButton(self.frame_tool)
        self.window4_btn.setStyleSheet(
            "background-color:rgb(196, 255, 216);")
        # self.window4_btn.setStyleSheet(
        #     "background-color:rgb(196, 255, 216);border-bottom-right-radius:15px;border-bottom-left-radius:15px;")
        self.window4_btn.setCheckable(True)
        self.window4_btn.setText("电话簿4")
        self.window4_btn.setObjectName("menu_btn")
        self.window4_btn.resize(100, 80)
        self.window4_btn.move(300, 0)
        self.window4_btn.clicked.connect(self.phone_book_click_4)
        self.window4_btn.setAutoRaise(True)

        self.btn_group = QButtonGroup(self.frame_tool)
        self.btn_group.addButton(self.window1_btn, 1)
        self.btn_group.addButton(self.window2_btn, 2)
        self.btn_group.addButton(self.window3_btn, 3)
        self.btn_group.addButton(self.window4_btn, 4)

    def show_message(self):
        QMessageBox.information(self, "标题", "更多功能正在开发中",
                                QMessageBox.Yes)

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
        if not checked and channel_id in self.client.user["listening_channels"]:
            rx_button.setStyleSheet("background-color:rgb(245, 245, 245);")
            self.client.del_listening_channel(channel_id)
            # 取消
            tx_button = self.channel_push_buttons["channel_frame_{}".format(channel_id)][2]
            tx_checked = tx_button.isChecked()
            if tx_checked:
                if self.client.CurChannel is not None and self.client.CurChannel == channel_id:
                    ret = self.cancel_occupy_channel(channel_id)
                    if ret is True:
                        self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setChecked(False)
                    else:
                        self.client.CurChannel = channel_id
                        logging.error("取消占用channel {} err: {}".format(channel_id, ret))
                        self.show_error_message("通道{}释放失败".format(channel_id))

        if checked and channel_id not in self.client.user["listening_channels"]:
            rx_button.setStyleSheet("background-color:rgb(255, 255, 0);")
            self.client.add_listening_channel(channel_id)

    # 通道的tx按钮点击时间
    def channel_tx_click_handle(self):
        tx_button = self.sender()
        checked = tx_button.isChecked()
        channel_id = tx_button.objectName()
        if checked:
            # 开始占用通道 channel_id
            # 检测当前是否占用其他某个信道
            cur_channel = self.client.CurChannel
            if self.client.CurChannel is not None:
                ret = self.cancel_occupy_channel(cur_channel)
                if ret is True:
                    self.channel_push_buttons["channel_frame_{}".format(cur_channel)][2].setStyleSheet("background-color:rgb(245, 245, 245);")
                    self.channel_push_buttons["channel_frame_{}".format(cur_channel)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败
                    tx_button.setStyleSheet("background-color:rgb(255, 255, 0);")
                    self.client.CurChannel = cur_channel
                    tx_button.setChecked(False)
                    logging.error("释放channel {} err: {}".format(cur_channel, ret))
                    self.show_error_message("通道{}释放失败".format(cur_channel))

            # 去占用
            ret = self.client.choose_channel(channel_id)
            if ret is True:
                self.client.start_send_to_channel()
                # 监听当前通道
                rx_button = self.channel_push_buttons["channel_frame_{}".format(channel_id)][1]
                checked = rx_button.isChecked()
                if channel_id not in self.client.user["listening_channels"]:
                    self.client.add_listening_channel(channel_id)
                if not checked:
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][1].setChecked(True)
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][1].setStyleSheet("background-color:rgb(255, 255, 0);")
            else:
                tx_button.setChecked(False)
                logging.error("choose_channel err: {}".format(ret))
                self.show_error_message("通道{}占用失败".format(channel_id))
        else:
            # 取消占用通道 channel_id
            if self.client.CurChannel is not None:
                ret = self.cancel_occupy_channel(channel_id)
                if ret is True:
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setStyleSheet("background-color:rgb(245, 245, 245);")
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败
                    tx_button.setStyleSheet("background-color:rgb(255, 255, 0);")
                    self.client.CurChannel = channel_id
                    tx_button.setChecked(True)
                    logging.error("取消占用channel {} err: {}".format(channel_id, ret))
                    self.show_error_message("通道{}释放失败".format(channel_id))

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

    def micro_phone_control(self):
        while self.client and not self.client.ExitFlag:
            print(" DTR:", self.client.ser.dtr, " CD:", self.client.ser.cd, " DSR:", self.client.ser.dsr, " CTS:",
                  self.client.ser.cts)
            # level 1
            if self.client.ser.cd:
                if len(self.client.devices["inputs"]) < 1:
                    # self.show_error_message("请插入输入设备1(CD)")
                    logging.info("请插入输入设备1(CD)")
                elif not self.client.input_device_flags[self.client.devices["inputs"][0]]:
                    self.client.start_record_voice_data(self.client.devices["inputs"][0])
            if not self.client.ser.cd and len(self.client.devices["inputs"]) >= 1 \
                    and self.client.input_device_flags[self.client.devices["inputs"][0]]:
                self.client.stop_record_voice_data(self.client.devices["inputs"][0])
            # level 2
            if self.client.ser.dsr:
                if len(self.client.devices["inputs"]) < 2:
                    # self.show_error_message("请插入输入设备2(DSR)")
                    logging.info("请插入输入设备2(DSR)")
                elif not self.client.input_device_flags[self.client.devices["inputs"][1]]:
                    self.client.start_record_voice_data(self.client.devices["inputs"][1])
            if not self.client.ser.dsr and len(self.client.devices["inputs"]) >= 2 \
                    and self.client.input_device_flags[self.client.devices["inputs"][1]]:
                self.client.stop_record_voice_data(self.client.devices["inputs"][1])
            # level 3
            if self.client.ser.cts:
                if len(self.client.devices["inputs"]) < 3:
                    # self.show_error_message("请插入输入设备3(CTS)")
                    logging.info("请插入输入设备3(CTS)")
                elif not self.client.input_device_flags[self.client.devices["inputs"][2]]:
                    self.client.start_record_voice_data(self.client.devices["inputs"][2])
            if not self.client.ser.cts and len(self.client.devices["inputs"]) >= 3 \
                    and self.client.input_device_flags[self.client.devices["inputs"][2]]:
                self.client.stop_record_voice_data(self.client.devices["inputs"][2])
            time.sleep(0.22)

    def animation(self, channel_id):
        channel_frame_name = "channel_frame_{}".format(channel_id)
        self.ani = QPropertyAnimation(self.channel_push_buttons[channel_frame_name][1], "color")
        self.ani.setDuration(1000)
        self.ani.setLoopCount(20)
        self.ani.setStartValue(QColor(245, 245, 245))
        self.ani.setEndValue(QColor(255, 255, 0))

    def phone_book_click_1(self):
        if self.stacked_layout.currentIndex() != 0:
            self.stacked_layout.setCurrentIndex(0)

    def phone_book_click_2(self):
        if self.stacked_layout.currentIndex() != 1:
            self.stacked_layout.setCurrentIndex(1)

    def phone_book_click_3(self):
        if self.stacked_layout.currentIndex() != 2:
            self.stacked_layout.setCurrentIndex(2)

    def phone_book_click_4(self):
        if self.stacked_layout.currentIndex() != 3:
            self.stacked_layout.setCurrentIndex(3)

    def somebody_speaking(self, channel_id):
        self.animation(channel_id)
        self.ani.start()

