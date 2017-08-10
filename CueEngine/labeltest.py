import sys
import logging
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush, QPalette, QPainter, QPen, QPixmap
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import LEDTest_ui

# app = QApplication(sys.argv)
#
# label = QLabel()
# pixmap = QPixmap('/home/mac/SharedData/PycharmProjs/ShowControl/ShowMixer/DnChevron.png')
# label.setPixmap(pixmap)
# label.show()

class LED(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.state_brush = QBrush(Qt.red)
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(event.rect(), self.state_brush)
        painter.setPen(QPen(Qt.NoPen))
        painter.end()

    def toggle(self, state=False):
        if state == True:
            self.state_brush = QBrush(Qt.red)
        else:
            self.state_brush = QBrush(Qt.green)
        self.update()

class LEDmainWindow(QMainWindow, LEDTest_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.toggle)
        self.LED_state = True
        self.LEDLabel = LED()
        self.LEDLabel.setMaximumSize(QSize(20,20))
        self.gridLayout.addWidget(self.LEDLabel,1,1,1,1)

    def toggle(self):
        if self.LED_state == False:
            self.LED_state = True
        elif self.LED_state == True:
            self.LED_state = False
        self.LEDLabel.toggle(self.LED_state)
        print('In toggle LEDState: {}'.format(self.LED_state))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename='/home/mac/Shows/Fiddler/labeltest.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info('Begin')
    app = QtWidgets.QApplication(sys.argv)
    ui = LEDmainWindow()
    ui.show()
    logging.info('Shutdown')

    sys.exit(app.exec_())