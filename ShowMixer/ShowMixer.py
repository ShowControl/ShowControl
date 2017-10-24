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

from ShowControl.utils import styles
# import ShowControl/utils
# from SCLog import SCLog
from Show import Show
#import configuration as cfg
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH, LOG_DIR
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

from ShowMixer.MixerConf import MixerConf
from ShowMixer.MixerMap import MixerCharMap

from ShowMixer.ui_ShowMixer import Ui_MainWindow
from ShowMixer.ui_preferences import Ui_Preferences


from ShowMixer import ShowMixer_rsrc_rc
cfg = configuration()

parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
# args = parser.parse_args()
#

class CommAddresses:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT

class LED(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.state_brush = QBrush(Qt.green)
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(event.rect(), self.state_brush)
        painter.setPen(QPen(Qt.NoPen))
        painter.end()

    def toggle(self, state=False):
        if state == True:
            self.state_brush = QBrush(Qt.red)
        else:
            self.state_brush = QBrush(Qt.green)
        self.update()



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
    return int(d)  # return int so the db value steps in increments of 1db

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
    return int(value * 1024)

cfg = configuration()


class ShowPreferences(QDialog, Ui_Preferences):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # super(object, self).__init__(self)
        self.setupUi(self)

    def accept(self):
        #todo - mac needs work in ShowControlConfig.py to handle xml structure correctly.
        x = self.cbxExitwCueEngine.checkState()
        print(x)
        if x == Qt.Checked:
            cfg.cfgdict['prefs']['exitwithce'] = 'true'
        else:
            cfg.cfgdict['prefs']['exitwithce'] = 'false'
        cfg.updateFromDict(cfg.cfgdict)
        cfg.write()
        super(ShowPreferences, self).accept()

    def reject(self):
        super(ShowPreferences, self).reject()

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

The_Show = ShowMxr()
The_Show.displayShow()


class ChanStripMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    #CSD_log = logging.getLogger(__name__)
    #CSD_log.debug('ChanStripMainWindow')
    ChanStrip_MinWidth = 50
    CueFileUpdate_sig = pyqtSignal(int)

    def __init__(self, parent=None):
        super(ChanStripMainWindow, self).__init__(parent)
        logging.info('In ChanStripMainWindow init.')
        #self.logger.info('In ChanStripMainWindow init.')
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)

        self.ShowMixerAppDev = CommAddresses(The_Show.show_conf.equipment['program']['ShowMixer']['IP_address'],
                                       int(The_Show.show_conf.equipment['program']['ShowMixer']['port']))
        logging.info('ShowMixer receives commands from IP: {} PORT: {}'.format(self.ShowMixerAppDev.IP,
                                                                               self.ShowMixerAppDev.PORT))

        self.CueAppDev = CommAddresses(The_Show.show_conf.equipment['program']['CueEngine']['IP_address'],
                                      int(The_Show.show_conf.equipment['program']['CueEngine']['port']))
        logging.info('CueEngine response will be sent to IP: {} PORT: {}'.format(self.CueAppDev.IP, self.CueAppDev.PORT))

        self.__index = 0
        self.cuehaschanged = False
        self.ExternalEditStarted = False
        self.ExternalEditComplete = False
        self.last_mixermap = 0
        self.ctrl_s = QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_S), self)
        self.ctrl_s.activated.connect(self.saveShow)
        self.CueFileUpdate_sig.connect(self.ExternalCueUpdate)
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
        self.mixer_sender_threads = []
        self.startdevicethreads()
        # # Set up sender threads for each mixer
        # self.mixer_sender_threads = []
        # # Setup thread and udp to handle mixer I/O
        # try:
        #     self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # except socket.error:
        #     #todo-mac need exception and logging here
        #     print('Failed to create mixer socket')
        #     sys.exit()
        # for idx in The_Show.mixers:
        #     if The_Show.mixers[idx].protocol == 'osc':
        #         # Setup thread and udp to handle mixer I/O
        #         try:
        #             senderthread = CommHandlers.sender(self.mxr_sock)  #, MXR_IP, MXR_PORT)
        #             senderthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
        #             senderthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
        #             senderthread.start()  # start the thread
        #             self.mixer_sender_threads.append(senderthread)
        #             #self.comm_threads.append(senderthread)
        #         except socket.error:
        #             print('Failed to create mixer socket')  #todo-mac need exception and logging here
        #             sys.exit()
        #     elif The_Show.mixers[idx].protocol == 'midi':  #todo-mac figure out to start jack server when it's not started yet.
        #         # Get midi input port (i.e. ports we can send to) list
        #         self.client = jack.Client("TempClient")
        #         self.portlist = self.client.get_ports(is_midi=True, is_physical=True)
        #         self.client.deactivate()
        #         self.client.close()
        #         self.client = None
        #         sleep(0.1)
        #         self.portlist.extend(self.getrtmidiports())
        #         self.selidx = 1  # temporarily hardwie to 0, it's my local jack client on my AF12
        #         if isinstance(self.portlist[self.selidx], str):
        #             print('{} ALSA port selected'.format(self.selidx))
        #             self.snd_sndrthread = CommHandlers.AMIDIsender()
        #             partofname = self.portlist[self.selidx].split(':')
        #             senderthread.setport([partofname[0], self.portlist[self.selidx]])
        #             senderthread.amidi_sndrsignal.connect(
        #                 self.snd_sndrtestfunc)  # connect to custom signal called 'signal'
        #             senderthread.finished.connect(
        #                 self.snd_sndrthreaddone)  # connect to buitlin signal 'finished'
        #             senderthread.start()  # start the thread
        #         else:
        #             print('{} JACK port selected'.format(self.selidx))
        #             senderthread = CommHandlers.JMIDIsender('ShowMixer')
        #             senderthread.setport(self.portlist[self.selidx].name)
        #         self.mixer_sender_threads.append(senderthread)
        #         #self.comm_threads.append(senderthread)
        #     else:
        #         raise ValueError('Mixer ID:{0} Unknown or missing protocol.')

        # setup receiver thread
        self.mxr_rcvrthread = CommHandlers.receiver(self.mxr_sock, self.ShowMixerAppDev.IP, self.ShowMixerAppDev.PORT)
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
        #self.cmd_sock.bind((CUE_IP, CUE_PORT))
        self.cmd_sock.bind((self.ShowMixerAppDev.IP, self.ShowMixerAppDev.PORT))
        # setup command receiver thread
        self.cmd_rcvrthread = CommHandlers.cmd_receiver(self.cmd_sock)
        self.cmd_rcvrthread.cmd_rcvrsignal.connect(self.cmd_rcvrtestfunc)  # connect to custom signal called 'signal'
        self.cmd_rcvrthread.finished.connect(self.cmd_rcvrthreaddone)  # connect to builtin signal 'finished'
        self.cmd_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.cmd_rcvrthread)

        #  Setup to send responses to CueEngine
        self.startCEResponsethread()

        self.setupUi(self)
        self.progressBar.setVisible(False)
        self.setWindowTitle('ShowMixer - {}'.format(The_Show.show_conf.settings['title']))
        self.LED_ext_cue_change = LED()
        self.LED_ext_cue_change.setMaximumSize(QtCore.QSize(32, 32))
        self.LED_ext_cue_change.setFixedSize((QtCore.QSize(32,32)))
        self.LED_ext_cue_change.setObjectName("extCueChanged")
        self.verticalLayout_2.insertWidget(0, self.LED_ext_cue_change)
        self.update()

        self.tabWidget.setCurrentIndex(0)
        # Comment out the next lines to disable the associated buttons
        #self.nextButton.clicked.connect(self.on_buttonNext_clicked)
        #self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        #self.savecueButton.clicked.connect(self.on_buttonSaveCue_clicked)
        self.scrollView = False
        self.row_focus_upButton.clicked.connect(self.scroll_cue_list)
        self.row_focus_downButton.clicked.connect(self.scroll_cue_list)
        self.tableView.clicked.connect(self.tableClicked)
        self.actionOpen_Show.triggered.connect(self.openShow)
        self.actionSave_Show.triggered.connect(self.saveShow)
        self.actionClose_Show.triggered.connect(self.closeShow)
        self.actionPreferences.triggered.connect(self.editpreferences)
        self.pref_dlg=ShowPreferences()
        self.slider_entered = ''
        self.slider_keypress = False
        self.sldr_actions_list = []
        self.sldr_action_names = ['Set Min', 'Set 0db', 'Propagate level']
        for action_name in self.sldr_action_names:
            newaction = QAction(action_name, None)
            self.sldr_actions_list.append(newaction)
        self.mute_actions_list = []
        self.mute_action_names = ['Propagate to next', 'Propagate to end']
        for action_name in self.mute_action_names:
            newaction = QAction(action_name, None)
            self.mute_actions_list.append(newaction)

    def mute_action_click(self, position):
        menu = QMenu()
        menu.addActions(self.mute_actions_list)
        mute = self.sender()
        mute_name = mute.objectName()
        print('Sender text: ' + mute_name)
        action = menu.exec_(mute.mapToGlobal(position))
        if action:
            action_name = action.text().replace(' ', '_').lower()
            eval('self.mute_action_{} (mute_name)'.format(action_name))

    def mute_action_propagate_to_next(self, mute_name):
        self.CER_send_edit_start()
        mute = self.window().findChild(QtWidgets.QPushButton, name=mute_name)
        print('Propagate mute {} to next.'.format(mute.objectName()))
        self.mute_propagate(mute)

    def mute_action_propagate_to_end(self, mute_name):
        self.CER_send_edit_start()
        mute = self.window().findChild(QtWidgets.QPushButton, name=mute_name)
        print('Propagate mute {} to next.'.format(mute.objectName()))
        self.mute_propagate(mute, 'end')

    def mute_propagate(self, mute_button, destination='next'):
        mute_button_name = mute_button.objectName()
        mute_chan_name = mute_button_name.replace('mute', 'ch')
        checked_state = mute_button.isChecked()
        control_name = self.get_control_name_from_chan_name(mute_chan_name)
        # start with next cue
        start_index = The_Show.cues.currentcueindex + 1
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        for mxrid in range(The_Show.mixers.__len__()):
            if The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
                if checked_state:
                    mute_val = 0
                else:
                    mute_val = 1
            else:
                if checked_state:
                    mute_val = 1
                else:
                    mute_val = 0

            # iterate through all cues and set the mute state of this mute
            for idx in range(start_index, The_Show.cues.cuecount):
                self.progressBar.setValue(int((100 * (idx / The_Show.cues.cuecount))))
                cue_mutes = The_Show.cues.get_cue_mute_state_by_index(idx)
                mute_state_in_cue = cue_mutes[control_name]
                # if destination is end continue to last cue
                if destination == 'end':
                    # update cue
                    cue_mutes[control_name] = mute_val
                    cue_mutes_list = []
                    for key in cue_mutes: cue_mutes_list.append('{}:{}'.format(key, cue_mutes[key]))
                    cue_mutes_list_sorted = self.sort_controls(cue_mutes_list)
                    cue_mutes_text_sorted = ','.join(str(s) for s in cue_mutes_list_sorted)

                    The_Show.cues.updatecueelement(idx, 'Mutes', cue_mutes_text_sorted)
                else:
                    if mute_state_in_cue != mute_val:
                        # update cue
                        cue_mutes[control_name] = mute_val
                        cue_mutes_list = []
                        for key in cue_mutes: cue_mutes_list.append('{}:{}'.format(key, cue_mutes[key]))
                        cue_mutes_list_sorted = self.sort_controls(cue_mutes_list)
                        cue_mutes_text_sorted = ','.join(str(s) for s in cue_mutes_list_sorted)

                        The_Show.cues.updatecueelement(idx, 'Mutes', cue_mutes_text_sorted)
                    else:
                        break
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

    def sort_controls(self, control_list=[]):
        chlist = []
        auxlist = []
        buslist = []
        mainlist = []
        for control in control_list:
            if 'bus' in control:
                buslist.append(control)
            elif 'aux' in control:
                auxlist.append(control)
            elif 'main' in control:
                mainlist.append(control)
            elif 'ch' in control:
                chlist.append(control)
        buslist = sorted(buslist)
        auxlist = sorted(auxlist)
        mainlist = sorted(mainlist)
        chlist = sorted(chlist)
        sorted_controls = chlist + auxlist + buslist + mainlist
        return sorted_controls


    def get_control_name_from_chan_name(self, control_name):
        mixer_index = int(control_name[1])
        control_index = int(control_name[-2:len(control_name)])
        chan_info = The_Show.mixers[mixer_index].mxrconsole[control_index]
        chan_name = chan_info['name']
        ret_name = control_name[:2] + chan_name.lower()
        return ret_name


    def sldr_action_click(self, position):
        menu = QMenu()
        menu.addActions(self.sldr_actions_list)
        sldr = self.sender()
        sldr_name = sldr.objectName()
        print('Sender text: ' + sldr_name)
        action = menu.exec_(sldr.mapToGlobal(position))
        if action:
            action_name = action.text().replace(' ', '_').lower()
            eval('self.slider_action_{} (sldr_name)'.format(action_name))

    def slider_action_set_min(self, sldr_name):
        self.CER_send_edit_start()
        act_sndr = self.sender()
        sldr = self.window().findChild(QtWidgets.QSlider, name=self.slider_entered)
        print('Set slider to min. Current value: {}'.format(sldr.value()))
        self.slider_set(self.slider_entered, 0)
        self.updatecuelevelstate()

    def slider_action_set_0db(self, sldr_name):
        self.CER_send_edit_start()
        val = db_to_int(0.00)
        act_sndr = self.sender()
        sldr = self.window().findChild(QtWidgets.QSlider, name=self.slider_entered)
        print('Set slider to 0db Current value: {}'.format(sldr.value()))
        self.slider_set(self.slider_entered, val)
        self.updatecuelevelstate()

    def slider_action_propagate_level(self, sldr_name):
        self.CER_send_edit_start()
        print('Propagate slider level.')
        sldr = self.window().findChild(QtWidgets.QSlider, name=sldr_name)
        new_level = sldr.value()
        mixer_index = int(sldr_name[1])
        chan_index = int(sldr_name[-2:len(sldr_name)])
        chan_info = The_Show.mixers[mixer_index].mxrconsole[chan_index]
        chan_name = chan_info['name']
        level_name = sldr_name[:-2].replace('sldr', chan_name.lower())
        next_cue_index = The_Show.cues.currentcueindex + 1
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        for cue_idx in range(next_cue_index, The_Show.cues.cuecount):
            self.progressBar.setValue(int((100*(cue_idx/The_Show.cues.cuecount))))
            levels = The_Show.cues.get_cue_levels(cue_idx)
            try:
                chan_level = levels[level_name]
                levels[level_name] = new_level
                # level_text = ','.join(str(key) + ':' + str(levels.get(key)) for key in levels)
                # level_list = level_text.split(',')
                level_list = []
                for key in levels: level_list.append('{}:{}'.format(key, levels[key]))
                level_list_sorted = self.sort_controls(level_list)
                level_text_sorted = ','.join(str(s) for s in level_list_sorted)
                The_Show.cues.setcueelement(cue_idx, level_text_sorted, 'Levels')
            except KeyError:
                logging.error('In slider_action_propagate_level key {} not found for index: {}!'.format(level_name, cue_idx))
            #print('Cue#{0} Levels:{1}'.format(cue_idx, levels))
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

    def sort_controls(self, control_list=[]):
        chlist = []
        auxlist = []
        buslist = []
        mainlist = []
        for control in control_list:
            if 'bus' in control:
                buslist.append(control)
            elif 'aux' in control:
                auxlist.append(control)
            elif 'main' in control:
                mainlist.append(control)
            elif 'ch' in control:
                chlist.append(control)
        buslist = sorted(buslist)
        auxlist = sorted(auxlist)
        mainlist = sorted(mainlist)
        chlist = sorted(chlist)
        sorted_controls = chlist + auxlist + buslist + mainlist
        return sorted_controls

    def startCEResponsethread(self):
        # Set up sender thread to send responses/alerts to CueEngine

        try:
            self.CEResp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            # todo-mac need exception and logging here
            print('Failed to create CueEngine response socket')
            sys.exit()
        # Setup thread and udp to handle mixer I/O
        try:
            self.CEResponsethread = CommHandlers.sender(self.CEResp_sock)  # , MXR_IP, MXR_PORT)
            self.CEResponsethread.setObjectName('CEResponsethread')
            self.CEResponsethread.sndrsignal.connect(self.CER_signal_handler)  # connect to custom signal called 'signal'
            self.CEResponsethread.finished.connect(self.CER_finished_signal_handler)  # connect to buitlin signal 'finished'
            self.CEResponsethread.start()  # start the thread
            self.comm_threads.append(self.CEResponsethread)
        except socket.error:
            print('Failed to create mixer socket')  # todo-mac need exception and logging here
            sys.exit()

    def startdevicethreads(self):
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
                    senderthread = CommHandlers.sender(self.mxr_sock)   #, MXR_IP, MXR_PORT)
                    senderthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
                    senderthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
                    senderthread.start()  # start the thread
                    self.mixer_sender_threads.append(senderthread)
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
            else:
                raise ValueError('Mixer ID:{0} Unknown or missing protocol.')

    def stopsenderthreads(self):
        for t in self.mixer_sender_threads:
            t.setstopflag()
            t.wait(500)

    def getrtmidiports(self):
        midiclass_ = rtmidi.MidiOut
        logging.info("Creating %s object.", midiclass_.__name__)

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
            #self.scroller = QtWidgets.QScrollArea()
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
            #self.tabWidget.insertTab(idx, self.tablist[idx], "Tab {}".format(idx))
            tab_label = '{} {} ({})'.format(The_Show.show_conf.equipment['mixers'][idx]['mfr'],
                                  The_Show.show_conf.equipment['mixers'][idx]['model'],
                                    idx)
            self.tabWidget.insertTab(idx, self.tablist[idx], tab_label)
            #The_Show.show_conf.equipment['mixers'][0]['mfr']

            for chn in range(The_Show.mixers[idx].mxrconsole.__len__()):
                # Add actor scribble for each channel
                scrbl = QtWidgets.QLabel()
                scrbl.setObjectName('M{0}scr{1:02}'.format(idx,chn))
                # print(scrbl.objectName())
                scrbl.setText(The_Show.mixers[idx].mxrconsole[chn]['name'])
                scrbl.setAlignment(QtCore.Qt.AlignHCenter)
                scrbl.setMinimumWidth(self.ChanStrip_MinWidth)
                scrbl.setMinimumHeight(30)
                scrbl.setWordWrap(True)
                self.tabstripgridlist[idx].addWidget(scrbl, 4, chn, 1, 1)

                # Add charactor scribble for each channel
                chscrbl = QtWidgets.QLabel()
                chscrbl.setObjectName('M{0}chscr{1:02}'.format(idx,chn))
                # print(scrbl.objectName())
                chscrbl.setText(The_Show.mixers[idx].mxrconsole[chn]['name'])
                chscrbl.setAlignment(QtCore.Qt.AlignHCenter)
                chscrbl.setMinimumWidth(self.ChanStrip_MinWidth)
                chscrbl.setMinimumHeight(30)
                chscrbl.setWordWrap(True)
                self.tabstripgridlist[idx].addWidget(chscrbl, 5, chn, 1, 1)

                # Add slider for this channel
                # sldr = QtWidgets.QSlider(QtCore.Qt.Vertical)  # default sliders
                sldr = MySlider()                           # slider with decibel ticks
                #sldr.setContextMenuPolicy(Qt.ActionsContextMenu)
                sldr.setContextMenuPolicy(Qt.CustomContextMenu)
                sldr.customContextMenuRequested.connect(self.sldr_action_click)
                #sldr.addActions(self.sldr_actions_list)
                # sldr.valueChanged.connect(self.sliderprint)
                sldr.sliderMoved.connect(self.slidermove)
                sldr.valueChanged.connect(self.slidervalchanged)
                sldr.sliderReleased.connect(self.sldrmovedone)
                sldr.sliderPressed.connect(self.slder_pressed)
                sldr.kpsig.connect(self.slder_kybd_sig_handler)
                sldr.setObjectName('M{0}sldr{1:02}'.format(idx, chn))
                # print(sldr.objectName())
                sldr.setMinimumSize(self.ChanStrip_MinWidth,200)
                sldr.setRange(0,1024)
                # sldr.setTickPosition(3)
                # sldr.setTickInterval(10)
                sldr.setSingleStep(26) # with 0-1024, 1db step is 26(int)
                sldr.setPageStep(260)  # 20x for page
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
                mute.setContextMenuPolicy(Qt.CustomContextMenu)
                mute.customContextMenuRequested.connect(self.mute_action_click)
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

    def slder_kybd_sig_handler(self):
        print('In slder_sig_handler')
        self.slider_keypress = True

    def changelayout(self):
        self.tablist = []
        self.tablistvertlayout = []
        self.tabgridlayoutlist = []
        self.tabstripgridlist = []
        self.scrollArea = []
        self.scrollAreaWidgetContents = []
        self.addChanStrip()

    def emptytabs(self, count):
        for idx in reversed(range(count)):
            self.tabWidget.removeTab(idx)
        QApplication.processEvents()
        return

    def deletecontrols(self):
        for tab in self.tablist:
            sliders = tab.findChildren(QSlider)
            print('slider count: {0}'.format(sliders.__len__()))
            for slider in sliders:
                slider.setParent(None)
            sliders = self.tablist[0].findChildren(QSlider)
            print('slider count: {0}'.format(sliders.__len__()))
            lbls = tab.findChildren(QLabel)
            print('label count: {0}'.format(lbls.__len__()))
            for lbl in lbls:
                lbl.setParent(None)
            lbls = tab.findChildren(QLabel)
            print('label count: {0}'.format(lbls.__len__()))
            btns = tab.findChildren(QPushButton)
            print('button count: {0}'.format(btns.__len__()))
            for btn in btns:
                btn.setParent(None)
            btns = tab.findChildren(QLabel)
            print('buttons count: {0}'.format(btns.__len__()))

        QApplication.processEvents()
        return

    def slidermove(self, val):
        sending_slider = self.sender()
        print('In slidermove, sending_slider name: {0}'.format(sending_slider.objectName()))

        # todo - moved this code to slidervalchanged...not sure if it messed anything up
        # self.cuehaschanged = True
        # sending_slider = self.sender()
        # print('In slidermove, sending_slider name: {0}'.format(sending_slider.objectName()))
        # sldrname = sending_slider.objectName()
        # mxrid = int(sldrname[1])
        # stripGUIindx = int(sldrname[-2:len(sldrname)])
        # scrLblname = sldrname.replace('sldr', 'lev')
        # scrLbl = self.findChild(QtWidgets.QLabel, name=scrLblname)
        # val_db = int_to_db(val)
        # scrLbl.setText('{0:>.2f}'.format(val_db))  # todo - mac see here for formating db rounded display
        # msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
        #     mxrconsole[stripGUIindx]['type']]['fader']. \
        #     Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], val)
        # if msg is not None:
        #     self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def slder_pressed(self):
        # if external change in progress, return
        if self.ExternalEditStarted and not self.ExternalEditComplete:
            self.NotifyEditInProgress()
            return


    def sldrmovedone(self):
        print('In sldrmovedone')
        sldr = self.sender()
        # if external change in progress, return
        if self.ExternalEditStarted and not self.ExternalEditComplete:
            self.NotifyEditInProgress()
            return

        levels = ''
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                sldr = self.window().findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
                levels += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower(), sldr.value())
                print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
        levels = levels[:-1]
        print(levels)
        The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels, 'Levels')
        pass

    def slidervalchanged(self, val):
        sending_slider = self.sender()
        print('Enter slidervalchanged, sending_slider name: {0}'.format(sending_slider.objectName()))
        print('SliderDown is : {}'.format(sending_slider.isSliderDown()))
        if sending_slider.isSliderDown() or self.slider_keypress:
            self.cuehaschanged = True
            CE_msg = osc_message_builder.OscMessageBuilder(address='/cue/editstarted')
            CE_msg.add_arg(True)
            CE_msg = CE_msg.build()
            self.CEResponsethread.queue_msg(CE_msg, self.CueAppDev)
        sldrname = sending_slider.objectName()
        mxrid = int(sldrname[1])
        stripGUIindx = int(sldrname[-2:len(sldrname)])
        scrLblname = sldrname.replace('sldr', 'lev')
        scrLbl = self.findChild(QtWidgets.QLabel, name=scrLblname)
        val_db = int_to_db(val)
        scrLbl.setText('{0:>.2f}'.format(val_db))  # todo - mac see here for formating db rounded display
        if not self.scrollView:
            msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                mxrconsole[stripGUIindx]['type']]['fader']. \
                Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], val)
            if msg is not None:
                self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
        if sending_slider.isSliderDown() or self.slider_keypress:
            print('In slidervalchanged, sending_slider name: {0}, updating level state'.format(sending_slider.objectName()))
            self.updatecuelevelstate()
        if self.slider_keypress: self.slider_keypress = False  # clear the keypress flag
        print('Exit slidervalchanged, sending_slider name: {0}'.format(sending_slider.objectName()))


    def slider_set(self, sldrname, val):
        self.cuehaschanged = True
        mxrid = int(sldrname[1])
        stripGUIindx = int(sldrname[-2:len(sldrname)])
        scrLblname = sldrname.replace('sldr', 'lev')
        scrLbl = self.findChild(QtWidgets.QLabel, name=scrLblname)
        sldr = self.findChild(QtWidgets.QSlider, name=sldrname)
        val_db = int_to_db(val)
        scrLbl.setText('{0:>.2f}'.format(val_db))
        msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
            mxrconsole[stripGUIindx]['type']]['fader']. \
            Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], val)
        sldr.setSliderPosition(int(val))
        if msg is not None:
            self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def on_buttonNext_clicked(self):
        self.next_cue()

    def on_buttonJump_clicked(self):
        self.execute_cue(The_Show.cues.selectedcueindex) # selectedcueindex no longer

    def on_buttonSaveCue_clicked(self): # todo mac this needs to save mute state
        """Save the current state of the levels and mutes for this cue"""
        print('Save Cue clicked!')
        levels = ''
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                sldr = self.findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
                sldr_name = The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower()
                levels += 'M{0}{1}:{2},'.format(mxrid, sldr_name, sldr.value())
                # print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
        levels = levels[:-1]
        print(levels)
        The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels, 'Levels')
        #  Commented this out because I don't why I would have changed the levels in an existing and then add a new cue
        # The_Show.cues.addnewcue()

    def updatecuelevelstate(self):
        levels = ''
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                sldr = self.findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
                levels += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower(), sldr.value())
                # print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
        levels = levels[:-1]
        print('In updatecuelevelstate, Levels: {}'.format(levels))
        The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels, 'Levels')
        pass

    def updatecuemutestate(self):  # todo-mac general overhaul of elements in cue.xml file
                                    # Entrances, Exits, and Mutes worked out...
        mutes = ''
        for mxrid in range(The_Show.mixers.__len__()):
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                mute = self.findChild(QtWidgets.QPushButton, name='M{0}mute{1:02}'.format(mxrid, stripGUIindx))
                if The_Show.mixers[mxrid].mutestyle['mutestyle']== 'illuminated':
                    if mute.isChecked():
                        mute_val = 0
                    else:
                        mute_val = 1
                else:
                    if mute.isChecked():
                        mute_val = 1
                    else:
                        mute_val = 0

                mutes += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower(), '{0}'.format(mute_val))
        mutes = mutes[:-1]
        print('In updatecuemutestate, mutes: {}'.format(mutes))
        The_Show.cues.setcueelement(The_Show.cues.currentcueindex, mutes, 'Mutes')
        pass

    def execute_cue_uuid(self, uuid):
        cueidx = The_Show.cues.getcueindexbyuuid(uuid)
        print('In execute_cue_uuid, cue index={}'.format(cueidx))
        self.execute_cue(int(cueidx))

    def execute_cue(self, num, hard=False):
        print('In execute_cue, cue number:{}'.format(num))
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
        The_Show.cues.currentcueindex = num
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
        self.execute_mutes(hard)
        self.execute_levels(hard)
        self.execute_MixerMap()
        # move table focus to next cue
        # ***changed this: now mutes/sliders show state of highlighted cue
        # The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
        # The_Show.cues.currentcueindex += 1
        # tblvw.selectRow(The_Show.cues.currentcueindex)
        self.update()
        return

    def execute_mutes(self, hard=False):
        #mute_changes = The_Show.cues.get_cue_mute_state_delta(The_Show.cues.currentcueindex)
        #mute_changes = The_Show.cues.get_cue_mute_state_by_index(The_Show.cues.currentcueindex)
        if The_Show.cues.currentcueindex == 0 or hard:
            mute_changes = The_Show.cues.get_cue_mute_state_by_index(The_Show.cues.currentcueindex)
        else:
            from_element = The_Show.cues.get_cue_element_by_name(The_Show.cues.previouscueindex, 'Mutes').text.split(',')
            to_element = The_Show.cues.get_cue_element_by_name(The_Show.cues.currentcueindex, 'Mutes').text.split(',')
            mute_changes = {ch_mute.split(':')[0]: int(ch_mute.split(':')[1]) for ch_mute in to_element if ch_mute not in from_element}
        # iterate through mute changes, if any
        if mute_changes != None:
            for key, value in mute_changes.items():
                # find the channel name in the mxrconsole list
                # that should be the stripGUIindex
                #get name from key
                nbrs = re.findall(r'\d+',key)  # old way to striGUIindex
                mxrid = int(nbrs[0])
                chname = key[re.search('\d', key).end():]
                # for cons_idx in The_Show.mixers:
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

    def execute_levels(self, hard=False):
        if The_Show.cues.currentcueindex == 0 or hard:
            levels = The_Show.cues.get_cue_levels(The_Show.cues.currentcueindex)
        else:
            from_element = The_Show.cues.get_cue_element_by_name(The_Show.cues.previouscueindex, 'Levels').text.split(',')
            to_element = The_Show.cues.get_cue_element_by_name(The_Show.cues.currentcueindex, 'Levels').text.split(',')
            levels = {level.split(':')[0] : int(level.split(':')[1]) for level in to_element if level not in from_element}

        if levels != None:
            for key, value in levels.items():
                # find the channel name in the mxrconsole list
                # that should be the stripGUIindex
                #get name from key
                nbrs = re.findall(r'\d+',key)
                mxrid = int(nbrs[0])
                chname = key[re.search('\d', key).end():]
                #print(chname)
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

    def execute_MixerMap(self):
        """Check for MixerMap entrees with this cues uuid
        if true, do the map"""
        mixermap_element = The_Show.cues.get_cue_element_by_name(The_Show.cues.currentcueindex, 'map')
        if mixermap_element != None:
            current_map_index = int(mixermap_element.text)
        else:
            current_map_index = 0
        # if mixermap_element:
        #     input_maps = mixermap_element.findall('input')
        #     for input_map in input_maps:
        #         mixerid = input_map.get('mixerid')
        #         mixerchan = input_map.get('chan')
        #         actor = input_map.get('actor')
        #         char = input_map.get('char')
        #         print('Mixer id: {}, chan: {}, actor: {}, char: {}'.format(mixerid, mixerchan, actor, char))
        current_cue_uuid = None
        print('last map: {}, current map:{}'.format(self.last_mixermap, current_map_index))
        logging.info('last map: {}, current map:{}'.format(self.last_mixermap, current_map_index))
        map_index_delta = current_map_index - self.last_mixermap
        indexes = []
        if map_index_delta == 1:  # we single stepped to a new map
            logging.info('executing map {}'.format(current_map_index))
            indexes.append(current_map_index)
            self.set_scribble_bycount(current_map_index)
        elif map_index_delta > 1:  # we've jumped forward, do last + 1 through and including current
            logging.info('executing map {} thru {}'.format(self.last_mixermap, current_map_index))
            indexes = list(range(self.last_mixermap + 1, current_map_index + 1))
        elif map_index_delta < 0:  #  we're going backwards, do cumulative maps to new current point
            logging.info('executing cumulative map')
            indexes = range(0, current_map_index + 1)
        for mm in indexes:
            self.set_scribble_bycount(mm)
        self.last_mixermap = current_map_index

    def next_cue(self):
        nextmxrcuefound = False
        index = The_Show.cues.currentcueindex
        # find the next cue with type Mixer
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
            low_level = db_to_int(-90)
            for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                    mxrconsole[stripGUIindx]['type']]['fader'].\
                    Set(The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['channum'], low_level)
                if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])

    def on_buttonMute_clicked(self):
        mbtn = self.sender()
        # if external change in progress, return
        if self.ExternalEditStarted and not self.ExternalEditComplete:
            self.NotifyEditInProgress()
            #mbtn.setChecked(not mbtn.isChecked())
            mbtn.toggle()
            return

        self.cuehaschanged = True
        CE_msg = osc_message_builder.OscMessageBuilder(address='/cue/editstarted')
        CE_msg.add_arg(True)
        CE_msg = CE_msg.build()
        self.CEResponsethread.queue_msg(CE_msg, self.CueAppDev)
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
        self.updatecuemutestate()

    def setfirstcue(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
        # self.execute_cue(The_Show.cues.currentcueindex)

    def getcurrentcueuuid(self):
        """ THis is a kludge to get things working"""
        uuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
        return uuid


    def scroll_cue_list(self):
        source_name = self.sender().objectName()
        tblvw = self.findChild(QtWidgets.QTableView)
        if 'up' in source_name:  # scrol up the table, i.e. previous cue
            if The_Show.cues.currentcueindex > 0:
                The_Show.cues.currentcueindex -= 1
            else:
                The_Show.cues.currentcueindex = 0
            #The_Show.cues.previouscueindex = The_Show.cues.currentcueindex -1
            #direction = -1
        else:  # scroll down the table, i.e. the next cue
            if The_Show.cues.currentcueindex < The_Show.cues.cuecount - 1:
                #The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
                The_Show.cues.currentcueindex += 1
            else:
                The_Show.cues.currentcueindex = The_Show.cues.cuecount - 1
            #direction = 1
        tblvw.selectRow(The_Show.cues.currentcueindex)
        self.display_cue_mutes()
        self.display_cue_levels()

    def display_cue_mutes(self):
        mutes = The_Show.cues.get_cue_mute_state_by_index(The_Show.cues.currentcueindex)
        if mutes is not None:  # iterate through mutes
            for key, value in mutes.items():
                # find the channel name in the mxrconsole list, it should be the stripGUIindex
                # get name from key
                nbrs = re.findall(r'\d+',key)  # old way to striGUIindex
                mxrid = int(nbrs[0])
                chname = key[re.search('\d', key).end():]
                for cons_idx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
                    if The_Show.mixers[mxrid].mxrconsole[cons_idx]['name'].lower() == chname.lower():
                        # print('found in stp {0}'.format(cons_idx))
                        stripGUIindx = cons_idx
                        break
                mute = self.findChild(QtWidgets.QPushButton, name='M{0}mute{1:02}'.format(mxrid, stripGUIindx))
                if value == 1:  # 1 >> unmute  0 >> mute
                    # Handle unmute
                    if The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
                        mute.setChecked(False)  # for illuminated = unmuted
                    else:
                        mute.setChecked(True)  # for a dark = umuted
                    #muteval = The_Show.mixers[mxrid].mutestyle['unmute']
                else:  # Handle mute
                    if The_Show.mixers[mxrid].mutestyle['mutestyle'] == 'illuminated':
                        mute.setChecked(True)
                    else:
                        mute.setChecked(False)
                    #muteval = The_Show.mixers[mxrid].mutestyle['mute']
        return

    def display_cue_levels(self):
        self.scrollView = True
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
                    sldr.setSliderPosition(int(value))
        self.scrollView = False
        return


    def openShow(self):
        '''
        Present file dialog to select new ShowConf.xml file
        :return:
        '''
        fdlg = QtWidgets.QFileDialog()
        fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fdlg.close()
        # update ShowControl_config.xml with new project folder and file
        # print(fname[0])
        # newprojfolder = os.path.dirname(fname(0))
        tabcount = The_Show.mixers.__len__()
        newprojectfolder, newprojfile = os.path.split(fname[0])
        cfg.cfgdict['configuration']['project']['folder'] = newprojectfolder
        cfg.cfgdict['configuration']['project']['file'] = newprojfile
        newtree = cfg.updateFromDict()
        cfg.write(newtree, False, CFG_PATH)
        cfg.reload()
        The_Show.loadNewShow(cfg.cfgdict)
        The_Show.reload()
        self.stopsenderthreads()
        time.sleep(.5)
        self.startdevicethreads()
        self.deletecontrols()
        self.emptytabs(tabcount)
        self.changelayout()
        self.setWindowTitle(The_Show.show_conf.settings['project']['title'])
        self.initmutes()
        self.initlevels()
        self.disptext()
        self.setfirstcue()
        firstuuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
        self.set_scribble(firstuuid)

    def saveShow(self):
        The_Show.cues.savecuelist(True, cfg.cfgdict['configuration']['project']['folder'] + '/' + The_Show.show_conf.settings['cues']['href1'])
        self.cuehaschanged = False
        self.CER_send_edit_complete()
        # CE_msg = osc_message_builder.OscMessageBuilder(address='/cue/editcomplete')
        # CE_msg.add_arg(True)
        # CE_msg = CE_msg.build()
        # self.CEResponsethread.queue_msg(CE_msg, self.CueAppDev)

    def closeShow(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        print(fname)

    def editpreferences(self):
        if cfg.cfgdict['configuration']['prefs']['exitwithce'] == 'true':
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Checked)
        else:
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Unchecked)
        self.pref_dlg.show()
        #self.itb = QDialog()
        #self.ui_prefdlg = Ui_Preferences()
        #self.ui_prefdlg.setupUi(self.itb)
        #self.itb.show()

    def set_scribble(self, uuid='bad'):
        #charcount = int(mxrmap.getroot().attrib['charcount'])
        charcount = The_Show.chrchnmap.getmixermapcharcount(uuid)
        #chars = mxrmap.findall('input')
        chars = The_Show.chrchnmap.getmixermapinputs(uuid)
        for char in chars:
            cnum = int(char.attrib['chan'])
            mxrid = int(char.attrib['mixerid'])
            msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                mxrconsole[cnum - 1]['type']]['scribble'].\
                Set(cnum, char.attrib['char'])
            if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
            # print('M{0}scr{1:02}'.format(mxrid,cnum))
            actorlbl = self.findChild(QtWidgets.QLabel, name='M{0}scr{1:02}'.format(mxrid,cnum-1))
            actorlbl.setText(char.attrib['actor'][:7])
            charlbl = self.findChild(QtWidgets.QLabel, name='M{0}chscr{1:02}'.format(mxrid,cnum-1))
            charlbl.setText(char.attrib['char'][:7])

        buses = The_Show.chrchnmap.getmixermapbus(uuid)
        for bus in buses:
            cnum = int(bus.attrib['chan'])
            mxrid = int(bus.attrib['mixerid'])
            #find the index of the bus to get the .Set object
            for control_index, mxcons in enumerate(The_Show.mixers[mxrid].mxrconsole):
                if mxcons['name'] == 'Bus{:02}'.format(cnum):
                    break
            msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                mxrconsole[control_index]['type']]['scribble']. \
                Set(cnum, bus.attrib['char'])
            if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
            actorlbl = self.findChild(QtWidgets.QLabel, name='M{0}scr{1:02}'.format(mxrid, control_index))
            actorlbl.setText(bus.attrib['actor'][:7])
            charlbl = self.findChild(QtWidgets.QLabel, name='M{0}chscr{1:02}'.format(mxrid, control_index))
            charlbl.setText(bus.attrib['char'][:7])

            auxes = The_Show.chrchnmap.getmixermapaux(uuid)
            for aux in auxes:
                cnum = int(aux.attrib['chan'])
                mxrid = int(aux.attrib['mixerid'])
                # find the index of the bus to get the .Set object
                for control_index, mxcons in enumerate(The_Show.mixers[mxrid].mxrconsole):
                    if mxcons['name'] == 'Aux{:02}'.format(cnum):
                        break
                msg = The_Show.mixers[mxrid].mxrstrips[The_Show.mixers[mxrid].
                    mxrconsole[control_index]['type']]['scribble']. \
                    Set(cnum, aux.attrib['char'])
                if msg is not None: self.mixer_sender_threads[mxrid].queue_msg(msg, The_Show.mixers[mxrid])
                actorlbl = self.findChild(QtWidgets.QLabel, name='M{0}scr{1:02}'.format(mxrid, control_index))
                actorlbl.setText(aux.attrib['actor'][:7])
                charlbl = self.findChild(QtWidgets.QLabel, name='M{0}chscr{1:02}'.format(mxrid, control_index))
                charlbl.setText(aux.attrib['char'][:7])
            pass

    def set_scribble_bycount(self, count=0):
        mixermap_element = The_Show.chrchnmap.get_map_element_by_count(count)
        if mixermap_element:
            input_maps = mixermap_element.findall('input')
            for input_map in input_maps:
                mixerid = int(input_map.get('mixerid'))
                mixerchan = int(input_map.get('chan'))
                actor = input_map.get('actor')
                char = input_map.get('char')
                print('Mixer id: {}, chan: {}, actor: {}, char: {}'.format(mixerid, mixerchan, actor, char))
                msg = The_Show.mixers[mixerid].mxrstrips[The_Show.mixers[mixerid].
                    mxrconsole[mixerchan - 1]['type']]['scribble'].\
                    Set(mixerchan, char)
                if msg is not None: self.mixer_sender_threads[mixerid].queue_msg(msg, The_Show.mixers[mixerid])
                # print('M{0}scr{1:02}'.format(mxrid,cnum))
                actorlbl = self.findChild(QtWidgets.QLabel, name='M{0}scr{1:02}'.format(mixerid,mixerchan-1))
                actorlbl.setText(actor[:7])
                charlbl = self.findChild(QtWidgets.QLabel, name='M{0}chscr{1:02}'.format(mixerid,mixerchan-1))
                charlbl.setText(char[:7])
        return

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        #self.tableView.connect(self.tableClicked, QtCore.SIGNAL("clicked()"))

    def get_table_data(self):
        self.tabledata = []
        for index in range(0, The_Show.cues.cuecount):
            cuenum = '{0:03}'.format(index)
            q = The_Show.cues.cuelist.find(".cues/cue[@num='"+cuenum+"']")
            type_list = q.find('CueType').text.split(',')
            for type in cue_types:
                if type in type_list and self.CueTypeVisible[type]:
                    self.append_table_data(q)
                    break
        # print(self.tabledata)
        return
        # qs = The_Show.cues.cuelist.findall('Cue')
        # self.tabledata =[]
        # for q in qs:
        #     dirty_list = q.find('CueType').text.split(',')
        #     type_list = [s.strip() for s in dirty_list]
        #     for type in cue_types:
        #         if type in type_list and self.CueTypeVisible[type]:
        #             self.append_table_data(q)
        #             break

    def append_table_data(self, q):
        tmp_list = ['{0:03}'.format(int(q.attrib['num']))]
        for i in range(1, header.__len__()):
            dirty_data = q.find(header[i].replace(' ','')).text
            try:
                clean_data = dirty_data.strip()
                tmp_list.append(clean_data)
            except AttributeError:
                tmp_list.append('')
        tmp_list.append('junk')
        self.tabledata.append(tmp_list)

    def tableClicked(self, modelidx):
        rowidx = modelidx.row()
        The_Show.cues.currentcueindex = rowidx
        self.tableView.selectRow(The_Show.cues.currentcueindex)
        # print('table clicked, row{}'.format(rowidx))
        self.display_cue_mutes()
        self.display_cue_levels()


    def closeEvent(self, event):
        """..."""
        if self.cuehaschanged:
            reply = self.confirmUnsaved()
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Save:
                # todo - mac this is hardwired to project cue file
                The_Show.cues.savecuelist(True, cfg.cfgdict['configuration']['project']['folder'] + '/' + The_Show.show_conf.settings['cues']['href1'])
                self.CER_send_edit_complete()
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

    def confirmUnsaved(self):
            return QMessageBox.question(self, 'Save Changes', 'Changed cues are unsaved!',
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                     QMessageBox.Cancel)

    '''CueEngine thread functions'''
    def CER_q_put(self, msg):
        """..."""
        self.CERespthread.queue_msg(msg)

    def CER_signal_handler(self, sigstr):
        """..."""
        # print(sigstr)
        self.statusBar().showMessage(sigstr)

    def CER_finished_signal_handler(self):
        """called when the signal called 'signal' is emitted from thread called CEResponse thread """
        print('CE Response thread done')

    def CER_send_edit_start(self):
        self.cuehaschanged = True
        CE_msg = osc_message_builder.OscMessageBuilder(address='/cue/editstarted')
        CE_msg.add_arg(True)
        CE_msg = CE_msg.build()
        self.CEResponsethread.queue_msg(CE_msg, self.CueAppDev)

    def CER_send_edit_complete(self):
        CE_msg = osc_message_builder.OscMessageBuilder(address='/cue/editcomplete')
        CE_msg.add_arg(True)
        CE_msg = CE_msg.build()
        self.CEResponsethread.queue_msg(CE_msg, self.CueAppDev)

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
        print('In cmd_rcvrtestfunc, OSC address: {}'.format(msg.address))
        for idx, param in enumerate(msg.params):
            print('param[{0}]: {1}'.format(idx, param))
        if msg.address == '/cue':
            if msg.params[0] == "Next":
                print('OSC msg.params[0]: {}'.format(msg.params[0]))
                self.next_cue()
        elif msg.address == '/cue/#':
            print('cue # : {}'.format(msg.params[0]))
            self.execute_cue(msg.params[0])
        elif msg.address == '/cue/uuid':
            print('cue uuid : {}'.format(msg.params[0]))
            self.execute_cue_uuid(msg.params[0])
        elif msg.address == '/cue/editstarted':
            if msg.params[0] == True:
                self.ExternalEditStarted = True
                self.LED_ext_cue_change.toggle(True)
        elif msg.address == '/cue/editcomplete':
            if msg.params[0] == True:
                self.ExternalEditComplete = True
                self.CueFileUpdate_sig.emit(msg.params[1])
                self.LED_ext_cue_change.toggle(False)
        elif msg.address == '/cue/quit':
            self.externalclose = True
            self.close()

    def NotifyEditInProgress(self):
        QMessageBox.information(self,'Cue Modification','Cue modification blocked, external edit in progress.', QMessageBox.Ok)

    def ExternalCueUpdate(self, changed=True):  # Always default to changed
        self.statusBar().showMessage('External Cue Update')
        logging.info('External Cue Update, changed flag: {}')
        if changed:
            index_before_update = The_Show.cues.currentcueindex
            The_Show.reloadShow(cfg.cfgdict)
            self.setWindowTitle(The_Show.show_conf.settings['title'])
            #self.initmutes()
            #self.initlevels()
            self.disptext()
            self.setfirstcue()
            firstuuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
            self.set_scribble(firstuuid)
            The_Show.cues.currentcueindex = index_before_update
            self.tableView.selectRow(The_Show.cues.currentcueindex)
            self.display_cue_mutes()
            self.display_cue_levels()
            self.execute_cue(The_Show.cues.currentcueindex, hard=True)
        self.ExternalEditStarted = False
        self.ExternalEditComplete = False

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
        for t in self.mixer_sender_threads:
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
    kpsig = pyqtSignal()

    def __init__(self, parent=None):
        super(MySlider, self).__init__(parent)

    def mouseReleaseEvent(self, m_ev):
        """Subclassed from QSlider"""
        # levels = ''
        # for mxrid in range(The_Show.mixers.__len__()):
        #     for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
        #         sldr = self.window().findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
        #         levels += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower(), sldr.value())
        #         print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
        # levels = levels[:-1]
        # print(levels)
        # The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels, 'Levels')
        QtWidgets.QSlider.mouseReleaseEvent(self, m_ev)

    def keyPressEvent(self, k_ev):
        print('In keyPressEvent for slider {}'.format(self.objectName()))
        if k_ev.key() in  [Qt.Key_Up, Qt.Key_Down, Qt.Key_PageDown, Qt.Key_PageUp]:
            #self.window().slider_keypress = True
            self.kpsig.emit()
            # levels = ''
            # for mxrid in range(The_Show.mixers.__len__()):
            #     for stripGUIindx in range(The_Show.mixers[mxrid].mxrconsole.__len__()):
            #         sldr = self.window().findChild(QtWidgets.QSlider, name='M{0}sldr{1:02}'.format(mxrid, stripGUIindx))
            #         levels += 'M{0}{1}:{2},'.format(mxrid, The_Show.mixers[mxrid].mxrconsole[stripGUIindx]['name'].lower(), sldr.value())
            #         #print('M{0}sldr{1:02}:{2:3}'.format(mxrid, stripGUIindx, sldr.value()))
            # levels = levels[:-1]
            # print('In keyPressEvent, levels: {}'.format(levels))
            # The_Show.cues.setcueelement(The_Show.cues.currentcueindex, levels, 'Levels')
        QtWidgets.QSlider.keyPressEvent(self, k_ev)

    def keyReleaseEvent(self, k_ev):
        print('In keyReleaseEvent for slider {}'.format(self.objectName()))
        if k_ev.key() in  [Qt.Key_Up, Qt.Key_Down, Qt.Key_PageDown, Qt.Key_PageUp]:
            pass
        QtWidgets.QSlider.keyPressEvent(self, k_ev)

    def enterEvent(self, m_ev):
        self.window().slider_entered = self.objectName()

    # Note: commented out because it looks too busy with 30+ sliders
    # def paintEvent(self, event):
    #     """Paint log scale ticks"""
    #     super(MySlider, self).paintEvent(event)
    #     qp = QPainter(self)
    #     pen = QPen()
    #     pen.setWidth(2)
    #     pen.setColor(Qt.black)
    #
    #     qp.setPen(pen)
    #     font = QFont('Times', 10)
    #     font_y_offset = font.pointSize()/2
    #     qp.setFont(font)
    #     size = self.size()
    #     contents = self.contentsRect()
    #     db_val_list =   [10, 5, 0, -5, -10, -20, -30, -40, -50, -60, -90]
    #     for val in db_val_list:
    #         if val == 10:
    #             y_val_fudge = 12
    #         elif val == -90:
    #             y_val_fudge = -12
    #         db_scaled = db_to_int(val)
    #         y_val = contents.height() - translate(db_scaled, 0, 1023, 0, contents.height())
    #         if val == -90:
    #             qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge, '-oo')
    #         else:
    #             qp.drawText(contents.x() - font.pointSize(), y_val + font_y_offset + y_val_fudge,'{0:2}'.format(val))
    #         qp.drawLine(contents.x() + font.pointSize(), y_val + y_val_fudge,  contents.x() + contents.width(), y_val + y_val_fudge)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        logging.info('In MyTableModel.')
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if len(self.arraydata) > 0: 
            #return len(self.arraydata[0])  # this will attempt to do all columns in arraydata
                                            # and since headerdata is shorter than the number of columns
                                            # (if all cue data is in the array) then it gets an
                                            # index error when it trys to index to column(len(headerdata)+1)
            return len(self.headerdata)  # this only displays the colmns defined in headerdata
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename= LOG_DIR + '/ShowMixer.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info('Begin')
    cfg = configuration()
    The_Show = ShowMxr()
    The_Show.displayShow()
    # try:
    app = QtWidgets.QApplication(sys.argv)
    #     app.setStyleSheet(""" QPushButton {color: blue;
    #                          background-color: yellow;
    #                          selection-color: blue;
    #                          selection-background-color: green;}""")
    # app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    ui = ChanStripMainWindow(path.abspath(path.join(path.dirname(cfg.cfgdict['configuration']['project']['folder']))))
    # ui.resize(chans*ui.ChanStrip_MinWidth,800)
    ui.addChanStrip()
    ui.resize(ui.max_slider_count * ui.ChanStrip_MinWidth, 800)
    ui.disptext()
    ui.initmutes()
    ui.initlevels()
    ui.setfirstcue()
    firstuuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
    ui.set_scribble(firstuuid)
    ui.execute_cue_uuid(firstuuid)
    ui.show()
    # execute the 000 cue to initialize the mixer
    # except KeyboardInterrupt:
    #     parser.exit('\nInterrupted by user')
    # # except (queue.Full):
    # #     # A timeout occured, i.e. there was an error in the callback
    # #     parser.exit(1)
    # except Exception as e:
    #     parser.exit(type(e).__name__ + ': ' + str(e))
    logging.info('Shutdown')
    sys.exit(app.exec_())

