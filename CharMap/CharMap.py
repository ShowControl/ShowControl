#!/usr/bin/env python3
__author__ = 'mac'

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
module_logger = logging.getLogger('CM_logger')

_translate = QtCore.QCoreApplication.translate

from CharMap.CharMap_ui import Ui_MainWindow

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, leveldata, headerdata_horz, headerdata_vert, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.leveldata = leveldata
        self.headerdata_horz = headerdata_horz
        self.headerdata_vert = headerdata_vert
        # self.iconmute_on = QtGui.QIcon()
        # self.iconmute_on.addPixmap(QtGui.QPixmap(":/icon/Mute_illum_64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.iconmute_off = QtGui.QIcon()
        # self.iconmute_off.addPixmap(QtGui.QPixmap(":/icon/Mute_dark_64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)


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

    def data(self, index, role):  # Return data from the model
        if index.isValid():
            #print('Invalid index in MyModel>data')
            logging.info('Invalid index in MyModel>data')
            retval = QtCore.QVariant()
            if role == QtCore.Qt.BackgroundRole:
                cell_contents = self.arraydata[index.row()][index.column()]
                retval = QtCore.QVariant()
                # if cell_contents[-1] == '0':
                #     #retval = QBrush(Qt.lightGray)
                #     retval = QtCore.QVariant()
                # else:
                #     retval = QBrush(Qt.red)
            elif role == QtCore.Qt.DisplayRole:
                retval = QtCore.QVariant(self.leveldata[index.row()][index.column()])
                # retval = QtCore.QVariant(self.leveldata[index.row()][index.column()])
            elif role == QtCore.Qt.DecorationRole:
                #retval = QtGui.QIcon("Mute_illum_64.png")
                #if index.column() != 0:
                try:
                    pm = QtGui.QPixmap()
                    if self.arraydata[index.row()][index.column()][-1] == '0':# or index.column() == 0:
                        #return mute_btn_dark# QtGui.QIcon('Mute_dark_64.png')
                        pm = pix_cache.find('dark')
                        return pm
                        #return self.iconmute_off
                    else:
                        #return mute_btn_illum #QtGui.QIcon('Mute_illum_64.png')
                        pm = pix_cache.find('illuminated')
                        return pm
                        #return self.iconmute_on
                except IndexError:
                    print('Bad index, Row: {}, Column:{}'.format(index.row(),index.column()))

        else:
            retval = QtCore.QVariant()

        return retval

    def setData(self, index, value, role):  # Set data in the model
        if role == QtCore.Qt.EditRole and index.isValid():
            print('In MyTableModel.setData, EditRole, index.row={}'.format(index.row()))
            self.arraydata[index.row()][index.column()] = value
            print('Return from rowCount: {0}'.format(self.rowCount(index)))
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        elif role == QtCore.Qt.DisplayRole:
            print('In MyTableModel.setData, DisplayRole')
        return False

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col < len(self.headerdata_horz):
                return QtCore.QVariant(self.headerdata_horz[col])
            else:
                return QtCore.QVariant('')
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if col < len(self.headerdata_vert):
                return QtCore.QVariant(self.headerdata_vert[col])
            else:
                return QtCore.QVariant('')

        return QtCore.QVariant()


class CharMap_MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(CharMap_MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.tableheader_horz = ['Tevya\nPatrickMcCarty']
        #self.tableheader_horz = self.get_header_horz()
        self.tableheader_vert = ['Page']
        #self.tableView.doubleClicked.connect(self.on_table_dblclick)
        #self.tableView.clicked.connect(self.on_table_click)
        self.tabledata = [['not much']]
        #self.get_table_data()
        self.leveldata = ['128']
        #self.get_level_data()
        self.tablemodel = MyTableModel(self.tabledata, self.leveldata, self.tableheader_horz, self.tableheader_vert, self)
#        self.tablemodel.dataChanged.connect(self.model_changed)
        self.tableView.setModel(self.tablemodel)
        self.tableView.setFont(QtGui.QFont('Helvetica', 12))
        # self.tableView.setItemDelegate(CellDelegate())
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        #self.tableView.resizeColumnsToContents()
        i = self.tableView.model().index(0, 0)

