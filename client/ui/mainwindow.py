from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from .ui_mainwindow import UIForm
from .ui_subwindow import UiForm2
from PyQt5.QtCore import Qt


class MainWindow(QtWidgets.QWidget, UIForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_ui(self)
        # for i in range(1, 9):
        #     temp_str = "channel_frame_{}".format(i)
        #     # 这样传过来就是空值
        #     self.channel_push_buttons[temp_str][1].clicked.connect(self.show_diaglog())
        self.show_diaglog()  # 直接在这里调用页面的话，虽然点击函数能出来窗口，但是我定义的subwindow的内容就不起作用

    def show_diaglog(self):
        form = QDialog()
        ui2 = UiForm2()
        ui2.initUI(form)
        form.setWindowModality(Qt.NonModal)  # 非模态，可与其他窗口交互
        # form.setWindowModality(Qt.WindowModal)  # 窗口模态，当前未处理完，阻止与父窗口交互
        # form.setWindowModality(Qt.ApplicationModal)  # 应用程序模态，阻止与任何其他窗口交互
        # form.show()
        # form.exec_()

    def on_world_clicked(self, remark):
        print(remark)
        self.Title.setText("Hello World")

    def on_china_clicked(self):
        self.Title.setText("Hello China")

    def online_edit_text_changed(self, p_str):
        self.Title.setText(p_str)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.ignore()
        self.exit_click_handle()
