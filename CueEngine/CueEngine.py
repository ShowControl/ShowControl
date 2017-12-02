#!/usr/bin/env python3
__author__ = 'mac'
__appmod__ = 'CueEngine'

import os, sys, inspect, subprocess
import types
import argparse
import socket
from time import sleep
from curses.ascii import isprint
import psutil
import rtmidi
from rtmidi.midiutil import get_api_from_environment
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON
import re

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush, QPalette, QPainter, QPen, QPixmap

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import xml.etree.ElementTree as ET
from os import path

import logging
LOG_NAME = 'CE_logger'
module_logger = logging.getLogger('CE_logger')
_translate = QtCore.QCoreApplication.translate

from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_ON
RtMidiIn_client_re = re.compile('.*RtMidi input')
#a = RtMidiIn_client_re.findall('xxxRtMidiIn Clientxxxx:RtMidi input xxxx128:0')
#b = RtMidiIn_client_re.findall('xxxRtMixdiIn Clientxxxx:RtMixdi input xxxx128:0')

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
module_logger.info('test if module_logger is instantiated')
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)


from ShowControl.utils.ShowControlConfig import configuration, CFG_DIR, CFG_PATH, LOG_DIR
from ShowControl.utils.Show import Show
#from ShowControlConfig import configuration, CFG_DIR, CFG_PATH, LOG_DIR
from ShowControl.utils import CommHandlers
from ShowControl.utils.Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields
from ShowControl.utils import styles

from CueEngine.CueEngine_ui import Ui_MainWindow
from CueEngine.CueEdit_alt_ui import Ui_dlgEditCue
import CueEngine.CueEngine_rsrc_rc

from pythonosc import osc_message
from pythonosc import osc_message_builder

changeStates = {'started': False, 'completed': False}

class CommAddresses:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT


# INMSG_IP = "127.0.0.1"
# INMSG_PORT = 5006

class cueTypeDispatcher():
    def __init__(self):
        self.dispatch = {'Stage':self.do_stage,
                         'Mixer':self.do_mixer(),
                         'Sound':self.do_sound,
                         'SFX':self.do_SFX,
                         'Light':self.do_light}

    def do_stage(self):
        pass

    def do_mixer(self):
        msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
        msg.add_arg(self.The_Show.cues.currentcueindex)
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)

    def do_sound(self):

        msg = [NOTE_ON, 60, 112]
        self.snd_sndrthread.queue_msg(msg, self.CueAppDev)

    def do_SFX(self):
        msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
        msg.add_arg(self.The_Show.cues.currentcueindex)
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)
        pass

    def do_light(self):
        pass

class EditCue(QDialog, Ui_dlgEditCue):
    def __init__(self, index, parent=None):
        QDialog.__init__(self, parent)
        self.editidx = index
        self.setupUi(self)
        self.chgdict = {}
        self.chglist = []
        self.changeflag = False
        for cuetypectlidx in range(cue_subelements.__len__()):
            if cue_fields[cuetypectlidx] == 'Cue_Type':
                break
        self.edt_list[cuetypectlidx].setText('Select cue type/s ')
        # self.toolButton.setText('Select cue type/s ')
        self.toolmenu = QtWidgets.QMenu(self)
        # self.toolmenu.triggered[QtWidgets.QAction].connect(self.processtrig)
        for i in range(cue_types.__len__()):
            action = self.toolmenu.addAction(cue_types[i])
            action.setCheckable(True)
        # self.toolButton.setMenu(self.toolmenu)
        # self.toolButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.edt_list[cuetypectlidx].setMenu(self.toolmenu)
        self.edt_list[cuetypectlidx].setPopupMode(QtWidgets.QToolButton.InstantPopup)
        #self.plainTextEditAct.textChanged.connect(self.setChangeFlag)

    def accept(self):
        self.changeflag = True
        thing = []
        type_str = ''
        for i in range(1, cue_fields.__len__()):  # skip cue_fields[0], it's the cue index
            if cue_fields[i] == 'Cue_Type':
                action_list = self.toolmenu.actions()
                for i in range(action_list.__len__()):
                    if action_list[i].isChecked():
                        if type_str == '':
                            type_str = action_list[i].text()
                        else:
                            type_str = '{0},{1}'.format(type_str, action_list[i].text())
                self.chglist.append(type_str)
            else:
                self.chglist.append(self.edt_list[i].toPlainText())
        super(EditCue, self).accept()

    def reject(self):
        self.changeflag = False
        super(EditCue, self).reject()

    def getchange(self):
        return self.chglist

    def fillfields(self, cueindex, cue_list):
        working_cue_list = list(cue_list)  # create a working copy of cue_list
        working_cue_list.insert(0, '{0:03}'.format(cueindex))
        for i in range(cue_fields.__len__()):
            if cue_fields[i] == 'Cue_Type':
                action_list = self.toolmenu.actions()
                for anum in range(action_list.__len__()):
                    action_list[anum].setChecked(False)
                type_list = working_cue_list[i].split(',')
                for type in type_list:
                    for anum in range(action_list.__len__()):
                        if action_list[anum].text() == type:
                            action_list[anum].setChecked(True)
                            break
            else:
                self.edt_list[i].setPlainText(working_cue_list[i])

    def setROcueelements(self, RO_list):
        for i in range(cue_fields.__len__()):
            if cue_fields[i] in RO_list:
                self.edt_list[i].setReadOnly(True)
                self.edt_list[i].setToolTip('{0} (read only)'.format(cue_subelements_tooltips[i]))

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


