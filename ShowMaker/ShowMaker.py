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
from ShowControl.utils.Char import Char
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


module_logger.info('module log from ShowMaker.py')

class ShowMakerWin(QtWidgets.QMainWindow, ShowMaker_ui.Ui_MainWindow_showmaker):

    def __init__(self, parent=None):
        super(ShowMakerWin, self).__init__(parent)
        logging.info('in ShowMakerWin.__init__')
        self.cfg = None
        self.load_cfg()
        self.The_Show = None
        self.load_show()
        self.setupUi(self)
        self.tablist = []
        self.tablistvertlayout = []
        # add the cast tab
        idx = 0
        self.tablist.append(QtWidgets.QWidget())
        self.tablist[idx].setMinimumSize(QtCore.QSize(0, 400))
        self.tablist[idx].setObjectName("Pg {}".format(idx))
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tablist[idx])
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        # create a tableview for the cast tab
        tableView = QtWidgets.QTableView(self.tablist[idx])
        tableView.setObjectName("table_cast")
        self.chrchnmap = MixerCharMap(self.The_Show.show_confpath + self.The_Show.show_conf.settings['mixermap'])
        self.char = None
        self.cast_data = []
        self.cast_header = []
        self.verticalLayout.addWidget(tableView)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.insertTab(idx, self.tablist[idx], 'Characters/Cast')
        # add the stage state tab
        self.tablist.append(QtWidgets.QWidget())
        idx = 1
        self.tablist[idx].setObjectName("Pg {}".format(idx))
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tablist[idx])
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        # create a tableview for the Stage State
        tableView = TableView(self.tablist[idx])
        tableView.setObjectName("table_stage")
        # the following two lines turn the text in the horizontal header vertical
        # but, the paint routine doesnt handle the newline
        # so until I get around to fixing that I commented them out
        # headerView = MyHeaderView()
        # tableView.setHorizontalHeader(headerView)
        self.stagestat_data = []
        self.stagestat_header = []
        self.verticalLayout_4.addWidget(tableView)
        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.tabWidget.insertTab(idx, self.tablist[idx], 'Stage State')
        self.load_project()
        self.pushButtonselectfolder.clicked.connect(self.select_new_path_clicked)

        self.action_Exit.triggered.connect(self.close)
        self.action_OpenShow.triggered.connect(self.openProjectFolder)
        self.action_NewShow.triggered.connect(self.new_project)

    def load_cfg(self):
        self.cfg = configuration()

    def load_show(self):
        self.The_Show = Show(self.cfg.cfgdict)

    def load_project(self):
        self.init_cast_data()
        castmodel = CastTableModel(self.cast_data, self.cast_header, self)
        cast_table = self.tablist[0].findChild(QtWidgets.QTableView, name='table_cast')
        cast_table.setModel(castmodel)
        cast_table.resizeColumnsToContents()
        self.init_stagestat_data()
        stagemodel = StageTableModel(self.stagestat_data, self.stagestat_header, self)
        stage_table = self.tablist[1].findChild(QtWidgets.QTableView, name='table_stage')
        stage_table.setModel(stagemodel)
        stage_table.resizeColumnsToContents()
        self.lineEdit_projectname.setText(self.The_Show.show_conf.settings['title'])
        self.lineEdit_projectcuefile.setText(self.The_Show.show_conf.settings['cues']['href1'])
        self.lineEdit_projectpath.setText(self.cfg.cfgdict['configuration']['project']['folder'])
        return

    def init_cast_data(self):
        self.cast_header = ['Character', 'Actor', 'Understudy']
        self.char = Char()
        self.char.setup_cast(self.The_Show.show_confpath + self.The_Show.show_conf.settings['charmap'])
        self.char.chars_to_list_of_tuples()
        for chrnam in self.char.char_list:
            try:
                char = chrnam[1]
                print(char)
            except:
                print('no char')
            try:
                actor = chrnam[2]
            except:
                print('no actor')
            self.cast_data.append([char,actor])

        return

    def init_stagestat_data(self):
        self.stagestat_header = ['Page', 'Act', 'Scene', 'Line']
        for chrnam in self.char.char_list:
            try:
                char = chrnam[1]
                print(char)
            except:
                print('no char')
            try:
                actor = chrnam[2]
            except:
                print('no actor')
            self.stagestat_header.extend([char + '\n' + actor])
        self.stagestat_data = []
        for row in range(0, 6):
            cols = list(range(1, 5))
            for chrnam in self.char.char_list:
                stage_stat = StageState(StageState.OffStage)
                cols.extend([stage_stat])
            self.stagestat_data.append(cols)

        return

    def select_new_path_clicked(self):
        print('New path')

    def closeEvent(self, event):
        """..."""
        # if self.mixers_modified:
        #     reply = QMessageBox.question(self, 'Save Changes', 'Save changes to mixers?',
        #                                  QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        #                                  QMessageBox.Cancel)
        #     if reply == QMessageBox.Yes:
        #         self.mixers.savemixers(False, 'TestMixerSave.xml')
        #         self.mixers_modified = False
        #     elif reply == QMessageBox.No:
        #         pass
        #     elif reply == QMessageBox.Cancel:
        #         pass

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

    def openProjectFolder(self):
        fileNames = []
        fdlg = QtWidgets.QFileDialog()
        # fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        fdlg.setFilter(QDir.Hidden | QDir.Dirs | QDir.Files)
        fdlg.setFileMode(QFileDialog.ExistingFile)
        fdlg.setNameFilters(["Project files (*.xml)"])
        fdlg.setDirectory(self.The_Show.show_confpath)
        if (fdlg.exec()):
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
            self.chrchnmap = None
            self.cast_data = []
            #self.chrchnmap = MixerCharMap(self.The_Show.show_confpath + self.The_Show.show_conf.settings['mixermap'])
            self.load_project()
        print('File>Open: {0}'.format(fileNames))

    def new_project(self):
        fdlg = QtWidgets.QFileDialog()
        fdlg.setFilter(QDir.Hidden | QDir.Dirs)
        shows_folder = os.path.dirname(os.path.dirname(self.The_Show.show_confpath))
        fdlg.setDirectory(shows_folder)
        if (fdlg.exec()):
            fileNames = fdlg.selectedFiles()
            if fileNames:
                if not os.path.exists(fileNames[0]):
                    os.makedirs(fileNames[0])
                project_name = os.path.basename(os.path.normpath(fileNames[0]))
                self.cfg.cfgdict['configuration']['project']['folder'] = project_name
                self.cfg.cfgdict['configuration']['project']['file'] = project_name + '_project.xml'
                newcfg_doc = self.cfg.updateFromDict()
                self.cfg.write(newcfg_doc, True, CFG_PATH)
                self.load_cfg()

        return

