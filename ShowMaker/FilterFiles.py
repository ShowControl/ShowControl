

import argparse
import inspect
import os
import shutil
import time
import math
import socket
import sys
import re
from os import path
import uuid
import logging
module_logger = logging.getLogger('ShowMaker_logger')

from time import sleep
from math import ceil

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class FileFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FileFilterProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, row, srcidx):
        print(row)
        #rowidx = self.createIndex(row, 0)
        #info = self.data(rowidx)
        #index = parent().model().index(row)
        return True

app = QtWidgets.QApplication(sys.argv)

proxymodel = FileFilterProxyModel()
dlg = QFileDialog()
dlg.setProxyModel(proxymodel)
dlg.setOption(QFileDialog.DontUseNativeDialog)
dlg.show()
app.exec_()