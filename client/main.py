import logging
import sys

from PyQt5 import QtWidgets

import conf.conf
from ui.mainwindow import MainWindow

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    conf.conf.init()
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