class CastTableModel(QtCore.QAbstractTableModel):
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
        # print('Role:({})'.format(role))
        if not index.isValid(): return None
        if not role == QtCore.Qt.DisplayRole: return None
        return self.arraydata[index.row()][index.column()]

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if not index.isValid(): return None
        if role == QtCore.Qt.EditRole:
            self.arraydata[index.row()][index.column()] = value
        print("setData", index.row(), index.column(), value)

    def flags(self, index):
        """changed to this to allow all columns to be editable"""
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
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
                return "{0:02d}".format(int(self.arraydata[index.row()][index.column()]))
        elif role == QtCore.Qt.EditRole:
            if isinstance(table_item, StageState):
                return table_item
            else:
                return "{0:02d}".format(int(self.arraydata[index.row()][index.column()]))
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
            return True
        else:
            return False

    def flags(self, index):
        """changed to this to allow all columns to be editable"""
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
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
        targetindex = self.createIndex(row, 0)
        self.beginInsertRows(targetindex, self.rowCount(),self.rowCount()+1)
        # copy last row data, except add a new StageState for all StageState columns

        newrow = self.arraydata[self.rowCount()-1][:]  # slice [:] clones the row
        for colcnt, junk in enumerate(newrow):
            if isinstance(newrow[colcnt], StageState):
                oldstagestate = newrow[colcnt].talentstate
                newrow[colcnt] = None
                newrow[colcnt] = StageState(oldstagestate)  # replace copy of StageState from old row, retaining previous state
        self.arraydata.append(newrow)
        self.endInsertRows()
        return True

class TableView(QtWidgets.QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        # Set the delegate for columns
        self.setItemDelegate(SelectDelegate(self))

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
        if selectedcolumn in list(range(0,4)):
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


if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    app = QtWidgets.QApplication(sys.argv)

    ui = ShowMakerWin()
    ui.show()
    sys.exit(app.exec_())