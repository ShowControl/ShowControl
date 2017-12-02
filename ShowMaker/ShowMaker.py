#!/usr/bin/env python3
__author__ = 'mac'

import argparse
import inspect
import os
import shutil
import time
import math
import socket
import sys
import re
from os import path
import uuid
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
from ShowControl.utils.Char import Char
from ShowControl.utils.Char import CreateChar
from ShowControl.utils.Actor import Actor
from ShowControl.utils.CueChar import CueChar
from ShowControl.utils.CueChar import CreateCueChar
from ShowControl.utils.ProjectXML import ProjectXML
from ShowControl.utils.Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields
from ShowControl.utils.Cues import CreateCue
from ShowControl.utils import styles
from ShowMixer.MixerConf import MixerConf
from ShowMixer.MixerMap import MixerCharMap

import ShowMaker_ui
import NewProject_dlg_ui
import CueEdit_ui

parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
# args = parser.parse_args()
#

_translate = QtCore.QCoreApplication.translate
module_logger.info('module log from ShowMaker.py')


class NewProject_dlg(QtWidgets.QDialog, NewProject_dlg_ui.Ui_NewProject):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def accept(self):
        super(NewProject_dlg, self).done(99)
        pass

    def reject(self):
        super(NewProject_dlg, self).reject()


class EditCue_dlg(QtWidgets.QDialog, CueEdit_ui.Ui_dlgEditCue):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.chgdict = {}
        self.chglist = []
        self.changeflag = False
        for cuetypectlidx in range(cue_subelements.__len__()):
            if cue_fields[cuetypectlidx] == 'Cue_Type':
                break
        self.edt_list[cuetypectlidx].setText('Select cue type/s ')
        self.toolmenu = QtWidgets.QMenu(self)
        for i in range(cue_types.__len__()):
            action = self.toolmenu.addAction(cue_types[i])
            action.setCheckable(True)
        self.edt_list[cuetypectlidx].setMenu(self.toolmenu)
        self.edt_list[cuetypectlidx].setPopupMode(QtWidgets.QToolButton.InstantPopup)

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

        super(EditCue_dlg, self).done(99)

    def getchange(self):
        return self.chglist

    def reject(self):
        self.changeflag = False
        super(EditCue_dlg, self).reject()

    def setROcueelements(self, RO_list):
        for i in range(cue_fields.__len__()):
            if cue_fields[i] in RO_list:
                self.edt_list[i].setReadOnly(True)
                self.edt_list[i].setToolTip('{0} (read only)'.format(cue_subelements_tooltips[i]))


