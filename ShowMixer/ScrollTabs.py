#!/usr/bin/env python3
__author__ = 'mac'

import argparse
import inspect
import os
import socket
import sys
from os import path

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
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

from MixerConf import MixerConf
from MixerMap import MixerCharMap

import ui_ScrollTabs
from ui_preferences import Ui_Preferences


import styles


cfgdict = cfg.toDict()


class ChanStripDlg(QtWidgets.QMainWindow, ui_ScrollTabs.Ui_MainWindow):
    ChanStrip_MinWidth = 50

    def __init__(self, cuelistfile, parent=None):
        super(ChanStripDlg, self).__init__(parent)
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        self.setupUi(self)
        self.tablist = []
        self.tablistvertlayout = []
        self.tabgridlayoutlist = []
        self.tabstripgridlist = []
        self.scrollArea = []
        self.scrollAreaWidgetContents = []

    def addChanStrip(self):
        scrbls = []
        for idx in range(self.tabWidget.count()):
            print(idx)
            # get the tab widget that was made as a place holder in Qt Designer
            #self.tablist.append(self.tabWidget.currentWidget())
        for idx in range(0, 3):
            self.tablist.append(QtWidgets.QWidget())  # create a tab
            self.tablist[idx].setMinimumSize(QtCore.QSize(0, 0))
            self.tablist[idx].setObjectName("Pg {}".format(idx))
            # put a vertical layout on the tab
            self.tablistvertlayout.append(QtWidgets.QVBoxLayout(self.tablist[idx]))
            self.tablistvertlayout[idx].setContentsMargins(10, 10, 10, 10)
            self.tablistvertlayout[idx].setObjectName("verticalLayout")

            self.scrollArea.append(QtWidgets.QScrollArea(self.tablist[idx]))  # add a scrollarea to the tab
            self.scrollArea[idx].setGeometry(QtCore.QRect(19, 20, 1200, 600))  # set overall size of the scroll area
            #self.scrollArea[idx].setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            #self.scrollArea[idx].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea[idx].setWidgetResizable(True)
            self.scrollArea[idx].setObjectName("scrollArea")
            self.scrollAreaWidgetContents.append(QtWidgets.QWidget())
            self.scrollAreaWidgetContents[idx].setGeometry(QtCore.QRect(0, 0, 1200, 400))  # set the size of the area under the scrol area
            self.scrollAreaWidgetContents[idx].setObjectName('scrollAreaWidgetContents_{}'.format(idx))
            # put a grid layout on the scroll container widget
            self.tabgridlayoutlist.append(QtWidgets.QGridLayout(self.scrollAreaWidgetContents[idx]))
            self.tabgridlayoutlist[idx].setContentsMargins(0, 0, 0, 0)
            self.tabgridlayoutlist[idx].setObjectName("gridLayout{}".format(idx))
            self.tabstripgridlist.append(QtWidgets.QGridLayout())
            self.tabstripgridlist[idx].setObjectName("stripgridLayout{}".format(idx))
            self.tabgridlayoutlist[idx].addLayout(self.tabstripgridlist[idx], 0, 0, 1, 1)
            self.tabWidget.insertTab(idx, self.tablist[idx], "Tab {}".format(idx))
            for chn in range(1,40):
                scrbl = QtWidgets.QLabel()
                scrbl.setObjectName('scr{0:02}'.format(chn))
                scrbl.setText('M{0} Scribble {1:02}'.format(idx,chn))
                scrbl.setAlignment(QtCore.Qt.AlignHCenter)
                scrbl.setMinimumWidth(self.ChanStrip_MinWidth)
                scrbl.setMinimumHeight(30)
                scrbl.setWordWrap(True)
                self.tabstripgridlist[idx].addWidget(scrbl,4,chn,1,1)
                # Add slider for this channel
                sldr = QtWidgets.QSlider(QtCore.Qt.Vertical)
                sldr.setObjectName('{0:02}'.format(chn+1))
                sldr.setMinimumSize(self.ChanStrip_MinWidth,200)
                sldr.setRange(0,1024)
                sldr.setTickPosition(3)
                sldr.setTickInterval(10)
                sldr.setSingleStep(2)
                self.tabstripgridlist[idx].addWidget(sldr, 3, chn, 1, 1)

                #self.scrbls.append(scrbl)
            self.scrollArea[idx].setWidget(self.scrollAreaWidgetContents[idx])
        print(self.tabWidget.count())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    #ui = ChanStripMainWindow(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui = ChanStripDlg(path.abspath(path.join(path.dirname(cfgdict['Show']['folder']))))
    ui.addChanStrip()
    ui.resize(32 * ui.ChanStrip_MinWidth, 800)
    # ui.disptext()
    # ui.set_scribble(The_Show.chrchnmap.maplist)
    # ui.initmutes()
    # ui.initlevels()
    # ui.setfirstcue()
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    sys.exit(app.exec_())