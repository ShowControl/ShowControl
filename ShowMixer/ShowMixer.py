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

from MixerConf import MixerConf
from MixerMap import MixerCharMap

import ui_ShowMixer
from ui_preferences import Ui_Preferences


import styles

parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
# args = parser.parse_args()
#

CUE_IP = "127.0.0.1"
CUE_PORT = 5005
MXR_IP = "192.168.53.40"
MXR_PORT = 10023


cfgdict = cfg.toDict()
#print(cfgdict['Show']['folder'])

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def int_to_db( value ):
    if value >= 512:
        d = ((value/1024) * 40.0) - 30.0
    elif value >= 256:
        d = ((value/1024) * 80.0) - 50.0
    elif value >= 64:
        d = ((value/1024) * 160.0) - 70.0
    elif value > 0:
        d = ((value/1024) * 480.0) - 90.0
    elif value == 0:
        d = -90.0
    return d

def db_to_int( db ):
    db_f = float( db )
    if db < -60:
        value = (db + 90) / 480
    elif db < -30:
        value = (db + 70) / 160
    elif db < -10:
        value = (db + 50) / 80
    elif db <= 10:
        value = (db + 30) / 40
    return value * 1023

class ShowPreferences(QDialog, Ui_Preferences):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # super(object, self).__init__(self)
        self.setupUi(self)

    def accept(self):
        x = self.cbxExitwCueEngine.checkState()
        print(x)
        if x == Qt.Checked:
            cfgdict['Prefs']['exitwithce'] = 'true'
        else:
            cfgdict['Prefs']['exitwithce'] = 'false'
        cfg.updateFromDict(cfgdict)
        cfg.write()
        super(ShowPreferences, self).accept()

    def reject(self):
        super(ShowPreferences, self).reject()

class ShowMxr(Show):
    """
    The Show class contains the information and object that constitute a show
    """
    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        super(ShowMxr, self).__init__(cfgdict)
        self.mixers = {}
        for mxrid in self.show_conf.settings['mixers']:
            #print(mxrid)
            self.mixers[mxrid] = MixerConf(path.abspath(path.join(path.dirname(__file__),
                                                                  '../ShowControl/', cfgdict['Mixer']['file'])),
                                           self.show_conf.settings['mixers'][mxrid]['mxrmfr'],
                                           self.show_conf.settings['mixers'][mxrid]['mxrmodel'],
                                           self.show_conf.settings['mixers'][mxrid]['address'])

        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])

