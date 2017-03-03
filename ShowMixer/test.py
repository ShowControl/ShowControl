# class MyCode:
#     def mycode(self):
#         print('test text')
#     def othercode(self,aval):
#         print('other {}'.format(aval))
#
# x = MyCode()
# x.mycode()
# eval('x.{}'.format('mycode()'))
# eval('x.{}'.format('othercode()'))
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)

label = QLabel()
# pixmap = QPixmap(sys.argv[1])
pixmap = QPixmap('/home/mac/Desktop/flying-spaghetti-monster-256x256.png')
label.setPixmap(pixmap)
label.show()

sys.exit(app.exec_())