class CueDlg(QtWidgets.QMainWindow, Ui_MainWindow):

    CueFileUpdate_sig = pyqtSignal()
    def __init__(self, parent=None):
        super(CueDlg, self).__init__(parent)
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        self.cfg = None
        self.load_cfg()
        self.The_Show = None
        self.load_show()

        self.externalchangestate = 'None'
        self.CommAddress_dict = {}
        self.CueAppDev = CommAddresses(self.The_Show.show_conf.equipment['program']['CueEngine']['IP_address'],
                                       int(self.The_Show.show_conf.equipment['program']['CueEngine']['port']))
        self.CommAddress_dict['CueEngine'] = self.CueAppDev
        logging.info('CueEngine receives from IP: {} PORT: {}'.format(self.CueAppDev.IP, self.CueAppDev.PORT))

        self.ShowMixerAppDev = CommAddresses(self.The_Show.show_conf.equipment['program']['ShowMixer']['IP_address'],
                                       int(self.The_Show.show_conf.equipment['program']['ShowMixer']['port']))
        self.CommAddress_dict['ShowMixer'] = self.ShowMixerAppDev
        logging.info('ShowMixer commands will be sent to IP: {} PORT: {}'.format(self.ShowMixerAppDev.IP,
                                                                                 self.ShowMixerAppDev.PORT))

        self.SFXAppDev = CommAddresses(self.The_Show.show_conf.equipment['program']['sound_effects']['IP_address'],
                                       int(self.The_Show.show_conf.equipment['program']['sound_effects']['port']))
        self.CommAddress_dict['SFXApp'] = self.SFXAppDev
        logging.info('sound_effects_player commands will be sent IP: {} PORT: {}'.format(self.SFXAppDev.IP,
                                                                                         self.SFXAppDev.PORT))

        self.MuteMapAppDev = CommAddresses(self.The_Show.show_conf.equipment['program']['MuteMap']['IP_address'],
                                      int(self.The_Show.show_conf.equipment['program']['MuteMap']['port']))
        self.CommAddress_dict['MuteMap'] = self.MuteMapAppDev
        logging.info('CueEngine response will be sent to IP: {} PORT: {}'.format(self.MuteMapAppDev.IP, self.MuteMapAppDev.PORT))



        self.setupUi(self)
        self.setWindowTitle('CueEngine - {}'.format(self.The_Show.show_conf.settings['title']))
        self.action_MuteMap = QtWidgets.QAction(self)
        self.action_MuteMap.setCheckable(True)
        self.action_MuteMap.setText('Show MuteMap')
        self.action_MuteMap.setToolTip('Launch the MuteMap application')
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/Res/MuteMap_base.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_MuteMap.setIcon(icon9)
        self.action_MuteMap.triggered.connect(self.show_MuteMap)
        self.menu_Application.addAction(self.action_MuteMap)
        self.LED_ext_cue_change = LED()
        self.LED_ext_cue_change.setMaximumSize(QtCore.QSize(32, 32))
        self.LED_ext_cue_change.setFixedSize((QtCore.QSize(32,32)))
        self.LED_ext_cue_change.setObjectName("extCueChanged")

        self.horizontalLayout.insertWidget(4,self.LED_ext_cue_change)
        self.update()

        self.goButton.setShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_G))

        # Setup multiple sound player apps
        self.action_Sound_FX2 = QtWidgets.QAction(self)
        self.action_Sound_FX2.setCheckable(True)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/Res/SoundFXApp_pressed.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon7.addPixmap(QtGui.QPixmap(":/Res/SoundFXApp.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Sound_FX2.setIcon(icon7)
        self.action_Sound_FX2.setObjectName("action_Sound_FX2")
        self.action_Sound_FX2.setToolTip('Show/hide LISP')
        self.menu_Application.addAction(self.action_Sound_FX2)
        self.toolBarApps.addAction(self.action_Sound_FX2)
        self.update()

        self.goButton.clicked.connect(self.on_buttonGo_clicked)
        self.goButton.setToolTip('Execute highlighted cue.')
        self.prevButton.clicked.connect(self.on_buttonPrev_clicked)
        self.prevButton.setToolTip('Execute condition before before highlighted cue.')
        self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        self.jumpButton.setToolTip('Execute the selected cue.')
        self.tableView.doubleClicked.connect(self.on_table_dblclick)
        self.tableView.clicked.connect(self.on_table_click)
        self.tableView.setContextMenuPolicy(Qt.ActionsContextMenu)

        # set up right click actions for tableView
        self.action_list = ['Edit','Insert', 'Add', 'Delete']  # actions that can be triggered by right click on table
        # add "Edit" action to the tableView
        self.editAction = QAction("Edit", None)
        self.editAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.editAction)
        # add "Insert" action to the tableView
        self.insertAction = QAction("Insert", None)
        self.insertAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.insertAction)
        # add "Add" action to the tableView
        self.AddAction = QAction("Add", None)
        self.AddAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.AddAction)
        # add "Delete" action to the tableView
        self.DeleteAction = QAction("Delete", None)
        self.DeleteAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.DeleteAction)
        self.ExternalEditStarted = False
        self.ExternalEditComplete = False
        self.CueFileUpdate_sig.connect(self.ExternalCueUpdate)

        self.tabledata = []
        self.actionOpen_Show.triggered.connect(self.openShow)
        self.actionSave.triggered.connect(self.saveShow)
        # start with all cue types visible
        self.CueTypeVisible = {}
        for type in cue_types:
            self.CueTypeVisible[type] = True
        # action_list = self.toolBar.actions()  # left here to show how to get iterable list of actions.
        self.action_Stage_Cues.triggered.connect(self.hide_show_cues)
        self.action_Stage_Cues.cuetype = 'Stage'
        self.action_Sound_FX_Cues.triggered.connect(self.hide_show_cues)
        self.action_Sound_FX_Cues.cuetype = 'Sound'
        self.action_Mixer_Cues.triggered.connect(self.hide_show_cues)
        self.action_Mixer_Cues.cuetype = 'Mixer'
        self.action_Lighting_Cues.triggered.connect(self.hide_show_cues)
        self.action_Lighting_Cues.cuetype = 'Light'
        # connect callbacks for launching external apps
        self.action_Sound_FX.triggered.connect(self.ShowSFXApp)
        self.action_Sound_FX2.triggered.connect(self.ShowLISP)
        self.action_Mixer.triggered.connect(self.ShowMxrApp)

        # initiallize SFX player objects
        self.SFXAppProc = None
        self.SFXApp_pid = None
        self.SFX_sock = None
        self.SFX_sndrthread = None

        # initialize SFX2 player objects
        self.LISPAppProc = None
        self.LISPApp_pid = None
        self.LISP_sndrthread = None
        self.midinoteoffset = 60
        self.portlist = []

        # initialize mixer app objects
        self.MxrAppProc = None
        self.MxrApp_pid = None
        self.MuteMapAppProc = None
        self.MuteMapApp_pid = None
        self.mxr_sock = None
        self.mxr_sndrthread = None

        self.dispatch = {'Stage':self.do_stage,
                         'Mixer':self.do_mixer,
                         'Sound':self.do_LISP,
                         'SFX':self.do_soundFX,
                         'Light':self.do_light}
        self.comm_threads = []  # a list of threads in use for later use when app exits
        self.sender_threads = []
        self.receiver_threads = []
        # setup receiver thread for inbound messages from slave apps, etc.
        try:
            self.rcvr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            #print('Failed to create message receiver socket')
            logging.info('CueDlg.__init__: Failed to create message receiver socket')
        # self.rcvr_sock.bind((INMSG_IP, INMSG_PORT))
        self.rcvr_sock.bind((self.CueAppDev.IP, self.CueAppDev.PORT))
        self.rcvrthread = CommHandlers.cmd_receiver(self.rcvr_sock)
        self.rcvrthread.setObjectName('CueEngine')
        self.rcvrthread.cmd_rcvrsignaled.connect(self.rcvrmessage)  # connect to custom signal called 'signal'
        self.rcvrthread.finished.connect(self.rcvrthreaddone)  # conect to buitlin signal 'finished'
        self.rcvrthread.start()  # start the thread
        self.comm_threads.append(self.rcvrthread)
        self.receiver_threads.append(self.rcvrthread)

    def load_cfg(self):
        self.cfg = configuration()

    def load_show(self):
        self.The_Show = Show(self.cfg.cfgdict)


    def on_buttonGo_clicked(self):
        """Execute the currently highlighted cue (current)"""
        tblvw = self.findChild(QtWidgets.QTableView)
        selections = tblvw.selectedIndexes()  # selections is a list that contains an entry for each column in the row
        tblrow = selections[0].row()  # the row is the index to the tabledata for the cue
        #tblrow += 1  # next row
        cuedata = self.tabledata[tblrow]  # data for this row
        cueindex = int(self.tabledata[tblrow][0])
        self.The_Show.cues.currentcueindex = cueindex  # new current cue index is the cue we want to execute
        self.dispatch_cue()  # execute the cue
        self.The_Show.cues.previouscueindex = self.The_Show.cues.currentcueindex  # save this as the previous cue index
        self.The_Show.cues.currentcueindex += 1
        tblvw.selectRow(self.The_Show.cues.currentcueindex)

    def on_buttonPrev_clicked(self):
        logging.info('In on_buttonPrev_clicked')
        if self.The_Show.cues.currentcueindex >= 2:
            before_target_index = self.The_Show.cues.currentcueindex - 2  # execute the cue before the target cue
            target_index = self.The_Show.cues.currentcueindex - 1
            #self.The_Show.cues.currentcueindex -= 1  # target cue becomes current
            #self.The_Show.cues.setcurrentcuestate(self.The_Show.cues.currentcueindex)
        else:
            before_target_index = 0
            target_index = 0
            #self.The_Show.cues.currentcueindex = 0
            logging.info('Cue before target: ' + str(before_target_index) + '   Target cue: ' + str(target_index))

        if before_target_index == 0 and target_index == 0:
            self.The_Show.cues.currentcueindex = target_index
            self.dispatch_cue()
        else:  # temporarily set currentcueindex to before target and execute that cue
            self.The_Show.cues.currentcueindex = before_target_index
            self.dispatch_cue()
            self.The_Show.cues.currentcueindex = target_index
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(self.The_Show.cues.currentcueindex)

    def on_buttonJump_clicked(self):
        """Execute the highlighted cue"""
        logging.info('In on_buttonJump_clicked.')
        #self.The_Show.cues.previouscueindex = self.The_Show.cues.currentcueindex  #todo previouscue index should be depricated
        if self.The_Show.cues.selectedcueindex is not None:
            self.The_Show.cues.currentcueindex = self.The_Show.cues.selectedcueindex
            self.The_Show.cues.selectedcueindex = None
        else:
            tblvw = self.findChild(QtWidgets.QTableView)
            index = tblvw.selectedIndexes()[0]
            self.The_Show.cues.currentcueindex = index.row()
        self.dispatch_cue()
        self.The_Show.cues.currentcueindex += 1
        self.tableView.selectRow(self.The_Show.cues.currentcueindex)


    def dispatch_cue(self):
        mutemap_msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
        mutemap_msg.add_arg(self.The_Show.cues.currentcueindex)
        mutemap_msg = mutemap_msg.build()

        # MuteMap messages get sent as long as the mixer sender thread has been started
        try:
            self.mxr_sndrthread.queue_msg(mutemap_msg, self.MuteMapAppDev)
        except AttributeError as e:
            logging.error(e)
            self.NotifyNoSlaveApp('MuteMap')

        # dispatch all types in the type list.
        # Note: this makes ShoeMixer appear to not change when types doesn't include mixer
        for type in self.The_Show.cues.getcuetype(self.The_Show.cues.currentcueindex):
            self.dispatch[type]()

    def do_stage(self):
        pass

    def do_mixer(self):
        cue_uuid = self.The_Show.cues.getcurrentcueuuid(self.The_Show.cues.currentcueindex)
        msg = osc_message_builder.OscMessageBuilder(address='/cue/uuid')
        # msg.add_arg(self.The_Show.cues.currentcueindex)
        msg.add_arg(cue_uuid)
        msg = msg.build()
        try:
            self.mxr_sndrthread.queue_msg(msg, self.ShowMixerAppDev)
        except AttributeError as e:
            logging.error('do_mixer:{}'.format(e))
            self.NotifyNoSlaveApp('mixer')

    def do_LISP(self):
        index = self.The_Show.cues.currentcueindex
        note = self.midinoteoffset + index
        msg = [NOTE_ON, note, 112]
        if self.LISPAppProc != None:
            self.LISP_sndrthread.queue_msg(msg, None)  # todo - mac 2nd arg might blowup...

    def do_soundFX(self):
