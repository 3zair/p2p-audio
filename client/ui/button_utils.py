import sys

from PyQt5.QtCore import pyqtProperty, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QToolButton


class QPushButtonWithColor(QPushButton):
    def __init__(self, parent=None):
        super(QPushButtonWithColor, self).__init__(parent)
        self._color = QColor()

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, col):
        self._color = col
        self.setStyleSheet('background-color: rgb({}, {}, {})'.format(col.red(), col.green(), col.blue()))


class QWidgetWithColor(QWidget):
    def __init__(self, parent=None):
        super(QWidgetWithColor, self).__init__(parent)
        self._color = QColor()

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, col):
        self._color = col
        self.setStyleSheet('background-color: rgb({}, {}, {})'.format(col.red(), col.green(), col.blue()))


class QToolButtonWithColor(QToolButton):
    def __init__(self, parent=None):
        super(QToolButtonWithColor, self).__init__(parent)
        self._color = QColor()

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, col):
        self._color = col
        self.setStyleSheet('background-color: rgb({}, {}, {})'.format(col.red(), col.green(), col.blue()))


class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.resize(600, 600)

        self.btn = QPushButtonWithColor(self)
        self.btn.setGeometry(0, 0, 100, 100)

        self.animation = QPropertyAnimation(self.btn, b'color')
        self.animation.setDuration(5000)
        self.animation.setStartValue(QColor(0, 0, 0))
        self.animation.setEndValue(QColor(255, 255, 255))
        self.animation.setLoopCount(-1)
        self.animation.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
