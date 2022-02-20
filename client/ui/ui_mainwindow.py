import logging
import time

from udpClient.client import ChatClient
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QSlider, QDialog
from PyQt5.QtCore import Qt
from .ui_subwindow import UiForm2


class UIForm(object):
    def __init__(self):
        self.channel_push_buttons = {}
        self.channel_frames = {}
        self.client = None
        self.users = None
        self.channels = None
        self.volume = 50

    # def setup_ui(self, main_form):
    #     # self.client = ChatClient(socket.gethostbyname(socket.gethostname()), 8002)
    #     self.client = ChatClient("192.168.1.112", 8002)

    def setup_ui(self, main_form):
        self.client = ChatClient("127.0.0.1", 8001)
        self.users = self.client.ClientsInfo
        self.channels = self.client.Channels
        print(self.client.user)

        main_form.setObjectName("main_form")
        main_form.resize(1024, 768)
        main_form.setMinimumSize(QtCore.QSize(1024, 768))
        main_form.setMaximumSize(QtCore.QSize(1024, 768))
        main_form.setStyleSheet("background-color:rgb(179, 179, 179);")

        main_form.setWindowTitle("Form")

        self.channel_frame_init(main_form)
        self.top_frame_init(main_form)
        self.bottom_frame_init(main_form)
        self.user_frame_init(main_form)
        self.value_change_frame_init(main_form)

        # self.retranslateUi(main_form)
        QtCore.QMetaObject.connectSlotsByName(main_form)

    def change_volume(self, value):
        self.volume = value

    def value_change_frame_init(self, main_form):
        value_change_frame = QtWidgets.QFrame(main_form)
        value_change_frame.setGeometry(QtCore.QRect(930, 10, 50, 120))
        value_change_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        value_change_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        value_change_frame.setObjectName("value_change_frame")

        self.volume_slider = QSlider(value_change_frame)
        self.volume_slider.setGeometry(QtCore.QRect(2, 2, 40, 100))
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.volume_slider.setMaximum(32767)
        self.volume_slider.setPageStep(1024)
        self.volume_slider.valueChanged.connect(self.change_volume)

    def btnClicked(self):
        form1 = QDialog()
        self.chile_Win = UiForm2()
        self.chile_Win.initUI(form1)
        form1.setWindowModality(Qt.NonModal)
        self.chile_Win.show()
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
            self.channel_push_buttons[channel_frame_name][0].setText("通道_{}".format(channel_id))
            self.channel_push_buttons[channel_frame_name][0].clicked.connect(self.btnClicked)

            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][1].setGeometry(QtCore.QRect(110, 0, 80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][1].setStyleSheet("background-color:rgb(245, 245, 245);")
            self.channel_push_buttons[channel_frame_name][1].setCheckable(True)
            self.channel_push_buttons[channel_frame_name][1].setObjectName(channel_id)
            self.channel_push_buttons[channel_frame_name][1].setText("RX")
            self.channel_push_buttons[channel_frame_name][1].clicked.connect(self.channel_rx_click_handle)

            self.channel_push_buttons[channel_frame_name].append(
                QtWidgets.QPushButton(self.channel_frames[channel_frame_name]))
            self.channel_push_buttons[channel_frame_name][2].setGeometry(QtCore.QRect(110, 60, 80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMinimumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setMaximumSize(QtCore.QSize(80, 60))
            self.channel_push_buttons[channel_frame_name][2].setStyleSheet("background-color:rgb(245, 245, 245);")
            self.channel_push_buttons[channel_frame_name][2].setCheckable(True)
            self.channel_push_buttons[channel_frame_name][2].setObjectName(channel_id)
            self.channel_push_buttons[channel_frame_name][2].setText("TX")
            self.channel_push_buttons[channel_frame_name][2].clicked.connect(self.channel_tx_click_handle)

            print(channel_id, self.channels[channel_id])

    def top_frame_init(self, main_form):
        # top frame
        top_frame = QtWidgets.QFrame(main_form)
        # top_frame.setGeometry(QtCore.QRect(20, 40, 980, 95))
        top_frame.setGeometry(QtCore.QRect(20, 40, 900, 95))
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

        top_2 = QtWidgets.QPushButton(top_frame)
        top_2.setGeometry(QtCore.QRect(98, 0, 98, 95))
        top_2.setMinimumSize(QtCore.QSize(98, 95))
        top_2.setMaximumSize(QtCore.QSize(98, 95))
        top_2.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_2.setObjectName("top_2")
        top_2.setText("扬声通话")

        top_3 = QtWidgets.QPushButton(top_frame)
        top_3.setGeometry(QtCore.QRect(196, 0, 98, 95))
        top_3.setMinimumSize(QtCore.QSize(98, 95))
        top_3.setMaximumSize(QtCore.QSize(98, 95))
        top_3.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_3.setObjectName("top_3")
        top_3.setText("音量调节")
        top_3.clicked.connect(self.show_message)

        top_4 = QtWidgets.QPushButton(top_frame)
        top_4.setGeometry(QtCore.QRect(294, 0, 98, 95))
        top_4.setMinimumSize(QtCore.QSize(98, 95))
        top_4.setMaximumSize(QtCore.QSize(98, 95))
        top_4.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_4.setObjectName("top_4")
        top_4.setText("亮度调节")

        top_5 = QtWidgets.QPushButton(top_frame)
        top_5.setGeometry(QtCore.QRect(392, 0, 98, 95))
        top_5.setMinimumSize(QtCore.QSize(98, 95))
        top_5.setMaximumSize(QtCore.QSize(98, 95))
        top_5.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_5.setObjectName("top_5")
        top_5.setText("PTT电话")

        top_6 = QtWidgets.QPushButton(top_frame)
        top_6.setGeometry(QtCore.QRect(490, 0, 98, 95))
        top_6.setMinimumSize(QtCore.QSize(98, 95))
        top_6.setMaximumSize(QtCore.QSize(98, 95))
        top_6.setStyleSheet("background-color:rgb(111, 255, 248);")
        top_6.setObjectName("top_6")
        top_6.setText("通话日志")

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
        bottom_2.setText("切换输出设备")

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
        user_frame.setGeometry(QtCore.QRect(600, 145, 400, 480))
        user_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        user_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        user_frame.setObjectName("user_frame")

    def show_message(self):
        QMessageBox.information(self, "标题", "我很喜欢学习python",
                                QMessageBox.Yes)

    def show_error_message(self, err_msg):
        QMessageBox.critical(self, "错误", err_msg)

    def exit_click_handle(self):
        reply = QMessageBox.question(self, '警告', "系统将退出，是否确认?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QtCore.QCoreApplication.instance().quit()
            self.client.exit()
            del self.client

    def channel_rx_click_handle(self):
        rx_button = self.sender()
        checked = rx_button.isChecked()
        channel_id = rx_button.objectName()
        if not checked and channel_id in self.client.user["listening_channels"]:
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
            self.client.add_listening_channel(channel_id)

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
                    self.channel_push_buttons["channel_frame_{}".format(cur_channel)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败
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
            else:
                tx_button.setChecked(False)
                logging.error("choose_channel err: {}".format(ret))
                self.show_error_message("通道{}占用失败".format(channel_id))
        else:
            # 取消占用通道 channel_id
            if self.client.CurChannel is not None:
                ret = self.cancel_occupy_channel(channel_id)
                if ret is True:
                    self.channel_push_buttons["channel_frame_{}".format(channel_id)][2].setChecked(False)
                else:
                    # 当前占用的通道取消失败
                    self.client.CurChannel = channel_id
                    tx_button.setChecked(True)
                    logging.error("取消占用channel {} err: {}".format(channel_id, ret))
                    self.show_error_message("通道{}释放失败".format(channel_id))

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
        while True:
            print(" DTR:", self.client.ser.dtr, " CD:", self.client.ser.cd, " DSR:", self.client.ser.dsr, " CTS:",
                  self.client.ser.cts)
            # level 1
            if self.client.ser.cd:
                if len(self.client.devices["inputs"]) <= 1:
                    self.show_error_message("请插入输入设备1(CD)")
                else:
                    self.client.start_record_voice_data(self.client.devices["inputs"][0])

            # level 2
            if self.client.ser.dsr:
                if len(self.client.devices["inputs"]) <= 2:
                    self.show_error_message("请插入输入设备2(DSR)")
                else:
                    self.client.start_record_voice_data(self.client.devices["inputs"][1])

            # level 3
            if self.client.ser.cts:
                if len(self.client.devices["inputs"]) <= 3:
                    self.show_error_message("请插入输入设备3(CTS)")
                else:
                    self.client.start_record_voice_data(self.client.devices["inputs"][2])
            time.sleep(0.22)