class ChanStripDlg(QtWidgets.QMainWindow, ui_ShowMixer.Ui_MainWindow):
    CSD_log = logging.getLogger(__name__)
    CSD_log.debug('ChanStripDlg')
    ChanStrip_MinWidth = 50

    def __init__(self, cuelistfile, parent=None):
        super(ChanStripDlg, self).__init__(parent)
        self.CSD_log.debug('in init')
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        self.max_slider_count = 0
        self.tablist = []
        self.tablistvertlayout = []
        self.tabgridlayoutlist = []
        self.tabstripgridlist = []
        self.scrollArea = []
        self.scrollAreaWidgetContents = []
        # start with all cue types visible
        self.CueTypeVisible = {}
        for type in cue_types:
            self.CueTypeVisible[type] = True
        self.comm_threads = []  # a list of all threads in use for later use when app exits
        # Set up sender threads for each mixer
        self.mixer_sender_threads = []
        # Setup thread and udp to handle mixer I/O
        try:
            self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            #todo-mac need exception and logging here
            print('Failed to create mixer socket')
            sys.exit()
        for idx in The_Show.mixers:
            if The_Show.mixers[idx].protocol == 'osc':
                # Setup thread and udp to handle mixer I/O
                try:
                    senderthread = CommHandlers.sender(self.mxr_sock)  #, MXR_IP, MXR_PORT)
                    senderthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
                    senderthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
                    senderthread.start()  # start the thread
                    self.mixer_sender_threads.append(senderthread)
                    self.comm_threads.append(senderthread)
                except socket.error:
                    print('Failed to create mixer socket')  #todo-mac need exception and logging here
                    sys.exit()
            elif The_Show.mixers[idx].protocol == 'midi':  #todo-mac figure out to start jack server when it's not started yet.
                # Get midi input port (i.e. ports we can send to) list
                self.client = jack.Client("TempClient")
                self.portlist = self.client.get_ports(is_midi=True, is_physical=True)
                self.client.deactivate()
                self.client.close()
                self.client = None
                sleep(0.1)
                self.portlist.extend(self.getrtmidiports())
                self.selidx = 1  # temporarily hardwie to 0, it's my local jack client on my AF12
                if isinstance(self.portlist[self.selidx], str):
                    print('{} ALSA port selected'.format(self.selidx))
                    self.snd_sndrthread = CommHandlers.AMIDIsender()
                    partofname = self.portlist[self.selidx].split(':')
                    senderthread.setport([partofname[0], self.portlist[self.selidx]])
                    senderthread.amidi_sndrsignal.connect(
                        self.snd_sndrtestfunc)  # connect to custom signal called 'signal'
                    senderthread.finished.connect(
                        self.snd_sndrthreaddone)  # connect to buitlin signal 'finished'
                    senderthread.start()  # start the thread
                else:
                    print('{} JACK port selected'.format(self.selidx))
                    senderthread = CommHandlers.JMIDIsender('ShowMixer')
                    senderthread.setport(self.portlist[self.selidx].name)
                self.mixer_sender_threads.append(senderthread)
                self.comm_threads.append(senderthread)
            else:
                raise ValueError('Mixer ID:{0} Unknown or missing protocol.')

        # setup receiver thread
        self.mxr_rcvrthread = CommHandlers.receiver(self.mxr_sock, MXR_IP, MXR_PORT)
        self.mxr_rcvrthread.rcvrsignal.connect(self.rcvrtestfunc)  # connect to custom signal called 'signal'
        self.mxr_rcvrthread.finished.connect(self.rcvrthreaddone)  # conect to buitlin signal 'finished'
        self.mxr_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.mxr_rcvrthread)
        self.externalclose = False


        # temporary to test the connection
        # cmdchn = CONTROL_CHANGE + 0x02
        # print('cmdchn: {:02X}'.format(cmdchn))
        # for control in reversed(range(1, 13)):
        #     print('control number: {}'.format(control))
        #     self.mixer_sender_threads[1].queue_msg([0, cmdchn, control, 0x00], '')
        #     sleep(0.05)
        # sleep(.5)
        # for control in range(1, 13):
        #     print('control number: {}'.format(control))
        #     self.mixer_sender_threads[1].queue_msg([0, cmdchn, control, 0x40],'')
        #     sleep(0.05)
        # sleep(.5)
        # for control in reversed(range(1, 13)):
        #     print('control number: {}'.format(control))
        #     self.mixer_sender_threads[1].queue_msg([0, cmdchn, control, 0x00],'')
        #     sleep(0.05)

        #  Setup thread and udp to handle commands from CueEngine
        # setup command receiver socket
        try:
            self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create mixer socket')  #todo-mac need exception and logging here
            sys.exit()
        self.cmd_sock.bind((CUE_IP, CUE_PORT))
        # setup command receiver thread
        self.cmd_rcvrthread = CommHandlers.cmd_receiver(self.cmd_sock)
        self.cmd_rcvrthread.cmd_rcvrsignal.connect(self.cmd_rcvrtestfunc)  # connect to custom signal called 'signal'
        self.cmd_rcvrthread.finished.connect(self.cmd_rcvrthreaddone)  # connect to builtin signal 'finished'
        self.cmd_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.cmd_rcvrthread)

        self.setupUi(self)
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.tabWidget.setCurrentIndex(0)
        self.nextButton.clicked.connect(self.on_buttonNext_clicked)
        self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        self.savecueButton.clicked.connect(self.on_buttonSaveCue_clicked)
        self.tableView.clicked.connect(self.tableClicked)
        self.actionOpen_Show.triggered.connect(self.openShow)
        self.actionSave_Show.triggered.connect(self.saveShow)
        self.actionClose_Show.triggered.connect(self.closeShow)
        self.actionPreferences.triggered.connect(self.editpreferences)
        self.pref_dlg=ShowPreferences()

    def getrtmidiports(self):
        midiclass_ = rtmidi.MidiOut
        logging.debug("Creating %s object.", midiclass_.__name__)

        api = get_api_from_environment(rtmidi.API_UNSPECIFIED)

        midiobj = midiclass_(api, None)
        type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "output"

        ports = midiobj.get_ports()
        midiobj = None
        return ports


    def addChanStrip(self):
        # determine max sliders
        #print('Mixer count: {}'.format(The_Show.mixers.__len__()))
        # for mxrid in The_Show.mixers:
        #     if The_Show.mixers[mxrid].mxrconsole.__len__() > self.max_slider_count:
        #         self.max_slider_count = The_Show.mixers[mxrid].mxrconsole.__len__()
        self.max_slider_count = 32
        for idx in range(The_Show.mixers.__len__()):
            self.scroller = QtWidgets.QScrollArea()
            self.tablist.append(QtWidgets.QWidget())
            self.tablist[idx].setMinimumSize(QtCore.QSize(0, 400))
            self.tablist[idx].setObjectName("Pg {}".format(idx))
            # put a vertical layout on the tab
            self.tablistvertlayout.append(QtWidgets.QVBoxLayout(self.tablist[idx]))
            self.tablistvertlayout[idx].setContentsMargins(10, 10, 10, 10)
            self.tablistvertlayout[idx].setObjectName("verticalLayout")
            # set up a scrolling area on the tab
            self.scrollArea.append(QtWidgets.QScrollArea(self.tablist[idx]))  # add a scrollarea to the tab
            #self.scrollArea[idx].setGeometry(QtCore.QRect(19, 20, 981, 191))
            self.scrollArea[idx].setGeometry(QtCore.QRect(19, 20, 1200, 400))  # set overall size of the scroll area
            # self.scrollArea[idx].setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            # self.scrollArea[idx].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea[idx].setWidgetResizable(True)
            self.scrollArea[idx].setObjectName("scrollArea")
            self.scrollAreaWidgetContents.append(QtWidgets.QWidget())
            self.scrollAreaWidgetContents[idx].setGeometry(QtCore.QRect(0, 0, 1200, 800))  # set the size of the area under the scrol area
            self.scrollAreaWidgetContents[idx].setObjectName('scrollAreaWidgetContents_{}'.format(idx))
            # add a grid layout were the controls go
            self.tabgridlayoutlist.append(QtWidgets.QGridLayout(self.scrollAreaWidgetContents[idx]))
            self.tabgridlayoutlist[idx].setContentsMargins(10, 10, 10, 10)
            self.tabgridlayoutlist[idx].setObjectName("gridLayout{}".format(idx))
            self.tabstripgridlist.append(QtWidgets.QGridLayout())
            self.tabstripgridlist[idx].setObjectName("stripgridLayout{}".format(idx))
            self.tabgridlayoutlist[idx].addLayout(self.tabstripgridlist[idx], 0, 0, 1, 1)
            self.tabWidget.insertTab(idx, self.tablist[idx], "Tab {}".format(idx))
            for chn in range(The_Show.mixers[idx].mxrconsole.__len__()):
            #for chn in range(The_Show.mixers[idx].input_count):
                # Add scribble for each channel
                scrbl = QtWidgets.QLabel()
                #scrbl.setObjectName('scr{0:02}'.format(chn))
                scrbl.setObjectName('M{0}scr{1:02}'.format(idx,chn))
                # print(scrbl.objectName())
                scrbl.setText(The_Show.mixers[idx].mxrconsole[chn]['name'])
                #scrbl.setText('M{0} Scribble {1:02}'.format(idx,chn))
                scrbl.setAlignment(QtCore.Qt.AlignHCenter)
                scrbl.setMinimumWidth(self.ChanStrip_MinWidth)
                scrbl.setMinimumHeight(30)
                scrbl.setWordWrap(True)
                self.tabstripgridlist[idx].addWidget(scrbl,4,chn,1,1)
                # Add slider for this channel
                sldr = QtWidgets.QSlider(QtCore.Qt.Vertical)  # default sliders
                # sldr = MySlider()                           # slider with decibel ticks
                # sldr.valueChanged.connect(self.sliderprint)
                sldr.sliderMoved.connect(self.sliderprint)
                sldr.setObjectName('M{0}sldr{1:02}'.format(idx, chn))
                # print(sldr.objectName())
                sldr.setMinimumSize(self.ChanStrip_MinWidth,200)
                sldr.setRange(0,1024)
                # sldr.setTickPosition(3)
                # sldr.setTickInterval(10)
                sldr.setSingleStep(2)
                sldr.setContentsMargins(10, 0, 10, 0)
                self.tabstripgridlist[idx].addWidget(sldr, 3, chn, 1, 1)
                # Add label for this channel level
                lev = QtWidgets.QLabel()
                lev.setObjectName('M{0}lev{1:02}'.format(idx, chn))
                # print(lev.objectName())
                lev.setText('000')
                lev.setMinimumWidth(self.ChanStrip_MinWidth)
                lev.setAlignment(QtCore.Qt.AlignHCenter)
                self.tabstripgridlist[idx].addWidget(lev,2,chn, 1, 1)
                #Add mute button for this channel
                mute = QtWidgets.QPushButton()
                mute.setCheckable(True)
                mute.clicked.connect(self.on_buttonMute_clicked)
                mute.setObjectName('M{0}mute{1:02}'.format(idx, chn))
                # print('Created: {}'.format(mute.objectName()))
                mute.setMinimumWidth(self.ChanStrip_MinWidth)
                self.tabstripgridlist[idx].addWidget(mute, 1, chn, 1, 1)
                # Add label for this channel
                lbl = QtWidgets.QLabel()
                lbl.setObjectName('M{0}lbl{1:02}'.format(idx, chn))
                lbl.setText(The_Show.mixers[idx].mxrconsole[chn]['name'])
                lbl.setMinimumWidth(self.ChanStrip_MinWidth)
                self.tabstripgridlist[idx].addWidget(lbl, 0, chn, 1, 1)
            self.scrollArea[idx].setWidget(self.scrollAreaWidgetContents[idx])
            self.tablistvertlayout[idx].addWidget(self.scrollArea[idx])

    def sliderprint(self, val):
        sending_slider = self.sender()
        #print('sending_slider name: {0}'.format(sending_slider.objectName()))
        sldrname = sending_slider.objectName()
        mxrid = int(sldrname[1])
        stripGUIindx = int(sldrname[-2:len(sldrname)])
        scrLblname = sldrname.replace('sldr', 'lev')
        scrLbl = self.findChild(QtWidgets.QLabel, name=scrLblname)
        val_db = int_to_db(val)
        scrLbl.setText('{0:>.2f}'.format(val_db))
        msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
            mxrconsole[stripGUIindx]['type']]['fader']. \
            Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], val)
        if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def on_buttonNext_clicked(self):
        self.next_cue()

    def on_buttonJump_clicked(self):
        self.execute_cue(The_Show.cues.selectedcueindex)

    def on_buttonSaveCue_clicked(self):
        print('Save Cue clicked!')
        levels = ''
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                sldr = self.findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
                levels += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'], sldr.value())
                # print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
        print(levels)
        The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels)
        # thiscue = The_Show.cues.cuelist.find("./cue[@num='" + '{0:03}'.format(The_Show.cues.currentcueindex) + "']")
        # newcuetype = thiscue.find('Exits')
        # print(newcuetype.text)
        The_Show.cues.addnewcue()

    def execute_cue(self, num):
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
        The_Show.cues.currentcueindex = num
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)

        mute_changes = The_Show.cues.get_cue_mute_state(The_Show.cues.currentcueindex)
        # iterate through mute changes, if any
        if mute_changes != None:
            for key, value in mute_changes.items():
                # find the channel name in the mxrconsole list
                # that should be the stripGUIindex
                #get name from key
                nbrs = re.findall(r'\d+',key)  # old way to striGUIindex
                mxrid = int(nbrs[0])
                chname = key[re.search('\d', key).end():]
                for cons_idx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                    if The_Show.mixers[mxrid].mxrconsole[cons_idx]['name'].lower() == chname.lower():
                        # print('found in stp {0}'.format(cons_idx))
                        stripGUIindx = cons_idx
                        break
                # stripGUIindx = int(nbrs[1]) - 1
                mute = self.findChild(QtWidgets.QPushButton, name='M{0}mute{1:02}'.format(mxrid, stripGUIindx))
                if value == 1:  # 1 >> unmute  0 >> mute
                    # Handle unmute
                    if The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
                        mute.setChecked(False)  # for illuminated = unmuted
                    else:
                        mute.setChecked(True)  # for a dark = umuted
                    muteval = The_Show.mixers[mxrid].mutestyle['unmute']
                else:
                    # Handle mute
                    if The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
                        mute.setChecked(True)
                    else:
                        mute.setChecked(False)
                    muteval = The_Show.mixers[mxrid].mutestyle['mute']
                msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                    mxrconsole[stripGUIindx]['type']]['mute']. \
                    Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], muteval)
                if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
                pass

        levels = The_Show.cues.get_cue_levels(The_Show.cues.currentcueindex)
        if levels != None:
            for key, value in levels.items():
                # find the channel name in the mxrconsole list
                # that should be the stripGUIindex
                #get name from key
                nbrs = re.findall(r'\d+',key)
                mxrid = int(nbrs[0])
                chname = key[re.search('\d', key).end():]
                for cons_idx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                    if The_Show.mixers[mxrid].mxrconsole[cons_idx]['name'].lower() == chname.lower():
                        # print('found in stp {0}'.format(cons_idx))
                        stripGUIindx = cons_idx
                        break

                ####
                # stripGUIindx = int(nbrs[1]) - 1
                sldr = self.findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
                scrLbl = self.findChild(QtWidgets.QLabel, name='M{0}lev{1:02}'.format(mxrid, stripGUIindx))
                val_db = int_to_db(int(value))
                scrLbl.setText('{0:>.2f}'.format(val_db))
                if sldr.sliderPosition() != value:
                    msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                        mxrconsole[stripGUIindx]['type']]['fader']. \
                        Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], int(value))
                    sldr.setSliderPosition(int(value))
                    if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
                pass

    def next_cue(self):
        nextmxrcuefound = False
        index = The_Show.cues.currentcueindex
        while not nextmxrcuefound:
            index += 1
            if index < The_Show.cues.cuecount:
                if 'Mixer' in The_Show.cues.getcuetype(index):
                    nextmxrcuefound = True
                    self.execute_cue(index)
            else:
                return

    def initmutes(self):
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                    mxrconsole[stripGUIindx]['type']]['mute'].\
                    Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], The_Show.mixers[mxrid].mutestyle['mute'])
                if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
                mute = self.findChild(QtWidgets.QPushButton, name='M{0}mute{1:02}'.format(mxrid, stripGUIindx))
                if The_Show.mixers[mxrid].mutestyle['mutestyle']== 'illuminated':
                    mute.setChecked(True)
                else:
                    mute.setChecked(False)

    def initlevels(self):
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                    mxrconsole[stripGUIindx]['type']]['fader'].\
                    Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], 0)
                if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def on_buttonMute_clicked(self):
        mbtn=self.sender()
        print('sending_slider name: {0}'.format(mbtn.objectName()))
        mbtnname = mbtn.objectName()
        mxrid = int(mbtnname[1])
        stripGUIindx = int(mbtnname[-2:len(mbtnname)])
        # print(mbtn.objectName())
        chkd = mbtn.isChecked()
        dwn=mbtn.isDown()
        if mbtn.isChecked() and The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
            muteval = The_Show.mixers[mxrid].mutestyle['mute']
        elif mbtn.isChecked() and The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'dark':
            muteval = The_Show.mixers[mxrid].mutestyle['unmute']
        elif not mbtn.isChecked() and The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
            muteval = The_Show.mixers[mxrid].mutestyle['unmute']
        elif not mbtn.isChecked() and The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'dark':
            muteval = The_Show.mixers[mxrid].mutestyle['mute']

        msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
            mxrconsole[stripGUIindx]['type']]['mute']. \
            Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], muteval)
        # todo-mac why does this go to main > sys.exit(app.exec_())?
        if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def setfirstcue(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
        self.execute_cue(The_Show.cues.currentcueindex)

    def openShow(self):
        '''
        Present file dialog to select new ShowConf.xml file
        :return:
        '''
        fdlg = QtWidgets.QFileDialog()
        fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fdlg.close()

        # print(fname[0])
        The_Show.loadNewShow(fname[0])
        self.set_scribble(The_Show.chrchnmap.maplist)
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.initmutes()
        self.initlevels()
        self.disptext()
        self.setfirstcue()

    def saveShow(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        # print(fname)

    def closeShow(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        print(fname)

    def editpreferences(self):
        if cfgdict['Prefs']['exitwithce'] == 'true':
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Checked)
        else:
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Unchecked)
        self.pref_dlg.show()
        #self.itb = QDialog()
        #self.ui_prefdlg = Ui_Preferences()
        #self.ui_prefdlg.setupUi(self.itb)
        #self.itb.show()

    def set_scribble(self, mxrmap):
        charcount = int(mxrmap.getroot().attrib['charcount'])

        chars = mxrmap.findall('input')
        for char in chars:
            cnum = int(char.attrib['chan'])
            mxrid = int(char.attrib['mixerid'])
            msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                mxrconsole[cnum - 1]['type']]['scribble'].\
                Set(cnum, char.attrib['actor'])
            if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
            # print('M{0}scr{1:02}'.format(mxrid,cnum))
            thislbl = self.findChild(QtWidgets.QLabel, name='M{0}scr{1:02}'.format(mxrid,cnum-1))
            thislbl.setText(char.attrib['actor'][:5])

            pass

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        #self.tableView.connect(self.tableClicked, QtCore.SIGNAL("clicked()"))

    def get_table_data(self):
        qs = The_Show.cues.cuelist.findall('cue')
        self.tabledata =[]
        for q in qs:
            type_list = q.find('CueType').text.split(',')
            for type in cue_types:
                 if type in type_list and self.CueTypeVisible[type]:
                     self.append_table_data(q)
                     break

            # self.tabledata.append([q.find('Move').text,
            #          q.find('Id').text,
            #          q.find('Scene').text,
            #          q.find('Page').text,
            #          q.find('Title').text,
            #          q.find('Cue').text])

    def append_table_data(self, q):
        tmp_list = ['{0:03}'.format(int(q.attrib['num']))]
        for i in range(1, header.__len__()):
            tmp_list.append(q.find(header[i].replace(' ','')).text)
        self.tabledata.append(tmp_list)

    def tableClicked(self, modelidx):
        rowidx = modelidx.row()
        The_Show.cues.selectedcueindex = rowidx
        self.tableView.selectRow(The_Show.cues.selectedcueindex)
        # print('table clicked, row{}'.format(rowidx))

    def closeEvent(self, event):
        """..."""
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            self.stopthreads()
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        """..."""
        if self.externalclose:
            reply =  QMessageBox.Yes
        else:
            reply = QMessageBox.question(self, 'Confirm Quit',
                "Are you sure you want to quit?", QMessageBox.Yes |
                QMessageBox.No, QMessageBox.No)
        return reply

    '''sender functions'''
    '''testfucn
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def sndrtestfunc(self, sigstr):
        """..."""
        # print(sigstr)
        self.statusBar().showMessage(sigstr)

    def cmd_rcvrtestfunc(self, sigstr):
        """..."""
        msg = osc_message.OscMessage(sigstr)
        # print(msg.address)
        for param in msg.params:
            print(param)
        if msg.address == '/cue':
            if msg.params[0] == "NEXT":
                self.next_cue()
        elif msg.address == '/cue/#':
            self.execute_cue(msg.params[0])
        elif msg.address == '/cue/quit':
            self.externalclose = True
            self.close()

    def sndrqput(self, msg):
        """..."""
        self.sndrthread.queue_msg(msg)

    '''receiver functions
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def rcvrtestfunc(self, sigstr):
        """..."""
        # print(sigstr)
        self.statusBar().showMessage(sigstr)

    '''gets called by main to tell the thread to stop'''
    def stopthreads(self):
        """..."""
        for t in self.comm_threads:
            t.setstopflag()
            t.wait(500)

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def sndrthreaddone(self):
        """..."""
        print('sender thread done')

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def rcvrthreaddone(self):
        """..."""
        print('receiver thread done')

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def cmd_rcvrthreaddone(self):
        """..."""
        print('command receiver thread done')

