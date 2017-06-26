#!/usr/bin/env python3
__author__ = 'mac'

import argparse
import inspect
import os
import time
import socket
import sys
import re
from os import path
import logging

logging.basicConfig(filename='ShowMaker.log', filemode='w', level=logging.DEBUG)

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
from pythonosc import osc_message
from pythonosc import osc_message_builder

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)


# import ShowControl/utils
from Show import Show
#import configuration as cfg
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

# from MixerConf import MixerConf
# from MixerMap import MixerCharMap

import ShowMaker_ui

parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
# args = parser.parse_args()
#

cfg = configuration()

class ShowMakerWin(QtWidgets.QMainWindow, ShowMaker_ui.Ui_MainWindow_showmaker):
    SMW_log = logging.getLogger(__name__)
    SMW_log.debug('ShowMakerWin')

    def __init__(self, parent=None):
        super(ShowMakerWin, self).__init__(parent)
        self.SMW_log.debug('in init')
        self.setupUi(self)
        self.action_Exit.triggered.connect(self.close)
        self.action_OpenShow.triggered.connect(self.newProjectFolder)

    def closeEvent(self, event):
        """..."""
        # if self.mixers_modified:
        #     reply = QMessageBox.question(self, 'Save Changes', 'Save changes to mixers?',
        #                                  QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        #                                  QMessageBox.Cancel)
        #     if reply == QMessageBox.Yes:
        #         self.mixers.savemixers(False, 'TestMixerSave.xml')
        #         self.mixers_modified = False
        #     elif reply == QMessageBox.No:
        #         pass
        #     elif reply == QMessageBox.Cancel:
        #         pass

        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


    def confirmQuit(self):
        """..."""
        reply = QMessageBox.question(self, 'Confirm Quit',
                                     "Are you sure you want to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)
        return reply

    def newProjectFolder(self):
        fileNames = []
        fdlg = QtWidgets.QFileDialog()
        # fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        fdlg.setFilter(QDir.Hidden | QDir.Dirs)
        if (fdlg.exec()):
            fileNames = fdlg.selectedFiles()
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fdlg.close()
        if len(fileNames) != 0:
            self.conffile = fileNames[0]
            self.actionLoadMixers.trigger()
        print('File>Open: {0}'.format(fileNames))

The_Show = Show(cfg.cfgdict)
# The_Show.displayShow()

if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    app = QtWidgets.QApplication(sys.argv)

    ui = ShowMakerWin()
    ui.show()
    sys.exit(app.exec_())