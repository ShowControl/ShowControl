import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import random
import styles
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def int_to_db( value ):
    if value >= 512:
        d = ((value/1024) * 40.0) - 30.0
    elif value >= 256:
        d = ((value/1024) * 80.0) - 50.0
    elif value >= 64:
        d = ((value/1024) * 160.0) - 70.0
    elif value > 0:
        d = ((value/1024) * 480.0) - 90.0
    elif value == 0:
        d = -90.0
    return d

def db_to_int( db ):
    db_f = float( db )
    if db < -60:
        value = (db + 90) / 480
    elif db < -30:
        value = (db + 70) / 160
    elif db < -10:
        value = (db + 50) / 80
    elif db <= 10:
        value = (db + 30) / 40
    return value * 1023

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'PyQt paint - pythonspot.com'
        self.screengeom = QtWidgets.QDesktopWidget().screenGeometry()
        self.left = self.screengeom.width()/ 2
        self.top = self.screengeom.height() / 2
        # self.width = 200
        # self.height = 280
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(850, 568)
        self.centralwidget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName("gridLayout")
        # self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider = MySlider(self.centralwidget)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setMinimumSize(50, 200)
        self.verticalSlider.setContentsMargins(10,0,10,0)
        self.gridLayout.addWidget(self.verticalSlider, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.setCentralWidget(self.centralwidget)

        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        # Add paint widget and paint
        # self.m = PaintWidget(self)
        # self.m.move(0, 0)
        # self.m.resize(850, 568)
        # # self.resize(850, 568)
        self.show()

class MySlider(QtWidgets.QSlider):
    def __init__(self, parent=None):
        super(MySlider, self).__init__(parent)

    def paintEvent(self, event):
        super(MySlider, self).paintEvent(event)
        qp = QPainter(self)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.black)

        qp.setPen(pen)
        font = QFont('Times', 10)
        font_y_offset = font.pointSize()/2
        qp.setFont(font)
        size = self.size()
        contents = self.contentsRect()
        db_val_list =   [10, 5, 0, -5, -10, -20, -30, -40, -50, -60, -90]
        for val in db_val_list:
            if val == 10:
                y_val_fudge = 12
            elif val == -90:
                y_val_fudge = -12
            db_scaled = db_to_int(val)
            y_val = contents.height() - translate(db_scaled, 0, 1023, 0, contents.height())
            if val == -90:
                qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge, '-oo')
            else:
                qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge,'{0:2}'.format(val))
            qp.drawLine(contents.x() + font.pointSize(), y_val + y_val_fudge,  contents.x() + contents.width(), y_val + y_val_fudge)

class PaintWidget(QWidget):
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(Qt.black)
        size = self.size()
        qp.drawLine(50,50,60,50)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)

    ex = App()
    sys.exit(app.exec_())