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
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, cue_fields

from MM_MixerConf import MixerConf
# from MixerMap import MixerCharMap

import MixerMaker_ui
import StripEdit_ui

import styles

parser = argparse.ArgumentParser()


cfgdict = cfg.toDict()

striplistheader = ['Type','Count','Name']

class MixerMakerDlg(QtWidgets.QMainWindow, MixerMaker_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MixerMakerDlg, self).__init__(parent)
        self.setupUi(self)
        self.comboBoxPickMixer.activated.connect(self.populateMixer)
        self.actionOpen.triggered.connect(self.openMixer)
        self.actionExit.triggered.connect(self.close)
        self.actionNew.triggered.connect(self.newMixer)
        self.actionSave.triggered.connect(self.saveMixer)
        self.actionLoadMixers = QAction()
        self.actionLoadMixers.triggered.connect(self.loadMixers)
        self.mixers = {}
        self.mixerindex = 0
        self.tableView.clicked.connect(self.tableClicked)
        self.stripmodelindex = 0
        self.tableView.doubleClicked.connect(self.on_table_dblclick)
        self.tableView.clicked.connect(self.on_table_click)

        self.tableView.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.action_list = ['Add', 'Edit', 'Remove']
        self.actionAdd = QAction("Add", None)
        self.actionAdd.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.actionAdd)
        self.actionEdit = QAction("Edit", None)
        self.actionEdit.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.actionEdit)
        self.actionRemove = QAction("Remove", None)
        self.actionRemove.triggered.connect(self.on_table_rightclick)
        self.tableView.addAction(self.actionRemove)

        self.pushButtonAddStrip.clicked.connect(self.stripAdd_clicked)
        self.pushButtonEditStrip.clicked.connect(self.stripEdit_clicked)
        self.pushButtonRemoveStrip.clicked.connect(self.stripRemove_clicked)



    def populateMixer(self, index):
        self.mixerindex = index
        self.lineEditBrand.setText(self.mixers.mfr_list[index])
        self.lineEditModel.setText(self.mixers.model_list[index])
        self.mixers.mixerattribs(self.mixers.mfr_list[index], self.mixers.model_list[index])
        if self.mixers.protocol == 'osc':
            self.radioButtonOSC.setChecked(True)
        else:
            self.radioButtonMIDI.setChecked(True)
        if self.mixers.mutestyle == 'illuminated':
            self.comboBoxMuteStyle.setCurrentIndex(0)
        else:
            self.comboBoxMuteStyle.setCurrentIndex(1)
        if self.mixers.s_countbase == '0':
            self.comboBoxCountBase.setCurrentIndex(0)
        else:
            self.comboBoxCountBase.setCurrentIndex(1)
        self.disptext()

    def loadMixers(self):
        print('loadMixers')
        self.mixers = MixerConf(self.conffile)
        print(self.mixers.mixer_count)
        print(self.mixers.mixer_list)
        a = ['{0}, {1}'.format( a, b) for a, b in zip(self.mixers.mfr_list, self.mixers.model_list)]
        self.comboBoxPickMixer.addItems(['{0}, {1}'.format( a, b) for a, b in zip(self.mixers.mfr_list, self.mixers.model_list)])
        pass

    def openMixer(self):
        fileNames = []
        fdlg = QtWidgets.QFileDialog()
        # fname = fdlg.getOpenFileName(self, 'Open file', '/home')
        fdlg.setFilter(QDir.AllEntries | QDir.Hidden)
        if (fdlg.exec()):
            fileNames = fdlg.selectedFiles()
        #fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fdlg.close()
        if len(fileNames) != 0:
            self.conffile = fileNames[0]
            self.actionLoadMixers.trigger()
        print('File>Open: {0}'.format(fileNames))


    def newMixer(self):
        print('File>New')

    def saveMixer(self):
        print('File>Save')

    def exitMixer(self):
        print('File>Exit')

    def closeEvent(self, event):
        """..."""
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        """..."""
        reply = QMessageBox.question(self, 'Confirm Quit',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)
        return reply

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, striplistheader, self)
        # tblview = self.window().findChild(QtWidgets.QTableView, name='tableWidget')
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        self.tableView.selectRow(0)
        #self.tableView.connect(self.tableClicked, QtCore.SIGNAL("clicked()"))

    def get_table_data(self):
        strips = self.mixers.mixers[self.mixerindex].findall('strip')
        # todo-mac fix this and decide how to collect all the strip info
        # strips = self.mixers.mixerstrips(self.mixers.mfr_list[self.mixerindex], self.mixers.model_list[self.mixerindex])

        self.tabledata =[]
        for strip in strips:
            striptype = strip.attrib['type']  # todo-mac display strip data on second tab??????
            stripcount = strip.attrib['cnt']
            stripname = strip.attrib['name']
            self.tabledata.append([striptype,stripcount,stripname])
        pass

    def tableClicked(self, modelidx):
        self.stripmodelindex = modelidx.row()
        self.tableView.selectRow(self.stripmodelindex)

    def on_table_rightclick(self):
        print('right click')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            print(sender_text)
        elif sender_text == 'Edit':
            print(sender_text)
        elif sender_text == 'Remove':
            print(sender_text)
        pass

    def on_table_dblclick(self,index):
        print('double click on row: {0}'.format(index.row()))
        pass

    def on_table_click(self,index):
        print('click on row: {0}'.format(index.row()))
        pass

    def stripAdd_clicked(self):
        print('stripAdd_clicked with row {0} selected.'.format(self.tableView.selectedIndexes()[0].row()))
        print(self.tableView.model().rowCount(None))


    def stripEdit_clicked(self):
        print('stripEdit_clicked')

    def stripRemove_clicked(self):
        print('stripRemove_clicked')


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
        # elif role == Qt.BackgroundColorRole:
        #     #print (self.arraydata[index.row()][7])
        #     if self.arraydata[index.row()][7] == 'Stage':
        #         return QBrush(Qt.blue)
        #     elif self.arraydata[index.row()][7] == 'Sound':
        #         return QBrush(Qt.yellow)
        #     elif self.arraydata[index.row()][7] == 'Light':
        #         return QBrush(Qt.darkGreen)
        #     elif self.arraydata[index.row()][7] == 'Mixer':
        #         return QBrush(Qt.darkYellow)
        #     else:
        #         return QBrush(Qt.darkMagenta)
        #
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
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    # try:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    #ui = ChanStripDlg(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui = MixerMakerDlg()
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