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



class MuteMapDlg(QtWidgets.QDialog, MuteMap_ui.Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        #self.setGeometry(screen.x() + int(0.05 * screen.width()), screen.y(), screen.width() * 0.9, screen.height() * 0.9)
        self.setGeometry(10, screen.y(), 1500,screen.height() * 0.9)
        #self.tableheader = ['Cue#'] + self.get_header()
        self.tableheader = ['Cue#', 'SHIT']
        self.tabledata = [['on', 'off'],['on', 'off']]
        #self.tableView.doubleClicked.connect(self.on_table_dblclick)
        #self.tableView.clicked.connect(self.on_table_click)
        #self.get_table_data()
        self.tablemodel = MyTableModel(self.tabledata, self.tableheader, self)
        self.tableView.setModel(self.tablemodel)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        i = self.tableView.model().index(0, 0)
        #Form.setObjectName("Form")
        #Form.resize(400, 300)
        # self.kled = KLed(Form)
        # self.kled.setObjectName("kled")
        #self.kled = QPushButton()
        #self.tableView.setIndexWidget(i, self.kled)

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
        if parent.isValid():
            return 0
        return len(self.arraydata)

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
            if self.arraydata:
                return len(self.arraydata[0])
            else:
                return 0
        # if len(self.arraydata) > 0:
        #     return len(self.arraydata[0])
        # return 0

    def data(self, index, role):
        if not index.isValid():
            print('Invalid index in MyModel>data')
            retval = QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            retval = QtCore.QVariant()
        else:
            retval = QtCore.QVariant(self.arraydata[index.row()][index.column()])
        #     print(self.arraydata[index.row()][index.column()])
        # print(retval)
        return retval
        # if not index.isValid():
        #     return QVariant()
        # elif role != QtCore.Qt.DisplayRole:
        #     return QtCore.QVariant()
        # return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole and index.isValid():
            print(index.row())
            self.arraydata[index.row()][index.column()] = value
            print('Return from rowCount: {0}'.format(self.rowCount(index)))
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        return False
        # if role == QtCore.Qt.EditRole:
        #     self.arraydata.extend([[supportedcontroltypes[value]]])
        #     self.dataChanged.emit(self.createIndex(0,0),
        #                       self.createIndex(self.rowCount(None), self.columnCount(None)),
        #                           [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole])
        #     return True
        # return False

    # def flags(self, index):
    #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col < len(self.headerdata):
                return QtCore.QVariant(self.headerdata[col])
            else:
                return QtCore.QVariant('')
        return QtCore.QVariant()
        # if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
        #     return QtCore.QVariant(self.headerdata[col])
        # return QtCore.QVariant()

if __name__ == "__main__":
    logger_main = logging.getLogger(__name__)
    logger_main.info('Begin')
    cfg = configuration()
    The_Show = ShowMxr()
    The_Show.displayShow()

    app = QtWidgets.QApplication(sys.argv)

    ui = MuteMapDlg()
    ui.show()
    logging.info('Shutdown')
    sys.exit(app.exec_())
