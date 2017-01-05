#!/usr/bin/env python3
'''

Created on Nov 16, 2014

@author: mac
'''

Fri Dec 23 11:18:25 EST 2016
This file is currently buggered. Started to move Show to a separate file and realized it
was creating a time rat hole, so put on hold.

import os, sys, inspect
import types
import argparse
import socket
from time import sleep

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pythonosc import osc_message_builder
from pythonosc import udp_client


import xml.etree.ElementTree as ET
from os import path

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)



from ShowConf import ShowConf
from MixerConf import MixerConf
from MixerMap import MixerCharMap
from Cues import CueList


import ui_ShowMixer
from ui_preferences import Ui_Preferences

import configuration as cfg

import styles

UDP_IP = "127.0.0.1"
UDP_PORT = 5005


cfgdict = cfg.toDict()
#print(cfgdict['Show']['folder'])


class Show:
    '''
    The Show class contains the information and object that constitute a show
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.show_confpath = cfgdict['Show']['folder'] + '/'
        self.show_conf = ShowConf(self.show_confpath + cfgdict['Show']['file'])
        self.mixer = MixerConf(path.abspath(path.join(path.dirname(__file__), '../ShowControl/', cfgdict['Mixer']['file'])),self.show_conf.settings['mxrmfr'],self.show_conf.settings['mxrmodel'])
        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'], self.mixer.input_count)
        self.cues.currentcueindex = 0
        self.cues.setcurrentcuestate(self.cues.currentcueindex)

    def loadNewShow(self, newpath):
        '''
            :param sho_configpath: path to new ShowConf.xml
            :return:
        '''
        print(cfgdict)
        self.show_confpath, showfile = path.split(newpath)
        #self.show_confpath = path.dirname(newpath)
        self.show_confpath = self.show_confpath + '/'
        cfgdict['Show']['folder'] = self.show_confpath
        cfgdict['Show']['file'] = showfile
        cfg.updateFromDict(cfgdict)
        cfg.write()
        self.show_conf = ShowConf(self.show_confpath + cfgdict['Show']['file'])
        self.mixer = MixerConf(path.abspath(path.join(path.dirname(__file__), '../ShowControl/', cfgdict['Mixer']['file'])),self.show_conf.settings['mxrmfr'],self.show_conf.settings['mxrmodel'])
        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'], self.mixer.input_count)
        self.cues.currentcueindex = 0
        self.cues.setcurrentcuestate(self.cues.currentcueindex)
        self.displayShow()

    def displayShow(self):
        '''
        Update the state of the mixer display to reflect the newly loaded show
        '''
        print(path.join(path.dirname(__file__)))
        print(path.abspath(path.join(path.dirname(__file__))) + '/')
        #print('Show Object:',The_Show)
        #print(The_Show.show_conf.settings['mxrmapfile'])
        insliders = self.mixer.inputsliders
        #print('Input Slider Count: ' + str(len(insliders)))
        for x in range(1, len(insliders)+1):
            sliderconf = insliders['Ch' + '{0:02}'.format(x)]
            #print('level: ' + str(sliderconf.level))
            #print('scribble: ' + sliderconf.scribble_text)
        outsliders = self.mixer.outputsliders
        #print('Output Slider Count: ' + str(len(outsliders)))
        for x in range(1, len(outsliders)+1):
            sliderconf = outsliders['Ch' + '{0:02}'.format(x)]
            #print('level: ' + str(sliderconf.level))
            #print('scribble: ' + sliderconf.scribble_text)

        #print(The_Show.cues)
        qs = self.cues.cuelist.findall('cue')
        for q in qs:
             print(q.attrib)

        #print(The_Show.chrchnmap)
        chs = self.chrchnmap.maplist.findall('input')
        # for ch in chs:
        #     print(ch.attrib)
