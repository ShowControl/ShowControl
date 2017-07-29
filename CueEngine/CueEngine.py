#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess
import types
import argparse
import socket
from time import sleep
from curses.ascii import isprint

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import xml.etree.ElementTree as ET
from os import path

import logging

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

from Show import Show
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

import CueEngine_ui
from CueEdit_alt_ui import Ui_dlgEditCue

from pythonosc import osc_message
from pythonosc import osc_message_builder

changeStates = {'started': False, 'completed': False}

class CommAddresses:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT

# CUE_IP = "127.0.0.1"
# CUE_PORT = 5005
INMSG_IP = "127.0.0.1"
INMSG_PORT = 5006

import styles

#cfgdict = cfg.toDict()

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
        msg.add_arg(The_Show.cues.currentcueindex)
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)

    def do_sound(self):
        msg = [NOTE_ON, 60, 112]
        self.snd_sndrthread.queue_msg(msg, self.CueAppDev)

    def do_SFX(self):
        msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
        msg.add_arg(The_Show.cues.currentcueindex)
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)
        pass

    def do_light(self):
        pass

class EditCue(QDialog, Ui_dlgEditCue):
    def __init__(self, index, parent=None):
        QDialog.__init__(self, parent)
        #super(object, self).__init__(self)
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
                print('In Cue_Type')
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