#        if self.SFXAppProc != None:
        cue_uuid = self.The_Show.cues.getcurrentcueuuid(self.The_Show.cues.currentcueindex)
        msg = osc_message_builder.OscMessageBuilder(address='/cue/uuid')
        # msg.add_arg(self.The_Show.cues.currentcueindex)
        msg.add_arg(cue_uuid)
        msg = msg.build()
        try:
            self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
        except AttributeError as e:
            logging.error('do_soundFX:{}'.format(e))
            self.NotifyNoSlaveApp('soundFX')
        pass

    def do_light(self):
        pass

    def on_table_rightclick(self):
        # if external change in progress, return
        if self.ExternalEditStarted and not self.ExternalEditComplete:
            self.NotifyEditInProgress()
            return
        # post edit started to external apps
        """insert a new cue before the selected row"""
        # save the old state of the cuefile with a revision number appended
        # todo - mac this is hardwired to project cue file
        self.The_Show.cues.savecuelist(True,
                                  cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])

        sender_text = self.sender().text()
        if sender_text == 'Edit':
            self.cue_edit()
        elif sender_text == 'Insert':
            self.cue_insert()
        elif sender_text == 'Add':
            self.cue_add()
        elif sender_text == 'Delete':
            self.cue_delete()

    def cue_add(self):
        self.notify_slaves_edit_start()
        tblvw = self.findChild(QtWidgets.QTableView)
        lastcueviewed = self.The_Show.cues.currentcueindex
        oldlastcue = self.The_Show.cues.getcuelist(self.The_Show.cues.cuecount-1)  # get the last cues data
        cueindex = self.The_Show.cues.cuecount
        self.editcuedlg = EditCue(cueindex)
        self.editcuedlg.setWindowTitle(_translate("dlgEditCue", "Add Cue"))
        #self.editcuedlg.setROcueelements(['Cue_Number', 'Mutes', 'Entrances', 'Exits', 'Levels', 'On_Stage'])
        self.editcuedlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        self.editcuedlg.fillfields(cueindex, oldlastcue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            self.The_Show.cues.addnewcue(chg_list)
            # save the new version of cue file, overwriting old version
            # todo - mac this is hardwired to project cue file
            self.The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
            # display the new state of the cuefile
            self.The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
            self.The_Show.cues.currentcueindex = cueindex
        else:
            self.The_Show.cues.currentcueindex = lastcueviewed
        self.disptext()
        tblvw.selectRow(self.The_Show.cues.currentcueindex)
        if self.editcuedlg.changeflag: tblvw.scrollToBottom()
        self.notify_slaves_edit_complete()

    def cue_insert(self):
        self.notify_slaves_edit_start()
        tblvw = self.findChild(QtWidgets.QTableView)
        index = tblvw.selectedIndexes()
        cueindex = int(self.tabledata[index[0].row()][0])
        self.editcuedlg = EditCue(cueindex)
        self.editcuedlg.setWindowTitle(_translate("dlgEditCue", "Insert Cue"))
        self.editcuedlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        thiscue = self.The_Show.cues.getcuelist(cueindex)
        self.editcuedlg.fillfields(cueindex, thiscue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            self.The_Show.cues.insertcue(cueindex, chg_list)
            # save the new version of cue file, overwriting old version
            # todo - mac hardwired to to second cue file
            self.The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
            # display the new state of the cuefile
            self.The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
        self.The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(self.The_Show.cues.currentcueindex)
        self.notify_slaves_edit_complete()

    def cue_edit(self):
        self.notify_slaves_edit_start()
        tblvw = self.findChild(QtWidgets.QTableView)
        index = tblvw.selectedIndexes()
        cueindex = int(self.tabledata[index[0].row()][0])
        self.editcuedlg = EditCue(cueindex)
        self.editcuedlg.setWindowTitle(_translate("dlgEditCue", "Edit Cue"))
        self.editcuedlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        thiscue = self.The_Show.cues.getcuelist(cueindex)
        self.editcuedlg.fillfields(cueindex, thiscue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            self.The_Show.cues.updatecue(cueindex, chg_list)
            # save the new version of cue file, overwriting old version
            # todo - mac this is hardwired to project cue file
            self.The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
            # display the new state of the cuefile
            self.The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + '/'  + self.The_Show.show_conf.settings['cues']['href1'])
        self.The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(self.The_Show.cues.currentcueindex)
        self.notify_slaves_edit_complete(self.editcuedlg.changeflag)

    def cue_delete(self):
        self.notify_slaves_edit_start()
        tblvw = self.findChild(QtWidgets.QTableView)
        # index[0].row() will be where the user clicked
        index = tblvw.selectedIndexes()
        cueindex = int(self.tabledata[index[0].row()][0])
        self.The_Show.cues.deletecue(cueindex)
        # save the new version of cue file, overwriting old version
        # todo - mac this is hardwired to project cue file
        self.The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + '/' + self.The_Show.show_conf.settings['cues']['href1'])
        # display the new state of the cuefile
        self.The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + '/'  + self.The_Show.show_conf.settings['cues']['href1'])
        self.The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(self.The_Show.cues.currentcueindex)
        self.notify_slaves_edit_complete()


    def NotifyEditInProgress(self):
        QMessageBox.information(self,'Cue Modification','Cue modification blocked, external edit in progress.', QMessageBox.Ok)

    def NotifyReloadBeforeEdit(self):
        QMessageBox.information(self,'Cue Modification','Cues reloaded.', QMessageBox.Ok)

    def NotifyNoSlaveApp(self, name):
        QMessageBox.warning(self,'Slave Comm Failure','Slave App {} not active.'.format(name), QMessageBox.Ok)


    def on_table_click(self,index):
        """Set a selected cue
        simply sets the selected row of the table/cue list
        Doesn't get executed, jump button executes the selected cue.
        index is the row in the tableview (thus the row of the tabledata)"""
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(index.row())
        # cuedata = self.tabledata[index.row()]
        self.The_Show.cues.selectedcueindex = int(self.tabledata[index.row()][0])

    def on_table_dblclick(self,index):
        """Edit the double clicked cue"""
        # if external change in progress, return
        if self.ExternalEditStarted and not self.ExternalEditComplete:
            self.NotifyEditInProgress()
            return
        # determine the cue index from the first column of the table data
        tblvw = self.findChild(QtWidgets.QTableView)
        cueindex = int(self.tabledata[index.row()][0])
        # cueindex = index.row()
        self.editcuedlg = EditCue(cueindex)  # create the edit dialog
        # self.editcuedlg.editidx = cueindex
        self.editcuedlg.setROcueelements(['Cue_Number', 'Entrances', 'Exits', 'Levels', 'On_Stage'])
        thiscue = self.The_Show.cues.getcuelist(cueindex)
        self.editcuedlg.fillfields(cueindex, thiscue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            for col in range(header.__len__()):
                changeddataindex = cue_subelements.index(header[col].replace(' ', '_'))
                self.tabledata[cueindex][col] = chg_list[changeddataindex]
            self.The_Show.cues.updatecue(cueindex, chg_list)
            # todo - mac hardwired to second cue file
            self.The_Show.cues.savecuelist(True, cfg.cfgdict['configuration']['project']['folder'] + self.The_Show.show_conf.settings['cues']['href1'])
        self.The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(self.The_Show.cues.currentcueindex)

    def setfirstcue(self, index=0):
        if index == 0:
            self.The_Show.cues.previouscueindex = 0
        else:
            self.The_Show.cues.previouscueindex = index -1
        self.The_Show.cues.currentcueindex = index
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(self.The_Show.cues.currentcueindex)

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()

    def get_table_data(self):
        self.tabledata = []
        for index in range(0, self.The_Show.cues.cuecount):
            cuenum = '{0:03}'.format(index)
            q = self.The_Show.cues.cuelist.find(".cues/cue[@num='"+cuenum+"']")
            type_list = q.find('CueType').text.split(',')
            for type in cue_types:
                if type in type_list and self.CueTypeVisible[type]:
                    self.append_table_data(q)
                    break
        return

    def append_table_data(self, q):
        tmp_list = ['{0:03}'.format(int(q.attrib['num']))]
        for i in range(1, header.__len__()):
            dirty_data = q.find(header[i].replace(' ','')).text
            try:
                clean_data = dirty_data.strip()
                tmp_list.append(clean_data)
            except AttributeError:
                tmp_list.append('')
        self.tabledata.append(tmp_list)

    #Menu and Tool Bar functions

    def openShow(self):
        '''
        Present file dialog to select new ShowConf.xml file
        :return:
        '''
        fileNames = []
        fdlg = QtWidgets.QFileDialog()
        fdlg.setFilter(QDir.Hidden | QDir.Dirs | QDir.Files)
        fdlg.setFileMode(QFileDialog.ExistingFile)
        fdlg.setNameFilters(["Project files (*.xml)"])
        fdlg.setDirectory(self.The_Show.show_confpath)
        proxymodel = FileFilterProxyModel(fdlg)
        proxymodel.setFilterRegExp(QRegExp("_project", Qt.CaseInsensitive, QRegExp.FixedString))
        fdlg.setProxyModel(proxymodel)

        if fdlg.exec():
            fileNames = fdlg.selectedFiles()
        fdlg.close()
        if len(fileNames) != 0:
            logging.info('Files selected in openProjectFolder: {}'.format(fileNames))
            self.conffile = fileNames[0]
            openproj = os.path.split(self.conffile)
            self.cfg.cfgdict['configuration']['project']['folder'] = openproj[0]
            self.cfg.cfgdict['configuration']['project']['file'] = openproj[1]
            newcfg_doc = self.cfg.updateFromDict()
            self.cfg.write(newcfg_doc, True, CFG_PATH)
            self.load_cfg()
            self.load_show()
            self.char_data = []
        print('File>Open: {0}'.format(fileNames))

    def saveShow(self):
        print("Save show.")
        pass

    def hide_show_cues(self):
        """Toggle visibility of stage cues"""
        who = self.sender()
        cuetype = who.cuetype
        if self.CueTypeVisible[cuetype]:
            self.CueTypeVisible[cuetype] = False
        else:
            self.CueTypeVisible[cuetype] = True
        self.disptext()
        self.setfirstcue()

    # launch sound_effects_player
    def ShowSFXApp(self):
        sender_action = self.sender()
        if sender_action.isChecked():

            for process in psutil.process_iter():
                #print(process.pid)
                try:
                    if 'run_sound_effects_player.sh' in process.cmdline()[1]:
                        self.SFXApp_pid = process.pid
                        #print('SFX player pid:{}'.format(self.SFXp_pid))
                        logging.info('SFX player pid:{}'.format(self.SFX_pid))
                        break
                except IndexError:
                    self.SFX_pid = None
            if self.SFXApp_pid is None:
                logging.info('SFX player not found, attempting to launch')
                #print("Launch SFX player.")
                # self.SFXAppProc = subprocess.Popen(['python3', '/home/mac/SharedData/PycharmProjs/ShowControl/ShowMixer/ShowMixer.py'])
                SFX_shell = cfg.cfgdict['configuration']['project']['folder'] + '/' + 'run_sound_effects_player.sh'
                self.SFXAppProc = subprocess.Popen([SFX_shell])
                if self.SFXAppProc is not None:
                    self.SFXApp_pid = self.SFXAppProc.pid
                    logging.info('SFX player launch success, pid: {}'.format(self.SFXApp_pid))
        else:
            # stop SFX player
            logging.info('SFX player shutdown requested.')
            # if we have a sender thread attempt to tell ShowMixer to quit
            try:  # if SFXAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.SFXApp_pid is not None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg = msg.build()
                    self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
                    sleep(2)  # wait for message to be sent
            except:
                raise

        if self.SFX_sock is None:

            try:
                self.SFX_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                #print('Failed to create SFX socket')
                logging.info('ShowSFXApp: Failed to create SFX socket')
                sys.exit()
            self.SFX_sndrthread = CommHandlers.sender(self.SFX_sock)
            self.SFX_sndrthread.setObjectName('SFXApp')
            self.SFX_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
            self.SFX_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
            self.SFX_sndrthread.start()  # start the thread
            self.comm_threads.append(self.SFX_sndrthread)
            self.sender_threads.append(self.SFX_sndrthread)

    def EndSFXApp(self):
        self.SFXAppProc.terminate()

    def ShowMxrApp(self):
        sender_action = self.sender()
        if sender_action.isChecked():

            for process in psutil.process_iter():
                #print(process.pid)
                try:
                    if 'ShowMixer.py' in process.cmdline()[1]:
                        self.MxrApp_pid = process.pid
                        #print('ShowMixer pid:{}'.format(self.MxrApp_pid))
                        logging.info('ShowMixer pid:{}'.format(self.MxrApp_pid))
                        break
                except IndexError:
                    self.MxrApp_pid = None
            if self.MxrApp_pid is None:
                logging.info('ShowMixer not found, attempting to launch')
                #print('ShowMixer not found, attempting to launch')
                # self.MxrAppProc = subprocess.Popen(
                #     ['python3', parentdir + '/ShowMixer/ShowMixer.py'])
                self.MxrAppProc = subprocess.Popen(
                    ['python3', parentdir + '/show-mixer.py'])
                logging.info('Starting ShowMixer')
                logging.info(parentdir + '/show-mixer.py')
                if self.MxrAppProc is not None:
                    self.MxrApp_pid = self.MxrAppProc.pid
                    logging.info('ShowMixer launch success, pid: {}'.format(self.MxrApp_pid))
        else:
            # stop ShowMixer
            logging.info('ShowMixer shutdown requested.')
            # if we have a sender thread attempt to tell ShowMixer to quit
            try:  # if MxrAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.MxrApp_pid is not None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg, self.ShowMixerAppDev)
                    sleep(2)  # wait for message to be sent
            except:
                raise

        if self.mxr_sock is None:
            # setup mixer sender thread
            try:
                self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                #print('Failed to create mixer socket')
                logging.info('ShowMxrApp: Failed to create mixer socket')
                sys.exit()
            self.mxr_sndrthread = CommHandlers.sender(self.mxr_sock)
            self.mxr_sndrthread.setObjectName('ShowMixer')
            self.mxr_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
            self.mxr_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
            self.mxr_sndrthread.start()  # start the thread
            self.comm_threads.append(self.mxr_sndrthread)
            self.sender_threads.append(self.mxr_sndrthread)

    def show_MuteMap(self):
        sender_action = self.sender()
        if sender_action.isChecked():

            for process in psutil.process_iter():
                #print(process.pid)
                try:
                    if 'MuteMap.py' in process.cmdline()[1]:
                        self.MxrApp_pid = process.pid
                        #print('MuteMap pid:{}'.format(self.MuteMapApp_pid))
                        logging.info('MuteMAp pid:{}'.format(self.MuteMapApp_pid))
                        break
                except IndexError:
                    self.MuteMapApp_pid = None
            if self.MuteMapApp_pid is None:
                logging.info('MuteMap not found, attempting to launch')
                #print('MuteMap not found, attempting to launch')
                self.MuteMapAppProc = subprocess.Popen(
                    ['python3', parentdir + '/MuteMap/MuteMap.py'])
                if self.MuteMapAppProc is not None:
                    self.MuteMapApp_pid = self.MuteMapAppProc.pid
                    logging.info('MuteMap launch success, pid: {}'.format(self.MuteMapApp_pid))
        else:
            # stop MuteMap
            logging.info('ShowMixer shutdown requested.')
            # if we have a sender thread attempt to tell ShowMixer to quit
            try:  # if MuteMapAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.MuteMapApp_pid is not None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg, self.MuteMapAppDev)
                    sleep(2)  # wait for message to be sent
            except:
                raise

    def ShowLISP(self):
        sender_action = self.sender()
        if sender_action.isChecked():

            for process in psutil.process_iter():
                #print(process.pid)
                try:
                    if 'linux-show-player' in process.cmdline()[1]:
                        self.LISPApp_pid = process.pid
                        #print('LISP pid:{}'.format(self.LISPApp_pid))
                        logging.info('LISP pid:{}'.format(self.LISPApp_pid))
                        break
                except IndexError:
                    self.LISPApp_pid = None
            if self.LISPApp_pid is None:
                logging.info('LISP not found, attempting to launch')
                #print('LISP not found, attempting to launch')
                #self.The_Show.show_conf.equipment['program']['LISP']['app']
                self.LISPAppProc = subprocess.Popen(
                    ['python3', self.The_Show.show_conf.equipment['program']['LISP']['app'],
                     self.The_Show.show_conf.equipment['program']['LISP']['args'],
                     cfg.cfgdict['configuration']['project']['folder'] + '/'
                     + self.The_Show.show_conf.equipment['program']['LISP']['setup']])
                logging.info('Starting LISP')
                logging.info(self.The_Show.show_conf.equipment['program']['LISP']['app'])
                logging.info(self.The_Show.show_conf.equipment['program']['LISP']['args'])
                logging.info(cfg.cfgdict['configuration']['project']['folder'] + '/'
                     + self.The_Show.show_conf.equipment['program']['LISP']['setup'])
                if self.LISPAppProc is not None:
                    self.LISPApp_pid = self.LISPAppProc.pid
                    logging.info('LISP launch success, pid: {}'.format(self.LISPApp_pid))
        else:
            # stop LISP
            logging.info('LISP shutdown requested.')
            # if we have a sender thread attempt to tell ShowMixer to quit
            try:  # if LISPAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.LISPAppProc is not None:
                    self.LISPAppProc.terminate()
            except:
                #print('LISP process not running, could not close.')
                logging.info('LISP process not running, could not close.')

        if self.LISP_sndrthread is None:
            # assume LISP just launced, give it a chance to establish the midi port
            count = 0
            index = None
            while count < 10:
                self.portlist = self.getrtmidiports()
                for index, client in enumerate(self.portlist):
                    if 'RtMidi input' in client:
                        break
                count += 1
                sleep(0.5)
            if index:
                self.selidx = index
                if isinstance(self.portlist[self.selidx], str):
                    #print('ALSA port {} selected, client name: {}'.format(self.selidx, client))
                    logging.info(('ALSA port {} selected, client name: {}'.format(self.selidx, client)))
                    self.LISP_sndrthread = CommHandlers.AMIDIsender()
                    self.LISP_sndrthread.setObjectName('LISP')
                    partofname = self.portlist[self.selidx].split(':')
                    self.LISP_sndrthread.setport([partofname[0], self.portlist[self.selidx]])
                    self.LISP_sndrthread.amidi_sndrsignal.connect(
                        self.snd_sndrtestfunc)  # connect to custom signal called 'signal'
                    self.LISP_sndrthread.finished.connect(
                        self.snd_sndrthreaddone)  # connect to buitlin signal 'finished'
                    self.LISP_sndrthread.start()  # start the thread
                self.sender_threads.append(self.LISP_sndrthread)
            else:
                #print('RtMidi port not found')
                logging.error('RtMidi port not found!')

    # # saved for running LISP
    # def ShowLISP(self):
    #     print("Launch SFX App.")
    #     self.SFXAppProc = subprocess.Popen(['python3', '/home/mac/SharedData/PycharmProjs/linux-show-player/linux-show-player', '-f', '/home/mac/Shows/Pauline/sfx.lsp'])
    #     #self.SFXAppProc = subprocess.Popen(['/home/mac/PycharmProjs/ShowControl/sound_effects_player/try_player.sh'])
    #     #self.SFXAppProc = subprocess.Popen(['sound_effects_player'])
    #     # setup sound sender thread
    #     self.snd_sndrthread = CommHandlers.AMIDIsender()
    #     self.snd_sndrthread.setport(['RtMidiIn', 'RtMidiIn Client:RtMidi input'])
    #     self.snd_sndrthread.amidi_sndrsignal.connect(self.snd_sndrtestfunc)  # connect to custom signal called 'signal'
    #     self.snd_sndrthread.finished.connect(self.snd_sndrthreaddone)  # connect to buitlin signal 'finished'
    #     self.snd_sndrthread.start()  # start the thread
    #     self.comm_threads.append(self.snd_sndrthread)
    #
    def getrtmidiports(self):
        midiclass_ = rtmidi.MidiOut
        logging.info("Creating %s object.", midiclass_.__name__)

        api = get_api_from_environment(rtmidi.API_UNSPECIFIED)

        midiobj = midiclass_(api, None)
        type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "output"

        ports = midiobj.get_ports()
        midiobj = None
        return ports


    def closeEvent(self, event):
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            if self.SFXApp_pid is not None:
                msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                msg = msg.build()
                self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
                sleep(2)  # wait for message to be sent before killing threads
                # savereply = QMessageBox.warning(self, 'Warning',
                #    "Save changes in FX player before continuing!", QMessageBox.Ok, QMessageBox.Ok)
                self.EndSFXApp()
            try:  # if MxrAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.MxrApp_pid is not None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg, self.ShowMixerAppDev)
                    self.mxr_sndrthread.queue_msg(msg, self.MuteMapAppDev)
                    sleep(2)  # wait for message to be sent before killing threads
            except:
                raise
            try:
                if self.LISPApp_pid is not None:
                    self.LISPAppProc.terminate()
            except:
                raise
            self.stopthreads()
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)
        return reply

    def notify_slaves_edit_start(self):
        self.cuehaschanged = True
        msg = osc_message_builder.OscMessageBuilder(address='/cue/editstarted')
        msg.add_arg(True)
        msg = msg.build()
        for slave in self.sender_threads:
            # quick fix to handle LISP doesn't care if cue is edited todo mac fix this
            if slave.objectName() != 'LISP':
                slave.queue_msg(msg, self.CommAddress_dict[slave.objectName()])

    def notify_slaves_edit_complete(self, Changed=True):
        msg = osc_message_builder.OscMessageBuilder(address='/cue/editcomplete')
        msg.add_arg(True)  # Add True to indicate edit complete
        msg.add_arg(Changed)  # Add arg to indicate whetehr the user canceled the edit
        msg = msg.build()
        for slave in self.sender_threads:
            # quick fix to handle LISP doesn't care if cue is edited todo mac fix this
            if slave.objectName() != 'LISP':
                slave.queue_msg(msg, self.CommAddress_dict[slave.objectName()])


    '''gets called by main to tell the thread to stop'''
    def stopthreads(self):
        """..."""
        for t in self.comm_threads:
            t.setstopflag()
            t.wait(500)

    '''testfucn
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def sndrtestfunc(self, sigstr):
        """..."""
        print(sigstr)
        self.statusBar().showMessage(sigstr)

    def snd_sndrtestfunc(self, sigstr):
        """..."""
        logging.info('snd_sndrtestfunc: sigstr: {}'.format(sigstr))
        self.statusBar().showMessage(sigstr)

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def sndrthreaddone(self):
        """..."""
        logging.info('sndrthreaddone: sender thread done')

    def snd_sndrthreaddone(self):
        """..."""
        logging.info('snd_sndrthreaddone: sender thread done')

    '''receiver functions
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def rcvrmessage(self, sigstr):
        """..."""
        msg = osc_message.OscMessage(sigstr)
        logging.info('rcvrmessage: msg.address: {}'.format(msg.address))
        self.statusBar().showMessage('Address: {0}, Message: {1}'.format(msg.address, '{}'.format(msg.params)))
        if msg.address == '/cue/editstarted':
            if msg.params[0] == True:
                self.ExternalEditStarted = True
                self.LED_ext_cue_change.toggle(True)
        elif msg.address == '/cue/editcomplete':
            if msg.params[0] == True:
                self.ExternalEditComplete = True
                self.LED_ext_cue_change.toggle(False)
                self.CueFileUpdate_sig.emit()

    def ExternalCueUpdate(self):
        self.statusBar().showMessage('External Cue Update')
        last_index = self.The_Show.cues.currentcueindex
        self.The_Show.reloadShow(cfg.cfgdict)
        self.disptext()
        self.The_Show.cues.currentcueindex = last_index
        self.tableView.selectRow(self.The_Show.cues.currentcueindex)
        self.ExternalEditStarted = False
        self.ExternalEditComplete = False


    '''called when builtin signal 'finished' is emitted by worker thread'''
    def rcvrthreaddone(self):
        """..."""
        logging.info('rcvrthreaddone: receiver thread done')


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
        #if role == Qt.BackgroundColorRole:
        #    rowColor = Qt.blue
        #    self.setData(index, rowColor, Qt.BackgroundRole )
        pass         # not sure what to put here

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def sort(self, Ncol, order):
        """
        Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

class FileFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FileFilterProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, srcidx):
        model = self.sourceModel()
        index0 = model.index(source_row, 0, srcidx)
        index2 = model.index(source_row, 2, srcidx)
        str0_filenamerole = model.data(index0, QFileSystemModel.FileNameRole)
        str2_displayrole = model.data(index2, Qt.DisplayRole)
        indexofstring = self.filterRegExp().indexIn(str0_filenamerole)
        if (indexofstring >= 0 and str2_displayrole == 'xml File')\
                or (str2_displayrole in ('Folder', 'Drive')):
            return True
        else:
            return False



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename= LOG_DIR + '/CueEngine.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info('Begin')
    cfg = configuration()
    The_Show = Show(cfg.cfgdict)
    The_Show.displayShow()

    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = CueDlg(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui.resize(900,800)
    ui.disptext()
    ui.setfirstcue(1)  # slaves should execute cue 0 as the initialization
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    logging.info('Shutdown')

    sys.exit(app.exec_())