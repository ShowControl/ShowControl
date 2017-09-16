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
from ShowControl.utils.ShowControlConfig import LOG_DIR
# from ShowControl.utils.Show import Show
# from ShowControl.utils.ShowConf import ShowConf
# from ShowControl.utils.Cues import CueList
# from ShowControl.utils.Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields
# import ShowControl.utils.CommHandlers
#

from CueEngine.CueEngine import CueDlg
#import CueEngine.CueEngine_rsrc_rc
#import CueEngine.CueEngine_ui
# from CueEngine import CueEngine

def main():
    logging.info('Message from main')
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = CueDlg()
    ui.resize(900,800)
    ui.disptext()
    ui.setfirstcue(1)  # slaves should execute cue 0 as the initialization
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
	main()
