#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess
import types
import argparse
import socket
from time import sleep

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import xml.etree.ElementTree as ET
from os import path

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

from Cues import cue_types, cue_subelements

from CueEdit_alt_ui import Ui_dlgEditCue

import styles

class EditCue(QDialog, Ui_dlgEditCue):
    def __init__(self, index, parent=None):
        QDialog.__init__(self, parent)
        #super(object, self).__init__(self)
        self.editidx = index
        self.setupUi(self)
        self.chgdict = {}
        for cuetypectlidx in range(cue_subelements.__len__()):
            if cue_subelements[cuetypectlidx] == 'CueType':
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
        #self.changeflag = False
        #self.plainTextEditAct.textChanged.connect(self.setChangeFlag)

    def accept(self):
        somethingchanged = True
        thing = []
        type_str = ''
        for i in range(cue_subelements.__len__()):
            if cue_subelements[i] == 'CueType':
                action_list = self.toolmenu.actions()
                for i in range(action_list.__len__()):
                    if action_list[i].isChecked():
                        if type_str == '':
                            type_str = action_list[i].text()
                        else:
                            type_str = '{0},{1}'.format(type_str, action_list[i].text())
            else:
                thing.append(self.edt_list[i].toPlainText())
        # action_list = self.toolmenu.actions()
        # for i in range(action_list.__len__()):
        #     if action_list[i].isChecked():
        #         if type_str == '':
        #             type_str = action_list[i].text()
        #         else:
        #             type_str = '{0},{1}'.format(type_str, action_list[i].text())
        # self.chgdict.update({'CueType':type_str})
        super(EditCue, self).accept()

    def reject(self):
        super(EditCue, self).reject()

    def getchange(self):
        return self.chglist

    def setROcueelements(self, RO_list):
        for i in range(cue_subelements.__len__()):
            if cue_subelements[i] in RO_list:
                self.edt_list[i].setReadOnly(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = EditCue(0)
    ui.setROcueelements(['Entrances', 'Exits', 'Levels'])
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    sys.exit(app.exec_())