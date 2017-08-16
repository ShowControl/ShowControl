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

import xmltodict

logging.basicConfig(filename='ShowMixer.log', filemode='w', level=logging.DEBUG)

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET



currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/ShowControl/utils'
showmixerdir = os.path.dirname(currentdir) + '/ShowControl/ShowMixer'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
sys.path.insert(0,showmixerdir)

print(sys.path)

from Show import Show
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

from MixerConf import MixerConf
from MixerMap import MixerCharMap



#import styles

parser = argparse.ArgumentParser()


import MuteMap_ui
#from kled import KLed

class ShowMxr(Show):
    """
    The Show class contains the information and object that constitute a show
    """
    def __init__(self):
        '''
        Constructor
        '''
        super(ShowMxr, self).__init__(cfg.cfgdict)
        self.mixers = {}
        for mxrid in self.show_conf.equipment['mixers']:
            #print(mxrid)
            if self.show_conf.equipment['mixers'][mxrid]['IP_address']:
                mixeraddress = self.show_conf.equipment['mixers'][mxrid]['IP_address'] + ',' + self.show_conf.equipment['mixers'][mxrid]['port']
            else:
                mixeraddress = self.show_conf.equipment['mixers'][mxrid]['MIDI_address']
            self.mixers[mxrid] = MixerConf(path.abspath(path.join(CFG_DIR, cfg.cfgdict['configuration']['mixers']['folder'], cfg.cfgdict['configuration']['mixers']['file'])),
                                           self.show_conf.equipment['mixers'][mxrid]['mfr'],
                                           self.show_conf.equipment['mixers'][mxrid]['model'],
                                           mixeraddress)

        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mixermap'])

    def reload(self):
        self.mixers = {}
        for mxrid in self.show_conf.equipment['mixers']:
            #print(mxrid)
            mixeraddress = self.show_conf.equipment['mixers'][mxrid]['IP_address'] + ',' + self.show_conf.equipment['mixers'][mxrid]['port']
            self.mixers[mxrid] = MixerConf(path.abspath(path.join(CFG_DIR, cfg.cfgdict['configuration']['mixers']['folder'], cfg.cfgdict['configuration']['mixers']['file'])),
                                           self.show_conf.equipment['mixers'][mxrid]['mfr'],
                                           self.show_conf.equipment['mixers'][mxrid]['model'],
                                           mixeraddress)

        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['project']['mixermap'])


if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    cfg = configuration()
    The_Show = ShowMxr()
    The_Show.displayShow()
    # app = QtWidgets.QApplication(sys.argv)

    with open('/home/mac/Shows/Fiddler/Fiddler_cuesx.xml','r') as xml_source:
        xml_string = xml_source.read()
        parsed = xmltodict.parse(xml_string)

    cuesxml = xmltodict.unparse(parsed)
    testoutput = open('/home/mac/Shows/Fiddler/Test_cuesx.xml','w')
    testoutput.write(cuesxml)

    logging.info('Shutdown')
#    sys.exit(app.exec_())
