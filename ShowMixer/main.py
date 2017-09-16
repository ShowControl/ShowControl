#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess
import types
import argparse
from os import path
import socket
from time import sleep
from curses.ascii import isprint
import psutil
import rtmidi
from rtmidi.midiutil import get_api_from_environment
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON
import re
import logging

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush, QPalette, QPainter, QPen, QPixmap

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from ShowControl.utils import styles
# from ShowControl.utils.ShowControlConfig import configuration, CFG_DIR, CFG_PATH, LOG_DIR
# from ShowControl.utils.Show import Show
# from ShowControl.utils.ShowConf import ShowConf
# from ShowControl.utils.Cues import CueList
# from ShowControl.utils.Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields
# import ShowControl.utils.CommHandlers

#from ShowMixer import styles
from ShowMixer.ShowMixer import ChanStripMainWindow
from ShowMixer.ShowMixer import ShowMxr

def main():
    # logging.basicConfig(level=logging.INFO,
    #                     filename=LOG_DIR + '/ShowMixer.log', filemode='w',
    #                     format='%(name)s %(levelname)s %(message)s')
    logging.info('Begin')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    ui = ChanStripMainWindow()
    # ui.resize(chans*ui.ChanStrip_MinWidth,800)
    ui.addChanStrip()
    ui.resize(ui.max_slider_count * ui.ChanStrip_MinWidth, 800)
    ui.disptext()
    ui.initmutes()
    ui.initlevels()
    ui.setfirstcue()
    firstuuid = ui.getcurrentcueuuid()
    ui.set_scribble(firstuuid)
    ui.execute_cue_uuid(firstuuid)
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
	main()
