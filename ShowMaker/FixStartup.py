
#!/usr/bin/env python3
__author__ = 'mac'

import argparse
import inspect
import os
import time
import math
import socket
import sys
import re
from os import path
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

from ShowControl.utils.ShowControlConfig import configuration, CFG_DIR, CFG_PATH
from ShowControl.utils.Show import Show
from ShowControl.utils.Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields
from ShowControl.utils import styles
from ShowMixer.MixerConf import MixerConf
from ShowMixer.MixerMap import MixerCharMap

import ShowMaker_ui

parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
# args = parser.parse_args()
#

cfg = configuration()
module_logger.info('module log from ShowMaker.py')
The_Show = Show(cfg.cfgdict)

class toplevelthing(QWidget):
    def __init__(self, parent=None):
        super(toplevelthing, self).__init__(parent)
        logging.info('in toplevelthing.__init__')

if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    app = QtWidgets.QApplication(sys.argv)

    ui = toplevelthing()
    sys.exit(app.exec_())