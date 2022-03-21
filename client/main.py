import logging
import sys

from PyQt5 import QtWidgets

import conf.conf
from ui.mainwindow import MainWindow
from udp_client.client import ChatClient
from conf.conf import get_host, get_port
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    conf.conf.init()
    app = QtWidgets.QApplication(sys.argv)
    client = ChatClient(get_host(), get_port())
    mainWindow = MainWindow(client)
    mainWindow.show()
    client.start()

    sys.exit(app.exec_())