class MySlider(QtWidgets.QSlider):
    def __init__(self, parent=None):
        super(MySlider, self).__init__(parent)

    def paintEvent(self, event):
        super(MySlider, self).paintEvent(event)
        qp = QPainter(self)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.black)

        qp.setPen(pen)
        font = QFont('Times', 10)
        font_y_offset = font.pointSize()/2
        qp.setFont(font)
        size = self.size()
        contents = self.contentsRect()
        db_val_list =   [10, 5, 0, -5, -10, -20, -30, -40, -50, -60, -90]
        for val in db_val_list:
            if val == 10:
                y_val_fudge = 12
            elif val == -90:
                y_val_fudge = -12
            db_scaled = db_to_int(val)
            y_val = contents.height() - translate(db_scaled, 0, 1023, 0, contents.height())
            if val == -90:
                qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge, '-oo')
            else:
                qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge,'{0:2}'.format(val))
            qp.drawLine(contents.x() + font.pointSize(), y_val + y_val_fudge,  contents.x() + contents.width(), y_val + y_val_fudge)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if len(self.arraydata) > 0: 
            return len(self.arraydata[0]) 
        return 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.BackgroundColorRole:
            #print (self.arraydata[index.row()][7])
            if self.arraydata[index.row()][7] == 'Stage':
                return QBrush(Qt.blue)
            elif self.arraydata[index.row()][7] == 'Sound':
                return QBrush(Qt.yellow)
            elif self.arraydata[index.row()][7] == 'Light':
                return QBrush(Qt.darkGreen)
            elif self.arraydata[index.row()][7] == 'Mixer':
                return QBrush(Qt.darkYellow)
            else:
                return QBrush(Qt.darkMagenta)

        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def setData(self, index, value, role):
        pass         # not sure what to put here

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

The_Show = ShowMxr(cfgdict)
The_Show.displayShow()

if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    # try:
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    #ui = ChanStripDlg(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui = ChanStripDlg(path.abspath(path.join(path.dirname(cfgdict['Show']['folder']))))
    #ui.resize(chans*ui.ChanStrip_MinWidth,800)
    ui.addChanStrip()
    ui.resize(ui.max_slider_count * ui.ChanStrip_MinWidth, 800)
    ui.disptext()
    ui.set_scribble(The_Show.chrchnmap.maplist)
    ui.initmutes()
    ui.initlevels()
    ui.setfirstcue()
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