#!/usr/bin/env python3
__author__ = 'mac'

import argparse
import inspect
import os
import socket
import sys
import re
from os import path
import logging

logging.basicConfig(filename='ShowMixer.log', filemode='w', level=logging.DEBUG)

from time import sleep
from math import ceil

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET


import jack
import rtmidi
from rtmidi.midiutil import get_api_from_environment
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON


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
import configuration as cfg
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

# from MixerConf import MixerConf
# from MixerMap import MixerCharMap

import MixerMaker_ui
import StripEdit_ui

import styles

parser = argparse.ArgumentParser()


cfgdict = cfg.toDict()

class MixerMakerDlg(QtWidgets.QMainWindow, MixerMaker_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MixerMakerDlg, self).__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    # try:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    #ui = ChanStripDlg(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui = MixerMakerDlg()
    ui.show()
    # except KeyboardInterrupt:
    #     parser.exit('\nInterrupted by user')
    # # except (queue.Full):
    # #     # A timeout occured, i.e. there was an error in the callback
    # #     parser.exit(1)
    # except Exception as e:
    #     parser.exit(type(e).__name__ + ': ' + str(e))
    logging.info('Shutdown')
    sys.exit(app.exec_())