class ShowMakerWin(QtWidgets.QMainWindow, ShowMaker_ui.Ui_MainWindow_showmaker):
    #enum
    char_table_enum, cast_table_enum, stage_table_enum = range(3)
    # char_table_enum, stage_table_enum = range(2)
    char_table_changed_sig = pyqtSignal(int)
    cast_table_changed_sig = pyqtSignal(int)
    stage_table_changed_sig = pyqtSignal(int)
    def __init__(self, parent=None):
        super(ShowMakerWin, self).__init__(parent)
        logging.info('in ShowMakerWin.__init__')
        self.setWindowTitle('MuteMap - {}'.format('Show Maker'))

        self.cfg = None
        self.load_cfg()
        self.The_Show = None
        self.load_show()
        self.stagestate_changed = False
        self.charstate_changed = False
        self.caststate_changed = False
        self.setupUi(self)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(screen.x() + int(0.05 * screen.width()), screen.y(), screen.width() * 0.98, screen.height() * 0.9)
        #self.move(40, 50)
        self.tablist = []
        self.tablistvertlayout = []
        # add the character tab
        self.tablist.append(QtWidgets.QWidget())
        self.tablist[ShowMakerWin.char_table_enum].setMinimumSize(QtCore.QSize(0, 400))
        self.tablist[ShowMakerWin.char_table_enum].setObjectName("Pg {}".format(ShowMakerWin.char_table_enum))
        # add a grid layout to the tab
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tablist[ShowMakerWin.char_table_enum])
        self.gridLayout_3.setObjectName("gridLayout_3")
        # create a vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        # create a tableview for the char tab
        tableView = QtWidgets.QTableView(self.tablist[ShowMakerWin.char_table_enum])
        tableView.setObjectName("table_char")
        tableView.setItemDelegateForColumn(3, CharTableDelegate(self))
        # tableView.setMinimumWidth(200)
        tableView.clicked.connect(self.on_table_click)
        tableView.doubleClicked.connect(self.on_table_dblclick)
        self.char_table_changed_sig.connect(self.char_list_changed_signal_handler)
        # set up actions for table right click context menu
        tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        # tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        # tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # set up right click actions for tableView
        self.action_list = ['Insert', 'Add', 'Delete']  # actions that can be triggered by right click on table
        # add "Insert" action to the tableView
        self.insertAction = QAction("Insert", None)
        self.insertAction.triggered.connect(self.on_char_table_rightclick)
        tableView.addAction(self.insertAction)
        # add "Add" action to the tableView
        self.AddAction = QAction("Add", None)
        self.AddAction.triggered.connect(self.on_char_table_rightclick)
        tableView.addAction(self.AddAction)
        # add "Delete" action to the tableView
        self.DeleteAction = QAction("Delete", None)
        self.DeleteAction.triggered.connect(self.on_char_table_rightclick)
        tableView.addAction(self.DeleteAction)

        self.char = None
        self.char_data = []
        self.char_header = []
        # add the tableview to the vertical layout
        self.verticalLayout.addWidget(tableView)
        # add the vertical layout to the grid
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.insertTab(ShowMakerWin.char_table_enum, self.tablist[ShowMakerWin.char_table_enum], 'Characters')

        # add the cast tab
        self.cast = None
        self.cast_data = []
        self.cast_header = []
        self.tablist.append(QtWidgets.QWidget())
        self.tablist[ShowMakerWin.cast_table_enum].setObjectName("Pg {}".format(ShowMakerWin.cast_table_enum))
        # create a gridlayout and add to the tab
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tablist[ShowMakerWin.cast_table_enum])
        self.gridLayout_4.setObjectName("gridLayout_4")
        # create a vertivcal layout
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        # create a tableview for the char tab
        tableView = QtWidgets.QTableView(self.tablist[ShowMakerWin.cast_table_enum])
        tableView.setObjectName("table_cast")
        # tableView.setMinimumWidth(200)
        tableView.clicked.connect(self.on_table_click)
        tableView.doubleClicked.connect(self.on_table_dblclick)
        self.cast_table_changed_sig.connect(self.cast_list_changed_signal_handler)
        # set up actions for table right click context menu
        tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        # add the tableview to the vertical layout
        self.verticalLayout_4.addWidget(tableView)
        # add the vertical layout to the grid
        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.tabWidget.insertTab(ShowMakerWin.cast_table_enum, self.tablist[ShowMakerWin.cast_table_enum], 'Cast')
        # set up actions for table right click context menu
        tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        # tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        # tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # set up right click actions for tableView
        self.cast_action_list = ['Insert', 'Add', 'Delete']  # actions that can be triggered by right click on table
        # add "Insert" action to the tableView
        self.cast_insertAction = QAction("Insert", None)
        self.cast_insertAction.triggered.connect(self.on_cast_table_rightclick)
        tableView.addAction(self.cast_insertAction)
        # add "Add" action to the tableView
        self.cast_AddAction = QAction("Add", None)
        self.cast_AddAction.triggered.connect(self.on_cast_table_rightclick)
        tableView.addAction(self.cast_AddAction)
        # add "Delete" action to the tableView
        self.cast_DeleteAction = QAction("Delete", None)
        self.cast_DeleteAction.triggered.connect(self.on_cast_table_rightclick)
        tableView.addAction(self.cast_DeleteAction)



        # add the stage state tab
        self.tablist.append(QtWidgets.QWidget())
        idx = 1
        self.tablist[ShowMakerWin.stage_table_enum].setObjectName("Pg {}".format(ShowMakerWin.stage_table_enum))
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tablist[ShowMakerWin.stage_table_enum])
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        # create a tableview for the Stage State
        tableView = StageTableView(self.tablist[ShowMakerWin.stage_table_enum])
        tableView.setObjectName("table_stage")
        tableView.doubleClicked.connect(self.on_stage_table_dblclick)
        self.stage_table_changed_sig.connect(self.stage_list_changed_signal_handler)
        tableView.horizontalHeader().setMinimumSectionSize(100)
        tableView.setContextMenuPolicy(Qt.ActionsContextMenu)

        # set up right click actions for tableView
        self.stage_action_list = ['Insert', 'Add', 'Delete', 'View/Edit Cue']  # actions that can be triggered by right click on table
        # add "Insert" action to the tableView
        self.stage_insertAction = QAction("Insert", None)
        self.stage_insertAction.triggered.connect(self.on_stage_table_rightclick)
        tableView.addAction(self.stage_insertAction)
        # add "Add" action to the tableView
        self.stage_AddAction = QAction("Add", None)
        self.stage_AddAction.triggered.connect(self.on_stage_table_rightclick)
        tableView.addAction(self.stage_AddAction)
        # add "Delete" action to the tableView
        self.stage_DeleteAction = QAction("Delete", None)
        self.stage_DeleteAction.triggered.connect(self.on_stage_table_rightclick)
        tableView.addAction(self.stage_DeleteAction)
        # add "Edit/View Cue" action to the tableView
        self.stage_EditCueAction = QAction("Edit/View Cue", None)
        self.stage_EditCueAction.triggered.connect(self.on_stage_table_rightclick)
        tableView.addAction(self.stage_EditCueAction)

        # the following two lines turn the text in the horizontal header vertical
        # but, the paint routine doesnt handle the newline
        # so until I get around to fixing that I commented them out
        # headerView = MyHeaderView()
        # tableView.setHorizontalHeader(headerView)
        self.stagestat_data = []
        self.stagestat_header = []
        self.verticalLayout_5.addWidget(tableView)
        self.gridLayout_5.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.tabWidget.insertTab(ShowMakerWin.stage_table_enum, self.tablist[ShowMakerWin.stage_table_enum], 'Stage State')
        self.load_project()
        self.pushButtonselectfolder.clicked.connect(self.select_new_path_clicked)

        self.action_Exit.triggered.connect(self.close)
        self.action_OpenProject.triggered.connect(self.openProjectFolder)
        self.action_NewProject.triggered.connect(self.new_project)

    def load_cfg(self):
        self.cfg = configuration()

    def load_show(self):
        self.The_Show = Show(self.cfg.cfgdict)

    def load_project(self):
        self.init_cast_data()
        castmodel = CastTableModel(self.cast_data, self.cast_header, self)
        cast_table = self.tablist[self.cast_table_enum].findChild(QtWidgets.QTableView, name='table_cast')
        cast_table.setModel(castmodel)
        cast_table.resizeColumnsToContents()
        cast_table.hideColumn(0)
        self.init_char_data()
        charmodel = CharTableModel(self.char_data, self.char_header, self)
        char_table = self.tablist[self.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        char_table.setModel(charmodel)
        # hide uuid columns
        for column in [0,2,4]:
            char_table.hideColumn(column)

        char_table.resizeColumnsToContents()
        char_table.selectRow(0)
        self.init_stagestat_data()
        stagemodel = StageTableModel(self.stagestat_data, self.stagestat_header, self)
        stage_table = self.tablist[self.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.setModel(stagemodel)
        stage_table.hideColumn(0)  # hide uuid column
        stage_table.resizeColumnsToContents()
        self.lineEdit_projectname.setText(self.The_Show.show_conf.settings['title'])
        self.lineEdit_projectcuefile.setText(self.The_Show.show_conf.settings['cues']['href1'])
        self.lineEdit_projectpath.setText(self.cfg.cfgdict['configuration']['project']['folder'])
        return

    def init_cast_data(self):
        self.cast_header = ['uuid', 'Actor', 'Understudy uuid', 'Understudy']
        self.actor = Actor()
        self.actor.setup_cast(self.The_Show.show_confpath + self.The_Show.show_conf.settings['actormap'])
        self.actor.actors_to_list_of_tuples()
        for actor in self.actor.actor_list:
            actor_uuid = actor[0]
            actor_name = actor[1]
            actor_understudy_uuid = actor[2]
            self.cast_data.append([actor_uuid, actor_name, actor_understudy_uuid])
        return

    def init_char_data(self):
        # self.char_header = ['uuid', 'Character', 'Actor uuid', 'Actor', 'Understudy uuid', 'Understudy']
        self.char_header = ['uuid', 'Character', 'Actor uuid', 'Actor']
        self.char = Char()
        self.char.setup_cast(self.The_Show.show_confpath + self.The_Show.show_conf.settings['charmap'])
        self.char.chars_to_list_of_tuples()
        #[(index, thing) for index, thing in enumerate(self.actor.actor_list) if thing[0] =='07940948-687f-4f37-bd9d-fc81e8dcf286']
        for chrnam in self.char.char_list:
            try:
                char = chrnam[1]
                print(char)
            except:
                print('no char')
            try:
                actor_uuid = chrnam[2]
                actor_item = [(actor_index, actor_tuple)
                              for actor_index, actor_tuple in enumerate(self.actor.actor_list)
                              if actor_tuple[0] == actor_uuid]
                # actor_item is a list that has one entry
                # that entry is a tuple with two elements
                # first element is the index of the actor
                # second entry is a tuple with 3 elements: actor uuid, actor name, understudy uuid or none
                if not actor_item:  # this kind of assumes the lack of any actors is ok, probably a new project
                    actor_uuid = 'none'
                    actor_name = 'none'
                else:
                    actor_uuid = actor_item[0][1][0]
                    actor_name = actor_item[0][1][1]  # [0] is the first item in the list,
                                                      # [1] is the actor item tuple
                                                      # [1] is the actor name in the actor item tuple
                # actor_understudy_uuid = actor_item[0][1][2]  # [2] is understudy uuid or none
                # if actor_understudy_uuid != 'none':  # assume it is a uuid
                #     understudy_item = [(actor_index, actor_tuple) for actor_index, actor_tuple in
                #                   enumerate(self.actor.actor_list) if
                #                   actor_tuple[0] == actor_understudy_uuid]
                #     understudy_name = understudy_item[0][1][1]
                # else:
                #     understudy_name = 'none'
            except:
                print('no actor')
            self.char_data.append([chrnam[0], char, actor_uuid, actor_name])
        return

    def init_stagestat_data(self):
        # this sets up th header data, one column for every character
        self.stagestat_header = ['uuid', 'Page', 'Act', 'Scene', 'Line']
        for chrnam in self.char.char_list:
            try:
                char = chrnam[1]
                print(char)
            except:
                print('no char')
            try:
                actor_uuid = chrnam[2]
                actor_item = [(actor_index, actor_tuple) for actor_index, actor_tuple in enumerate(self.actor.actor_list) if
                 actor_tuple[0] == actor_uuid]
                # actor_item is a list that has one entry
                # that entry is a tuple with two elements
                # first element is the index of the actor
                # second entry is a tuple with 3 elements: actor uuid, actor name, understudy uuid or none
                if not actor_item:
                    actor_uuid = 'none'
                    actor_name = 'none'
                    actor_understudy_uuid = 'none'
                else:
                    actor_uuid = actor_item[0][1][0]
                    actor_name = actor_item[0][1][1]  # [0] is the first item in the list,
                                                      # [1] is the actor item tuple
                                                      # [1] is the actor name in the actor item tuple
                    actor_understudy_uuid = actor_item[0][1][2]  # [2] is understudy uuid or none
                # todo mac: if actor_understudy is uuid, find understudy name from uuid
                # the understudy is an element of self.actor.actor_list, i.e. just another actor
                if actor_understudy_uuid != 'none':  # assume it is a uuid
                    understudy_item = [(actor_index, actor_tuple) for actor_index, actor_tuple in
                                  enumerate(self.actor.actor_list) if
                                  actor_tuple[0] == actor_understudy_uuid]
                    understudy_name = understudy_item[0][1][1]
                else:
                    understudy_name = 'none'
            except:
                print('no actor')
            self.stagestat_header.extend([char + '\n' + actor_name])
        print('In init_stagestat_data, length: {}'.format(len(self.stagestat_header)))
        # TODO -mac need to load cuechar, probably into The_Show...
        # each row will be a cue, so from *_cues.xml
        # will use num to get:
        # cue_uuid, cue_page, cue_act, cue_scene, cue_line for each cue
        allcues = self.The_Show.cues.cuelist.findall(".cues/cue")
        self.stagestat_data = []
        for q in allcues:
            cue_uuid = q.get('uuid')
            cue_num = q.get('num')
            # print('q num: {}, uuid: {}'.format(cue_num, cue_uuid))
            # fill in first columns
            cols = []
            cols.extend([cue_uuid])
            cols.extend([q.find(".Page").text])
            cols.extend([q.find(".Act").text])
            cols.extend([q.find(".Scene").text])
            cols.extend([q.find(".Id").text])
            # cols = list(range(1, 5))  # offset columns by header colmumns
            try:
                # get the character states for this cue
                cuechar_element = self.The_Show.cuechar.cuecharlist.find(".cues/cue[@uuid='"+ cue_uuid +"']")
                if cuechar_element is None: raise AttributeError
                for chr in self.char.char_list:
                    chr_state = cuechar_element.find(".char[@uuid='"+ chr[0] +"']")
                    stage_state = StageState.OffStage
                    onstage_state = chr_state.find('.onstage').text
                    if onstage_state == '1':
                        stage_state += StageState.OnStage
                    mute_state = chr_state.find('.mute').text
                    if mute_state == '1':
                        stage_state += StageState.MicOn
                    col_state = StageState(stage_state)
                    cols.extend([col_state])
                self.stagestat_data.append(cols)
            except AttributeError:
                logging.info("cue uuid: {} not found in cuechar xml")

        return

    def select_new_path_clicked(self):
        print('New path')

    def closeEvent(self, event):
        """..."""
        if self.charstate_changed or self.stagestate_changed or self.caststate_changed:
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to project?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                print('In closeEvent cast changed query.')
                self.save_char_list()
                self.charstate_changed = False
                self.save_cast_list()
                self.caststate_changed = False
                self.save_cuechar()
                self.stagestate_changed = False
                self.save_cues()
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        """..."""
        reply = QMessageBox.question(self, 'Confirm Quit',
                                     "Are you sure you want to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)
        return reply

    def save_char_list(self):
        # fields: 'uuid', 'Character', 'Actor uuid', 'Actor', 'Understudy uuid', 'Understudy'
        # move model data to list of tuples
        self.char.char_list = []
        for char in self.char_data:
            self.char.char_list.append((char[0], char[1], char[2]))
        # move new list of tuples to xml doc
        newchar_doc = self.char.chars_toxmldoc()
        # save new xml file
        self.char.write(newchar_doc, True, self.The_Show.show_confpath + self.The_Show.show_conf.settings['charmap'])

    def save_cast_list(self):
        # fields: 'uuid', 'Actor', 'Understudy uuid', 'Understudy'
        self.actor.actor_list = []
        for actor in self.cast_data:
            self.actor.actor_list.append((actor[0], actor[1], actor[2]))
        newactor_doc = self.actor.actors_toxmldoc()
        self.actor.write(newactor_doc, True, self.The_Show.show_confpath + self.The_Show.show_conf.settings['actormap'])
        return

    def save_cuechar(self):
        new_doc = self.The_Show.cuechar.cuecharlist.getroot()
        self.The_Show.cuechar.write(new_doc,
                                    True,
                                    self.The_Show.show_confpath + self.The_Show.show_conf.settings['cuechar'])

    def save_cues(self):
        self.The_Show.cues.savecuelist(True, self.The_Show.show_confpath + self.The_Show.show_conf.settings['cues']['href1'])
        return

    def openProjectFolder(self):
        fileNames = []
        fdlg = QtWidgets.QFileDialog()
        # fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        fdlg.setFilter(QDir.Hidden | QDir.Dirs | QDir.Files)
        fdlg.setFileMode(QFileDialog.ExistingFile)
        fdlg.setNameFilters(["Project files (*.xml)"])
        fdlg.setDirectory(self.The_Show.show_confpath)
        proxymodel = FileFilterProxyModel(fdlg)
        proxymodel.setFilterRegExp(QRegExp("_project", Qt.CaseInsensitive, QRegExp.FixedString))
        fdlg.setProxyModel(proxymodel)

        if fdlg.exec():
            fileNames = fdlg.selectedFiles()
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
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
            self.load_project()
        print('File>Open: {0}'.format(fileNames))

    def new_project(self):
        # get the path to the projects/shows folder
        shows_folder = os.path.dirname(os.path.dirname(self.The_Show.show_confpath))

        new_proj_dlg = NewProject_dlg()
        new_proj_dlg.lineEdit_HomeFolder.setText(shows_folder)
        retval = new_proj_dlg.exec()
        if retval:  # if retval then new project was defined
            project_name = new_proj_dlg.lineEdit_ProjectName.text()
            project_title = new_proj_dlg.lineEdit_ProjectTitle.text()
            project_venue = new_proj_dlg.lineEdit_ProjectVenue.text()
            if project_name == '' or project_title == '':
                QMessageBox.information(self.parent(), 'Invalid Project', 'Please fill all fields.',
                                        QMessageBox.Ok)
            else:  # build new project with specified info
                # TODO mac no white space in project name
                project_folder = os.path.join(shows_folder, project_name)
                if not os.path.exists(project_folder):
                    os.makedirs(project_folder)
                self.cfg.cfgdict['configuration']['project']['folder'] = os.path.join(shows_folder, project_name)
                self.cfg.cfgdict['configuration']['project']['file'] = project_name + '_project.xml'
                newcfg_doc = self.cfg.updateFromDict()
                self.cfg.write(newcfg_doc, True, CFG_PATH)
                self.load_cfg()
                self.lineEdit_projectname.setText(self.The_Show.show_conf.settings['title'])
                self.lineEdit_projectcuefile.setText(self.The_Show.show_conf.settings['cues']['href1'])
                self.lineEdit_projectpath.setText(self.cfg.cfgdict['configuration']['project']['folder'])

                # new project fle
                prjxml = ProjectXML()
                prjxml_doc = prjxml.toXMLdoc(project_title, project_name, project_venue)
                project_xml_path = os.path.join(project_folder, self.cfg.cfgdict['configuration']['project']['file'])
                prjxml.write(prjxml_doc, False, project_xml_path)
                prjxml = None
                # create empty project files

                # cue file with one dummy cue
                create_cues = CreateCue(os.path.join(project_folder, project_name + '_cues.xml'))
                first_cue_uuid = create_cues.get_first_uuid()
                # create a new _actor.xml file
                newactor = Actor()
                newactor.create_new_project(shows_folder, project_name)
                # cuesxml = CuesXML()
                # cues_doc = cuesxml.toXMLdoc()
                # # we get away with this because at this point there is only one cue element
                # first_cue_uuid = cues_doc.find(".cues/cue").get('uuid')
                # cuesxml.write(cues_doc, False, os.path.join(project_folder, project_name + '_cues.xml'))
                # char file with one empty char
                create_char = CreateChar(os.path.join(project_folder, project_name + '_char.xml'))
                char_list = create_char.get_firstchar()
                create_char = None
                # new cuechar file
                CreateCueChar(os.path.join(project_folder, project_name + '_cuechar.xml'),
                                  first_cue_uuid,
                                  char_list)
                # copy template files
                template_folder = os.path.join(shows_folder, 'Template')
                shutil.copy(os.path.join(template_folder, 'Venue_equipment.xml'),
                            os.path.join(project_folder, project_venue + '_equipment.xml'))
                shutil.copy(os.path.join(template_folder, 'Project_equipment.xml'),
                            os.path.join(project_folder, project_name + '_equipment.xml'))

                # load new show
                self.char_data = []
                self.cast_data = []
                self.load_show()
                self.load_project()
                #self.charstate_changed = True
                #self.stagestate_changed = True

        return

    # cast table management
    def on_table_click(self, index):
        print('In on_table_click.')
        char_table = self.tablist[self.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        char_table.selectRow(index.row())
        return

    def on_table_dblclick(self, index):
        print('In on_table_dblclick.')
        char_table = self.tablist[self.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        char_table.selectRow(index.row())
        return

    # char table Add, Insert, Delete handlers
    def char_list_changed_signal_handler(self, char_list_row):
        """this signal is emitted when the cast table (i.e.data) has changed"""
        print('In char_list_changed_signal_handler.')
        self.char.char_list[char_list_row] = self.char_data[char_list_row]
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        self.charstate_changed = True
        return

    # cast table Add, Insert, Delete handlers
    def cast_list_changed_signal_handler(self, cast_list_row):
        """this signal is emitted when the char table (i.e.data) has changed"""
        print('In cast_list_changed_signal_handler.')
        self.actor.actor_list[cast_list_row] = self.cast_data[cast_list_row]
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        self.caststate_changed = True
        return


    def on_char_table_rightclick(self):
        sender_text = self.sender().text()
        if sender_text == 'Insert':
            self.char_table_insert()
        elif sender_text == 'Add':
            self.char_table_add()
        elif sender_text == 'Delete':
            self.char_table_delete()
        return

    def char_table_add(self):
        print('In char_table_add')
        char_table = self.tablist[ShowMakerWin.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        # uuid, char, actor_uuid, actor_name, actor_understudy_uuid, understudy_name]
        new_char = ['{}'.format(uuid.uuid4()), 'New Char', 'actor uuid', 'New Actor', 'understudy uuid', 'none']
        self.char_data.append(new_char)  # new char to cast list
        self.char.char_list.append(new_char)  # new char to char object list of tuples
        char_model = char_table.model()
        char_model.layoutChanged.emit()
        char_table.scrollToBottom()
        self.The_Show.cuechar.add_new_char(new_char[0])  # new char to cuechar
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        self.charstate_changed = True
        self.stagestate_changed = True

    def char_table_insert(self):
        print('In char_table_insert')
        char_table = self.tablist[ShowMakerWin.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        char_model = char_table.model()
        indexes = char_table.selectedIndexes()
        row = indexes[0].row()
        # print('In char_table_insert before insert, length: {}'.format(len(self.char_data)))
        char_model.insertRows(row, 1)
        char_model.layoutChanged.emit()
        char_table.resizeColumnsToContents()
        char_table.selectRow(row)
        new_char = tuple(char_model.arraydata[row])
        self.char.char_list.insert(row, new_char)  # new char to char object list of tuples
        #print('In char_table_insert after insert, length: {}'.format(len(self.char_data)))
        self.The_Show.cuechar.add_new_char(new_char[0])  # new char to cuechar
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        self.charstate_changed = True
        self.stagestate_changed = True
        return

    def char_table_delete(self):
        print('In char_table_delete')
        char_table = self.tablist[ShowMakerWin.char_table_enum].findChild(QtWidgets.QTableView, name='table_char')
        indexes = char_table.selectedIndexes()
        try:
            row = indexes[0].row()
            char_model = char_table.model()
            old_row_count = len(char_model.arraydata)
            deleted_item = self.char_data[row]
            #deleted_item = self.char_data.pop(row)  # use pop so we have the item that was removed
                                                    #todo -mac save pop'd item for later undo???
            deleted_item_1 = self.char.char_list.pop(row)
            self.The_Show.cuechar.delete_char(deleted_item[0])

            char_model.removeRows(indexes[0].row(), indexes[0].row())
            new_row_count = len(char_model.arraydata)
            char_table.rowCountChanged(old_row_count, new_row_count)
            print('Olde row count: {}, New row count: {}'.format(old_row_count, new_row_count))
            char_model.layoutChanged.emit()
            char_table.resizeColumnsToContents()
            char_table.selectRow(row - 1)
            self.init_stagestat_data()
            stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
            stage_table.model().headerdata_horz = self.stagestat_header
            stage_table.model().arraydata = self.stagestat_data
            stage_table.model().layoutChanged.emit()
            stage_table.resizeColumnsToContents()
            #stage_table.selectRow()
            self.charstate_changed = True
            self.stagestate_changed = True
        except IndexError:
            QMessageBox.information(self.parent(), 'Invalid Index', 'Nothing selected!', QMessageBox.Ok)

        return

    def on_cast_table_rightclick(self):
        sender_text = self.sender().text()
        if sender_text == 'Insert':
            self.cast_table_insert()
        elif sender_text == 'Add':
            self.cast_table_add()
        elif sender_text == 'Delete':
            self.cast_table_delete()
        return

    def cast_table_add(self):
        print('In cast_table_add')
        cast_table = self.tablist[ShowMakerWin.cast_table_enum].findChild(QtWidgets.QTableView, name='table_cast')
        new_cast = ['{}'.format(uuid.uuid4()), 'New Actor', 'none']
        self.cast_data.append(new_cast)  # new char to cast list
        self.actor.actor_list.append(new_cast)  # new char to char object list of tuples
        cast_model = cast_table.model()
        cast_model.layoutChanged.emit()
        cast_table.scrollToBottom()
        self.The_Show.cuechar.add_new_char(new_cast[0])  # new char to cuechar
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        self.caststate_changed = True
        self.stagestate_changed = True

    def cast_table_insert(self):
        print('In cast_table_insert')
        cast_table = self.tablist[ShowMakerWin.cast_table_enum].findChild(QtWidgets.QTableView, name='table_cast')
        cast_model = cast_table.model()
        indexes = cast_table.selectedIndexes()
        row = indexes[0].row()
        # print('In char_table_insert before insert, length: {}'.format(len(self.char_data)))
        cast_model.insertRows(row, 1)
        cast_model.layoutChanged.emit()
        cast_table.resizeColumnsToContents()
        cast_table.selectRow(row)
        new_cast = tuple(cast_model.arraydata[row])
        self.actor.actor_list.insert(row, new_cast)  # new char to char object list of tuples
        #print('In char_table_insert after insert, length: {}'.format(len(self.char_data)))
        self.The_Show.cuechar.add_new_char(new_cast[0])  # new char to cuechar
        self.init_stagestat_data()
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.model().headerdata_horz = self.stagestat_header
        stage_table.model().arraydata = self.stagestat_data
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        self.caststate_changed = True
        self.stagestate_changed = True
        return

    def cast_table_delete(self):
        print('In cast_table_delete')
        cast_table = self.tablist[ShowMakerWin.cast_table_enum].findChild(QtWidgets.QTableView, name='table_cast')
        indexes = cast_table.selectedIndexes()
        try:
            row = indexes[0].row()
            cast_model = cast_table.model()
            old_row_count = len(cast_model.arraydata)
            deleted_item = self.cast_data[row]
            #deleted_item = self.char_data.pop(row)  # use pop so we have the item that was removed
                                                    #todo -mac save pop'd item for later undo???
            deleted_item_1 = self.char.char_list.pop(row)
            self.The_Show.cuechar.delete_char(deleted_item[0])

            cast_model.removeRows(indexes[0].row(), indexes[0].row())
            new_row_count = len(cast_model.arraydata)
            cast_table.rowCountChanged(old_row_count, new_row_count)
            print('Olde row count: {}, New row count: {}'.format(old_row_count, new_row_count))
            cast_model.layoutChanged.emit()
            cast_table.resizeColumnsToContents()
            cast_table.selectRow(row - 1)
            self.init_stagestat_data()
            stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
            stage_table.model().headerdata_horz = self.stagestat_header
            stage_table.model().arraydata = self.stagestat_data
            stage_table.model().layoutChanged.emit()
            stage_table.resizeColumnsToContents()
            #stage_table.selectRow()
            self.caststate_changed = True
            self.stagestate_changed = True
        except IndexError:
            QMessageBox.information(self.parent(), 'Invalid Index', 'Nothing selected!', QMessageBox.Ok)

        return

    # stage table management
    def on_stage_table_dblclick(self, index):
        print('In on_stage_table_dblclick')
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.selectRow(index.row())
        return

    def stage_list_changed_signal_handler(self, stage_list_row):
        self.stagestate_changed = True

    def on_stage_table_rightclick(self):
        sender_text = self.sender().text()
        if sender_text == 'Insert':
            self.stage_table_insert()
        elif sender_text == 'Add':
            self.stage_table_add()
        elif sender_text == 'Delete':
            self.stage_table_delete()
        elif sender_text == 'Edit/View Cue':
            self.stage_table_editcue()
        return

    # stage table Add, Insert, Delete handlers
    def stage_table_insert(self):
        print('In stage table insert')
        '''Inserting into the stage table requires adding a cue.
        Normally the cue would have been added elsewhere.
        But to handle it for now launch a dialog to enter cue details'''

        # get stage table and find the selected row
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        indexes = stage_table.selectedIndexes()
        row = indexes[0].row()

        # get the uuid of the selected row/cue and get it's details
        cue_uuid = stage_table.model().arraydata[row][0]
        cue_xml = self.The_Show.cues.cuelist.find(".cues/cue[@uuid='" + cue_uuid + "']")
        cue_list = self.The_Show.cues.getcuelistbyuuid(cue_uuid)

        # Show to user for editing
        edit_dlg = EditCue_dlg()
        edit_dlg.setWindowTitle(_translate("dlgEditCue", "Insert Cue"))
        edit_dlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        edit_dlg.fillfields(row, cue_list)
        edit_dlg.exec_()
        # insert new cue into the cue list
        if edit_dlg.changeflag:
            chg_list = edit_dlg.getchange()
            self.The_Show.cues.insertcue(row, chg_list)  # insert with changes
        else:
            self.The_Show.cues.insertcue(row, cue_list)  # insert no changes

        # Insert the new row into the stage table
        stage_model = stage_table.model()
        stage_model.insertRows(row, 1)
        '''At this point the table model and the cues.cue_list uuid for this cue
        don't match, reconcile here'''
        new_cue_uuid = self.The_Show.cues.getcurrentcueuuid(row)
        stage_model.arraydata[row][0] = new_cue_uuid
        # add new cue to cuechar
        self.The_Show.cuechar.add_cue(new_cue_uuid, self.char_data)
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        stage_table.selectRow(row)
        self.stagestate_changed = True
        return

    def stage_table_add(self):
        print('In stage table add')
        '''Adding to the stage table requires adding a cue.
        Normally the cue would have been added elsewhere.
        But to handle it for now launch a dialog to enter cue details'''

        # get stage table and find the selected row
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        stage_model = stage_table.model()
        # Adding to end of table, so get the last index
        if stage_model.rowCount() == 0:
            cue_num = 0  # if rowcount == 0, then the table is empty
        else:
            cue_num = stage_model.rowCount() - 1

        # get the uuid of the selected row/cue and get it's details
        cue_uuid = stage_table.model().arraydata[cue_num][0]
        cue_xml = self.The_Show.cues.cuelist.find(".cues/cue[@uuid='" + cue_uuid + "']")
        cue_list = self.The_Show.cues.getcuelistbyuuid(cue_uuid)

        # Show to user for editing
        edit_dlg = EditCue_dlg()
        edit_dlg.setWindowTitle(_translate("dlgEditCue", "Insert Cue"))
        edit_dlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        edit_dlg.fillfields(cue_num, cue_list)
        edit_dlg.exec_()
        # insert new cue into the cue list
        if edit_dlg.changeflag:
            chg_list = edit_dlg.getchange()
            new_cue_uuid, new_cue_num = self.The_Show.cues.addnewcue(chg_list)  # add with changes
        else:
            new_cue_uuid, new_cue_num = self.The_Show.cues.addnewcue(cue_list)  # add no changes

        print('stage_model.rowCount(): {}'.format(stage_model.rowCount()))
        print('cue_num: {}'.format(cue_num))
        print('cue_uuid: {}'.format(cue_uuid))
        print('cue_xml num: {}'.format(cue_xml.get('num')))
        print('new_cue_num: {}'.format(new_cue_num))
        print('new_cue_uuid: {}'.format(new_cue_uuid))
        #print(': {}'.format())

        # Add the new row to the stage table
        stage_model.insertRows(stage_model.rowCount(), 1)
        '''At this point the table model and the cues.cue_list uuid for this cue
        don't match, reconcile here'''
        #new_cue_uuid = self.The_Show.cues.getcurrentcueuuid(row)
        stage_model.arraydata[int(new_cue_num)][0] = new_cue_uuid
        # add new cue to cuechar
        self.The_Show.cuechar.add_cue(new_cue_uuid, self.char_data)
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        stage_table.scrollToBottom()
        stage_table.selectRow(int(new_cue_num))
        self.stagestate_changed = True
        return

    def stage_table_delete(self):
        print('In stage table delete')
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        indexes = stage_table.selectedIndexes()
        row = indexes[0].row()
        stage_model = stage_table.model()
        cue_uuid = stage_model.arraydata[row][0]
        self.The_Show.cuechar.delete_cue(cue_uuid)
        self.The_Show.cues.delete_cue_by_uuid(cue_uuid)
        stage_model.removeRows(row, 1)
        stage_table.model().layoutChanged.emit()
        stage_table.resizeColumnsToContents()
        stage_table.selectRow(row - 1)
        self.stagestate_changed = True
        return

    def stage_table_editcue(self):
        stage_table = self.tablist[ShowMakerWin.stage_table_enum].findChild(QtWidgets.QTableView, name='table_stage')
        indexes = stage_table.selectedIndexes()
        row = indexes[0].row()
        cue_uuid = stage_table.model().arraydata[row][0]
        cue_list = self.The_Show.cues.getcuelistbyuuid(cue_uuid)
        edit_dlg = EditCue_dlg()
        edit_dlg.setWindowTitle(_translate("dlgEditCue", "Edit/View Cue"))
        edit_dlg.setROcueelements(['Cue_Number', 'Mutes', 'Levels'])
        edit_dlg.fillfields(row, cue_list)
        edit_dlg.exec_()
        if edit_dlg.changeflag:
            chg_list = edit_dlg.getchange()
            self.The_Show.cues.updatecue(row, chg_list)
            self.stagestate_changed = True
        return

class CharTableModel(QtCore.QAbstractTableModel):
    """

    """
    def __init__(self, datain, headerdata_horz, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata_horz = headerdata_horz

    def rowCount(self, parent=QtCore.QModelIndex()):
        # print('arrayData len: {}'.format(len(self.arraydata)))
        return len(self.arraydata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.arraydata[0])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print('Role:({})'.format(role))
        if not index.isValid(): return None
        if role == QtCore.Qt.EditRole:
            return self.arraydata[index.row()][index.column()]
        if not role == QtCore.Qt.DisplayRole: return None

        return self.arraydata[index.row()][index.column()]

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if not index.isValid(): return False
        if role == QtCore.Qt.EditRole:
            self.arraydata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            self.parent().char_table_changed_sig.emit(index.row())
        print("setData", index.row(), index.column(), value, role)
        return True

    def flags(self, index):
        """changed to this to allow all columns to be editable"""
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # if (index.column() == 0):
        #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        # else:
        #     return QtCore.Qt.ItemIsEnabled

    def headerData(self, sect, orientation, role):
        """"""
        '''For horizontal headers, the section number corresponds to the column number.
        Similarly, for vertical headers, the section number corresponds to the row number.'''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if sect < len(self.headerdata_horz):
                return QtCore.QVariant(self.headerdata_horz[sect])
            else:
                return QtCore.QVariant('')
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return sect  # return the row count
            # if sect < len(self.headerdata_vert):
            #     return QtCore.QVariant(self.headerdata_vert[col])
            # else:
            #     return QtCore.QVariant('')

        return QtCore.QVariant()

    def insertRows(self, row, count):
        self.beginInsertRows(QModelIndex(), row, row)
        newrow = self.arraydata[row][:]  # slice [:] clones the row
        # new uuid for this character
        newrow[0] = '{}'.format(uuid.uuid4())
        self.arraydata.insert(row, newrow)
        self.endInsertRows()
        return True

    def removeRows(self, row, count):
        targetindex =self.createIndex(row, 0)
        self.beginRemoveRows(QModelIndex(), row, row)
        popped_item = self.arraydata.pop(row)
        self.endRemoveRows()
        return True


class CastTableModel(QtCore.QAbstractTableModel):
    """

    """

    def __init__(self, datain, headerdata_horz, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata_horz = headerdata_horz

    def rowCount(self, parent=QtCore.QModelIndex()):
        # print('arrayData len: {}'.format(len(self.arraydata)))
        return len(self.arraydata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.arraydata[0])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print('Role:({})'.format(role))
        if not index.isValid(): return None
        if role == QtCore.Qt.EditRole:
            return self.arraydata[index.row()][index.column()]
        if not role == QtCore.Qt.DisplayRole: return None

        return self.arraydata[index.row()][index.column()]

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if not index.isValid(): return False
        if role == QtCore.Qt.EditRole:
            self.arraydata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            self.parent().cast_table_changed_sig.emit(index.row())
        print("setData", index.row(), index.column(), value, role)
        return True

    def flags(self, index):
        """changed to this to allow all columns to be editable"""
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # if (index.column() == 0):
        #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        # else:
        #     return QtCore.Qt.ItemIsEnabled

    def headerData(self, sect, orientation, role):
        """"""
        '''For horizontal headers, the section number corresponds to the column number.
        Similarly, for vertical headers, the section number corresponds to the row number.'''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if sect < len(self.headerdata_horz):
                return QtCore.QVariant(self.headerdata_horz[sect])
            else:
                return QtCore.QVariant('')
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return sect  # return the row count
            # if sect < len(self.headerdata_vert):
            #     return QtCore.QVariant(self.headerdata_vert[col])
            # else:
            #     return QtCore.QVariant('')

        return QtCore.QVariant()

    def insertRows(self, row, count):
        self.beginInsertRows(QModelIndex(), row, row)
        newrow = self.arraydata[row][:]  # slice [:] clones the row
        # new uuid for this character
        newrow[0] = '{}'.format(uuid.uuid4())
        self.arraydata.insert(row, newrow)
        self.endInsertRows()
        return True

    def removeRows(self, row, count):
        targetindex = self.createIndex(row, 0)
        self.beginRemoveRows(QModelIndex(), row, row)
        popped_item = self.arraydata.pop(row)
        self.endRemoveRows()
        return True


class CastTableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

    # def dataChanged(self, fromIndex, toIndex, roles):
    #
    #     print('In CastTableView dataChanged')
    #     self.cast


class StageTableModel(QtCore.QAbstractTableModel):
    """
    A simple 5x4 table model to demonstrate the delegates
    """
    def __init__(self, datain, headerdata_horz, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata_horz = headerdata_horz

    def rowCount(self, parent=QtCore.QModelIndex()):
        # print('arrayData len: {}'.format(len(self.arraydata)))
        return len(self.arraydata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.arraydata[0])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print("data: index:{}{}, val@index: {}, role:{}".format(index.row(),
        #                                                         index.column(),
        #                                                         self.arraydata[index.row()][index.column()], role))

        if not index.isValid(): return QVariant()
        table_item = self.arraydata[index.row()][index.column()]
        if role == Qt.DisplayRole:
            if isinstance(table_item, StageState):
                return table_item
            else:
                #return "{0:02d}".format(int(self.arraydata[index.row()][index.column()]))
                return self.arraydata[index.row()][index.column()]
        elif role == QtCore.Qt.EditRole:
            if isinstance(table_item, StageState):
                return table_item
            else:
                # return "{0:02d}".format(int(self.arraydata[index.row()][index.column()]))
                return self.arraydata[index.row()][index.column()]
        else:
            return QVariant()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        # print("setData: index:{}{}, value:{}, role:{}".format(index.row(), index.column(), value, role))
        if not index.isValid(): return False
        if role == QtCore.Qt.DisplayRole:
            return False
            #return self.arraydata[index.row()][index.column()]
        elif role == QtCore.Qt.EditRole:
            if isinstance(index.data(), StageState):
                index.data().talentstate = value
            else:
                self.arraydata[index.row()][index.column()] = str(value)
            self.dataChanged.emit(index, index)
            self.parent().stage_table_changed_sig.emit(index.row())
            return True
        else:
            return False

    def flags(self, index):
        """changed to this to allow all columns to be editable"""
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # if (index.column() == 0):
        #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        # else:
        #     return QtCore.Qt.ItemIsEnabled

    def headerData(self, sect, orientation, role=QtCore.Qt.DisplayRole):
        """"""
        '''For horizontal headers, the section number corresponds to the column number.
        Similarly, for vertical headers, the section number corresponds to the row number.'''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if sect < len(self.headerdata_horz):
                # return QtCore.QVariant(self.headerdata_horz[sect])
                return self.headerdata_horz[sect]
            else:
                return QtCore.QVariant('')
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return sect  # return the row count
            # if sect < len(self.headerdata_vert):
            #     return QtCore.QVariant(self.headerdata_vert[col])
            # else:
            #     return QtCore.QVariant('')

        return QtCore.QVariant()

    def insertRows(self, row, count):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if row == self.rowCount():
            # copy last row data, except add a new StageState for all StageState columns
            newrow = self.arraydata[row - 1][:]  # slice [:] clones the row
        else:
            # copy row
            newrow = self.arraydata[row][:]  # slice [:] clones the row
        # new cue gets a new uuid
        newrow[0] = '{}'.format(uuid.uuid4())
        for colcnt, junk in enumerate(newrow):
            if isinstance(newrow[colcnt], StageState):
                oldstagestate = newrow[colcnt].talentstate
                newrow[colcnt] = None
                newrow[colcnt] = StageState(oldstagestate)  # replace copy of StageState from old row, retaining previous state
        if row == self.rowCount():
            self.arraydata.append(newrow)
        else:
            self.arraydata.insert(row, newrow)
        self.endInsertRows()
        return True

    def removeRows(self, row, count):
        self.beginRemoveRows(QModelIndex(), row, row)
        popped_item = self.arraydata.pop(row)
        self.endRemoveRows()
        return True


class StageTableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        # Set the delegate for columns
        self.setItemDelegate(SelectDelegate(self))

    def dataChanged(self, fromIndex, toIndex, roles):
        print('In StageTableView dataChanged')


class StageState(object):
    # enum EditMode
    Editable, ReadOnly = range(2)
    # enum
    OffStage, OnStage, MicOn = range(3)
    PaintingScaleFactor = 20

    def __init__(self, state=0, maxStarCount=5):
        self.talentstate = state
        self._maxStarCount = maxStarCount

        self.starPolygon = QtGui.QPolygonF([QtCore.QPointF(1.0, 0.5)])
        for i in range(5):
            self.starPolygon << QtCore.QPointF(0.5 + 0.5 * math.cos(0.8 * i * math.pi),
                                               0.5 + 0.5 * math.sin(0.8 * i * math.pi))

        self.diamondPolygon = QtGui.QPolygonF()
        self.diamondPolygon << QtCore.QPointF(0.4, 0.5) \
                            << QtCore.QPointF(0.5, 0.4) \
                            << QtCore.QPointF(0.6, 0.5) \
                            << QtCore.QPointF(0.5, 0.6) \
                            << QtCore.QPointF(0.4, 0.5)

    def sizeHint(self):
        return self.PaintingScaleFactor * QtCore.QSize(self._maxStarCount, 1)

    def paint(self, painter, rect, palette, editMode):
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)

        if editMode == StageState.Editable:
            painter.setBrush(palette.highlight())
        else:
            painter.setBrush(palette.windowText()) #QColor(255, 51, 0))

        if self.talentstate == StageState.OffStage:
            painter.setBrush(QBrush(QColor(255, 255, 102)))
        elif self.talentstate == StageState.OnStage:
            painter.setBrush(QBrush(QColor(0, 102, 255)))
        elif self.talentstate == StageState.MicOn:
            painter.setBrush(QBrush(QColor(255, 153, 51)))

        yOffset = (rect.height() - self.PaintingScaleFactor) / 2
        xOffset = (rect.width() - self.PaintingScaleFactor) /2
        painter.translate(rect.x() + xOffset, rect.y() + yOffset)
        painter.scale(self.PaintingScaleFactor, self.PaintingScaleFactor)

        # for i in range(self._maxStarCount):
        #     if i < self.talentstate:
        #         painter.drawPolygon(self.starPolygon, QtCore.Qt.WindingFill)
        #     elif editMode == StageState.Editable:
        #         painter.drawPolygon(self.diamondPolygon, QtCore.Qt.WindingFill)
        #
        #     painter.translate(1.0, 0.0)
        painter.drawPolygon(self.starPolygon, QtCore.Qt.WindingFill)
        painter.restore()


class MyHeaderView(QtWidgets.QHeaderView):

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self._font = QtGui.QFont("helvetica", 15)
        self._metrics = QtGui.QFontMetrics(self._font)
        self._descent = self._metrics.descent()
        self._margin = 10

    def paintSection(self, painter, rect, index):
        # if index < 1: return
        data = self._get_data(index)
        painter.rotate(-90)
        painter.setFont(self._font)
        painter.drawText(- rect.height() + self._margin,
                         rect.left() + (rect.width() + self._descent) / 2, data)

    def sizeHint(self):
        return QtCore.QSize(0, self._get_text_width() + 2 * self._margin)

    def _get_text_width(self):
        return max([self._metrics.width(self._get_data(i))
                    for i in range(0, self.model().columnCount())])

    def _get_data(self, index):
        return self.model().headerData(index, self.orientation())


class SelectDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        starRating = index.data()
        if isinstance(starRating, StageState):
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            starRating.paint(painter, option.rect, option.palette,
                    StageState.ReadOnly)
        else:
            super(SelectDelegate, self).paint(painter, option, index)

    def sizeHint(self, option, index):
        return super(SelectDelegate, self).sizeHint(option, index)

    def createEditor(self, parent, option, index):
        selectedcolumn = index.column()
        # if selectedcolumn == 0 or selectedcolumn == 1:
        if selectedcolumn in list(range(0,1)):
            editor = QtWidgets.QSpinBox(parent)
            return editor
        elif selectedcolumn > 3:
            editor = QtWidgets.QComboBox(parent)
            li = []
            li.append("Off Stage")
            li.append("On Stage")
            li.append("Mic On")
            editor.addItems(li)
            return editor
        else:
            return super(SelectDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            editor.setCurrentIndex(index.data().talentstate)
        elif isinstance(editor, QSpinBox):
            editor.setValue(int(index.data()))
        else:
            super(SelectDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            state = editor.currentIndex()
            model.setData(index, state, Qt.EditRole)
        elif isinstance(editor, QSpinBox):
            model.setData(index, editor.value(), Qt.EditRole)
        else:
            super(SelectDelegate, self).setModelData(editor, model, index)

class CharTableDelegate(QtWidgets.QStyledItemDelegate):

    def sizeHint(self, option, index):
        return super(CharTableDelegate, self).sizeHint(option, index)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        return editor

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            current_played_by_index = 0
            try:
                # populate the combobox with the cast list
                for actor_index, actor in enumerate(self.parent().findChild(QTableView, name='table_cast').model().arraydata):
                    if actor[1] == index.data():
                        current_played_by_index = actor_index
                    editor.addItem(actor[1])
                editor.setCurrentIndex( current_played_by_index )
            except:
                logging.error('cast table data not found')
        else:
            super(CharTableDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            actor_index = editor.currentIndex()  # is the index of the name selected
            actor_item = self.parent().findChild(QTableView, name='table_cast').model().arraydata[actor_index]
            uuid_index = model.createIndex(index.row(), index.column() -1)
            model.setData(index, actor_item[1], Qt.EditRole)  # set the played by name
            model.setData(uuid_index, actor_item[0], Qt.EditRole)
            print()
        else:
            super(SelectDelegate, self).setModelData(editor, model, index)

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
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    app = QtWidgets.QApplication(sys.argv)

    ui = ShowMakerWin()
    ui.show()
    sys.exit(app.exec_())