class CueDlg(QtWidgets.QMainWindow, CueEngine_ui.Ui_MainWindow):

    CueFileUpdate_sig = pyqtSignal()
    def __init__(self, cuelistfile, parent=None):
        super(CueDlg, self).__init__(parent)
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        self.externalchangestate = 'None'

        self.CueAppDev = CommAddresses(The_Show.show_conf.equipment['program']['CueEngine']['IP_address'],
                                       int(The_Show.show_conf.equipment['program']['CueEngine']['port']))
        logging.info('CueEngine receives from IP: {} PORT: {}'.format(self.CueAppDev.IP, self.CueAppDev.PORT))

        self.ShowMixerAppDev = CommAddresses(The_Show.show_conf.equipment['program']['ShowMixer']['IP_address'],
                                       int(The_Show.show_conf.equipment['program']['ShowMixer']['port']))
        logging.info('ShowMixer commands will be sent to IP: {} PORT: {}'.format(self.ShowMixerAppDev.IP,
                                                                                 self.ShowMixerAppDev.PORT))

        self.SFXAppDev = CommAddresses(The_Show.show_conf.equipment['program']['sound_effects']['IP_address'],
                                       int(The_Show.show_conf.equipment['program']['sound_effects']['port']))
        logging.info('sound_effects_player commands will be sent IP: {} PORT: {}'.format(self.SFXAppDev.IP,
                                                                                         self.SFXAppDev.PORT))

        self.setupUi(self)
        self.setWindowTitle(The_Show.show_conf.settings['title'])
        self.goButton.clicked.connect(self.on_buttonGo_clicked)
        self.prevButton.clicked.connect(self.on_buttonPrev_clicked)
        self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        self.tableView.doubleClicked.connect(self.on_table_dblclick)
        self.tableView.clicked.connect(self.on_table_click)

        self.tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.action_list = ['Insert', 'Add']
        self.insertAction = QAction("Insert", None)
        self.insertAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.insertAction)
        self.AddAction = QAction("Add", None)
        self.AddAction.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.AddAction)
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
        self.action_Mixer.triggered.connect(self.ShowMxrApp)
        self.SFXAppProc = None
        self.MxrAppProc = None
        self.dispatch = {'Stage':self.do_stage,
                         'Mixer':self.do_mixer,
                         'Sound':self.do_SFX,
                         'SFX':self.do_SFX,
                         'Light':self.do_light}

        self.comm_threads = []  # a list of threads in use for later use when app exits

        # setup receiver thread for inbound messages from slave apps, etc.
        try:
            self.rcvr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create message receiver socket')
        # self.rcvr_sock.bind((INMSG_IP, INMSG_PORT))
        self.rcvr_sock.bind((self.CueAppDev.IP, self.CueAppDev.PORT))
        self.rcvrthread = CommHandlers.cmd_receiver(self.rcvr_sock)
        self.rcvrthread.cmd_rcvrsignaled.connect(self.rcvrmessage)  # connect to custom signal called 'signal'
        self.rcvrthread.finished.connect(self.rcvrthreaddone)  # conect to buitlin signal 'finished'
        self.rcvrthread.start()  # start the thread
        self.comm_threads.append(self.rcvrthread)

    def on_buttonGo_clicked(self):
        """Execute the currently highlighted cue (current)"""
        print('Go')
        tblvw = self.findChild(QtWidgets.QTableView)
        selections = tblvw.selectedIndexes()  # selections is a list that contains an entry for each column in the row
        tblrow = selections[0].row()  # the row is the index to the tabledata for the cue
        #tblrow += 1  # next row
        cuedata = self.tabledata[tblrow]  # data for this row
        cueindex = int(self.tabledata[tblrow][0])
        The_Show.cues.currentcueindex = cueindex  # new current cue index is the cue we want to execute
        self.dispatch_cue()  # execute the cue
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex  # save this as the previous cue index
        tblvw.selectRow(tblrow + 1 )  # select the next row

    def on_buttonPrev_clicked(self):
        print('Prev')
        if The_Show.cues.currentcueindex > 0:
            previdx = The_Show.cues.currentcueindex
            The_Show.cues.currentcueindex -= 1
            print('Old index: ' + str(previdx) + '   New: ' + str(The_Show.cues.currentcueindex))
            The_Show.cues.setcurrentcuestate(The_Show.cues.currentcueindex)
        else:
            The_Show.cues.currentcueindex = 0
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
        self.dispatch_cue()

    def on_buttonJump_clicked(self):
        """Execute the highlighted cue"""
        print('Jump')
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
        The_Show.cues.currentcueindex = The_Show.cues.selectedcueindex
        self.dispatch_cue()

    def dispatch_cue(self):
        for type in The_Show.cues.getcuetype(The_Show.cues.currentcueindex):
            self.dispatch[type]()
            # if type in 'Mixer':
            #     msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
            #     msg.add_arg(The_Show.cues.currentcueindex)
            #     msg = msg.build()
            #     self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)
            # elif type == 'Sound':
            #     msg = [NOTE_ON, 60, 112]
            #     self.snd_sndrthread.queue_msg(msg, self.CueAppDev)


    def do_stage(self):
        pass

    def do_mixer(self):
        cue_uuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
        msg = osc_message_builder.OscMessageBuilder(address='/cue/uuid')
        # msg.add_arg(The_Show.cues.currentcueindex)
        msg.add_arg(cue_uuid)
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, self.ShowMixerAppDev)

    def do_sound(self):
        msg = [NOTE_ON, 60, 112]
        if self.SFXAppProc != None:
            self.snd_sndrthread.queue_msg(msg, None)  # todo - mac 2nd arg might blowup...

    def do_SFX(self):
        if self.SFXAppProc != None:
            cue_uuid = The_Show.cues.getcurrentcueuuid(The_Show.cues.currentcueindex)
            msg = osc_message_builder.OscMessageBuilder(address='/cue/uuid')
            # msg.add_arg(The_Show.cues.currentcueindex)
            msg.add_arg(cue_uuid)
            msg = msg.build()
            self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
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
        The_Show.cues.savecuelist(True,
                                  cfg.cfgdict['configuration']['project']['folder'] + '/' + The_Show.show_conf.settings['cues']['href1'])

        sender_text = self.sender().text()
        if sender_text == 'Insert':
            self.cue_insert()
        elif sender_text == 'Add':
            self.cue_add()

    def cue_add(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        oldlastcue = The_Show.cues.getcuelist(The_Show.cues.cuecount-1)  # get the last cues data
        cueindex = The_Show.cues.cuecount
        self.editcuedlg = EditCue(cueindex)
        self.editcuedlg.setWindowTitle(_translate("dlgEditCue", "Add Cue"))

        self.editcuedlg.setROcueelements(['Cue_Number','Entrances', 'Exits', 'Levels', 'On_Stage'])
        self.editcuedlg.fillfields(cueindex, oldlastcue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            The_Show.cues.addnewcue(chg_list)
            # save the new version of cue file, overwriting old version
            # todo - mac this is hardwired to project cue file
            The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + '/' + The_Show.show_conf.settings['cues']['href1'])
            # display the new state of the cuefile
            The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + '/'  + The_Show.show_conf.settings['cues']['href1'])
        The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(The_Show.cues.currentcueindex)

    def cue_insert(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        # index[0].row() will be where the user clicked
        index = tblvw.selectedIndexes()
        cueindex = int(self.tabledata[index[0].row()][0])
        self.editcuedlg = EditCue(cueindex)
        self.editcuedlg.setWindowTitle(_translate("dlgEditCue", "Edit Cue"))
        self.editcuedlg.setROcueelements(['Cue_Number','Entrances', 'Exits', 'Levels', 'On_Stage'])
        thiscue = The_Show.cues.getcuelist(cueindex)
        self.editcuedlg.fillfields(cueindex, thiscue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            The_Show.cues.insertcue(cueindex, chg_list)
            # save the new version of cue file, overwriting old version
            # todo - mac hardwired to to second cue file
            The_Show.cues.savecuelist(False, cfg.cfgdict['configuration']['project']['folder'] + The_Show.show_conf.settings['cues']['href1'])
            # display the new state of the cuefile
            The_Show.cues.setup_cues(cfg.cfgdict['configuration']['project']['folder'] + The_Show.show_conf.settings['cues']['href1'])
        The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(The_Show.cues.currentcueindex)

    def NotifyEditInProgress(self):
        QMessageBox.information(self,'Cue Modification','Cue modification blocked, external edit in progress.', QMessageBox.Ok)

    def NotifyReloadBeforeEdit(self):
        QMessageBox.information(self,'Cue Modification','Cues reloaded.', QMessageBox.Ok)

    def on_table_click(self,index):
        """Set a selected cue
        simply sets the selected row of the table/cue list
        Doesn't get executed, jump button executes the selected cue.
        index is the row in the tableview (thus the row of the tabledata)"""
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(index.row())
        # cuedata = self.tabledata[index.row()]
        The_Show.cues.selectedcueindex = int(self.tabledata[index.row()][0])

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
        thiscue = The_Show.cues.getcuelist(cueindex)
        self.editcuedlg.fillfields(cueindex, thiscue)
        self.editcuedlg.exec_()
        if self.editcuedlg.changeflag:
            chg_list = self.editcuedlg.getchange()
            for col in range(header.__len__()):
                changeddataindex = cue_subelements.index(header[col].replace(' ', '_'))
                self.tabledata[cueindex][col] = chg_list[changeddataindex]
            The_Show.cues.updatecue(cueindex, chg_list)
            # todo - mac hardwired to second cue file
            The_Show.cues.savecuelist(True, cfg.cfgdict['configuration']['project']['folder'] + The_Show.show_conf.settings['cues']['href1'])
        The_Show.cues.currentcueindex = cueindex
        self.disptext()
        tblvw.selectRow(The_Show.cues.currentcueindex)

    def setfirstcue(self, index=0):
        if index == 0:
            The_Show.cues.previouscueindex = 0
        else:
            The_Show.cues.previouscueindex = index -1
        The_Show.cues.currentcueindex = index
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()

    def get_table_data(self):
        qs = The_Show.cues.cuelist.findall('Cue')
        self.tabledata =[]
        for q in qs:
            dirty_list = q.find('CueType').text.split(',')
            type_list = [s.strip() for s in dirty_list]
            for type in cue_types:
                 if type in type_list and self.CueTypeVisible[type]:
                     self.append_table_data(q)
                     break
        # print(self.tabledata)

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
        fdlg = QtWidgets.QFileDialog()
        fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fdlg.close()

        print(fname[0])
        newprojectfolder, newprojfile = os.path.split(fname[0])
        cfg.cfgdict['configuration']['project']['folder'] = newprojectfolder
        cfg.cfgdict['configuration']['project']['file'] = newprojfile
        newtree = cfg.updateFromDict()
        cfg.write(newtree, False, CFG_PATH)
        cfg.reload()
        The_Show.loadNewShow(cfg.cfgdict)

        # self.stopthreads() todo - mac need to work through re-start of apps....
        # sleep(.5)

        self.setWindowTitle(The_Show.show_conf.settings['project']['title'])
        self.disptext()
        self.setfirstcue()
        # self.setWindowTitle(self.show_conf.settings('name'))

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
        if self.SFXAppProc != None:
            msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
            msg = msg.build()
            self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
            self.SFXAppProc = None
        else:
            logging.info('Launch SFX App.')

            print("Launch SFX App.")
            SFX_shell = cfg.cfgdict['configuration']['project']['folder'] + '/' + 'run_sound_effects_player.sh'
            self.SFXAppProc = subprocess.Popen([SFX_shell])
            #self.SFXAppProc = subprocess.Popen(['sound_effects_player'])
            # setup sound sender thread

            try:
                self.SFX_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print('Failed to create SFX socket')
                sys.exit()
            self.SFX_sndrthread = CommHandlers.sender(self.SFX_sock)
            self.SFX_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
            self.SFX_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
            self.SFX_sndrthread.start()  # start the thread
            self.comm_threads.append(self.SFX_sndrthread)

    def EndSFXApp(self):
        self.SFXAppProc.terminate()

    # # saved for running LISP
    # def ShowSFXApp(self):
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
    # def EndSFXApp(self):
    #     self.SFXAppProc.terminate()

    def ShowMxrApp(self):
        if self.MxrAppProc != None:
            msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
            #msg.add_arg(The_Show.cues.currentcueindex)
            msg = msg.build()
            self.mxr_sndrthread.queue_msg(msg, self.CueAppDev)
            self.MxrAppProc = None
        else:
            print("Launch Mxr App.")
            self.MxrAppProc = subprocess.Popen(['python3', '/home/mac/SharedData/PycharmProjs/ShowControl/ShowMixer/ShowMixer.py'])
            # setup mixer sender thread
            try:
                self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print('Failed to create mixer socket')
                sys.exit()
            self.mxr_sndrthread = CommHandlers.sender(self.mxr_sock)
            self.mxr_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
            self.mxr_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
            self.mxr_sndrthread.start()  # start the thread
            self.comm_threads.append(self.mxr_sndrthread)


    def closeEvent(self, event):
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            if self.SFXAppProc != None:
                msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                msg = msg.build()
                self.SFX_sndrthread.queue_msg(msg, self.SFXAppDev)
                sleep(2)  # wait for message to be sent before killing threads
                # savereply = QMessageBox.warning(self, 'Warning',
                #    "Save changes in FX player before continuing!", QMessageBox.Ok, QMessageBox.Ok)
                self.EndSFXApp()
            try:  # if MxrAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.MxrAppProc != None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg, self.ShowMixerAppDev)
                    sleep(2)  # wait for message to be sent before killing threads
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
        print(sigstr)
        self.statusBar().showMessage(sigstr)

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def sndrthreaddone(self):
        """..."""
        print('sender thread done')

    def snd_sndrthreaddone(self):
        """..."""
        print('sender thread done')

    '''receiver functions
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def rcvrmessage(self, sigstr):
        """..."""
        print('rcvrmessage')
        msg = osc_message.OscMessage(sigstr)
        print(msg.address)
        self.statusBar().showMessage('Address: {0}, Message: {1}'.format(msg.address, '{}'.format(msg.params)))
        if msg.address == '/cue/editstarted':
            if msg.params[0] == True:
                self.ExternalEditStarted = True
        elif msg.address == '/cue/editcomplete':
            if msg.params[0] == True:
                self.ExternalEditComplete = True
                self.CueFileUpdate_sig.emit()

    def ExternalCueUpdate(self):
        self.statusBar().showMessage('External Cue Update')
        The_Show.reloadShow(cfg.cfgdict)
        self.disptext()
        self.ExternalEditStarted = False
        self.ExternalEditComplete = False


    '''called when builtin signal 'finished' is emitted by worker thread'''
    def rcvrthreaddone(self):
        """..."""
        print('receiver thread done')


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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename='/home/mac/Shows/Fiddler/CueEngine.log', filemode='w',
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
    ui.resize(800,800)
    ui.disptext()
    ui.setfirstcue(1)  # slaves should execute cue 0 as the initialization
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    logging.info('Shutdown')

    sys.exit(app.exec_())