#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess
import types
import argparse
import socket
from time import sleep

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import xml.etree.ElementTree as ET
from os import path

_translate = QtCore.QCoreApplication.translate

from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)

#from ShowConf import ShowConf
#from Cues import CueList
#from MixerConf import MixerConf
from Show import Show
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header

import CueEngine_ui
from CueEdit_alt_ui import Ui_dlgEditCue

from pythonosc import osc_message_builder

import configuration as cfg

import styles

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

cfgdict = cfg.toDict()
The_Show = Show(cfgdict)
The_Show.displayShow()

if __name__ == "__main__":
    for i in range(The_Show.cues.cuecount):
        cuenum = '{0:03}'.format(i)
        cuetomod = The_Show.cues.cuelist.find("cue[@num='"+cuenum+"']")

        for ele_idx in range(1, cue_subelements.__len__()):
            try:
                subelement = cuetomod.find(cue_subelements[ele_idx].replace('_',''))
                if subelement == None:
                    print('Index: {0}: Missing: {1}'.format(i, cue_subelements[ele_idx]))
                    newele = ET.SubElement(cuetomod, cue_subelements[ele_idx].replace('_', ''))
            except:
                print('Index: {0} bad'.format(i))
    The_Show.cues.savecuelist(True, cfgdict['Show']['folder'] + The_Show.show_conf.settings['cuefile'])
    pass