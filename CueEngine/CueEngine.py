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

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)

#from ShowConf import ShowConf
#from Cues import CueList
#from MixerConf import MixerConf
from Show import Show
import CommHandlers


import CueEngine_ui
from CueEdit_ui import Ui_dlgEditCue

from pythonosc import osc_message_builder

CUE_IP = "127.0.0.1"
CUE_PORT = 5005


import configuration as cfg

import styles

cfgdict = cfg.toDict()

columndict = {'Number': 0, 'Act':1, 'Scene':2, 'Page':3, 'ID':4, 'Title':5,'Dialog/Prompt':6}

class EditCue(QDialog, Ui_dlgEditCue):
    def __init__(self, index, parent=None):
        QDialog.__init__(self, parent)
        #super(object, self).__init__(self)
        self.editidx = index
        self.setupUi(self)
        self.chgdict = {}
        #self.changeflag = False
        #self.plainTextEditAct.textChanged.connect(self.setChangeFlag)

    def accept(self):
        somethingchanged = False
        for dobj in self.findChildren(QtWidgets.QPlainTextEdit):
            tobj = dobj.document()
            if tobj.isModified():
                somethingchanged = True
            #print(dobj)
        if somethingchanged:
            print('editidx',self.editidx)
            for dobj in self.findChildren(QtWidgets.QPlainTextEdit):
                objnam = dobj.objectName()
                flddoc = dobj.documentTitle()
                print('documentTitle: ', flddoc)
                print('object name: ', objnam)
                fldtxt = dobj.toPlainText()
                self.chgdict.update({flddoc:fldtxt})

        print('Something changed: ', somethingchanged)
        docobj = self.plainTextEditTitle.document()
        print('Window modded:',self.isWindowModified())
        #print(docobj.isModified())
        # if docobj.isModified():
        #     print(self.plainTextEditTitle.toPlainText())
        #     self.chgdict.update()
        #     #save changes
        #     #save to cue file
        #     #redisplay
        # self.chglist.append('ddd')
        # #rowlist = self.sender().tableview #.tabledata[self.editidx]
        # #print('rowlist', rowlist)
        super(EditCue, self).accept()

    def reject(self):
        super(EditCue, self).reject()

    def getchange(self):
        return self.chglist

    #def setChangeFlag(self):
    #    print('textchanged')
    #    self.changeflag = True

class CueDlg(QtWidgets.QMainWindow, CueEngine_ui.Ui_MainWindow):

    def __init__(self, cuelistfile, parent=None):
        super(CueDlg, self).__init__(parent)
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        self.setupUi(self)
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.nextButton.clicked.connect(self.on_buttonNext_clicked)
        self.prevButton.clicked.connect(self.on_buttonPrev_clicked)
        self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        self.tableView.doubleClicked.connect(self.on_table_dblclick)
        self.tableView.clicked.connect(self.on_table_click)
        self.tabledata = []
        self.actionOpen_Show.triggered.connect(self.openShow)
        self.actionSave.triggered.connect(self.saveShow)
        self.action_Stage_Cues.triggered.connect(self.ShowStageCues)
        self.StageCuesVisible = True
        self.action_Sound_FX_Cues.triggered.connect(self.ShowSoundFXCues)
        self.SoundFXCuesVisible = True
        self.action_Mixer_Cues.triggered.connect(self.ShowMixerCues)
        self.MixerCuesVisible = True
        self.action_Lighting_Cues.triggered.connect(self.ShowLightCues)
        self.LightCuesVisible = True
        self.action_Sound_FX.triggered.connect(self.ShowSFXApp)
        self.action_Mixer.triggered.connect(self.ShowMxrApp)
        self.SFXAppProc = None
        self.MxrAppProc = None

        self.editcuedlg = EditCue('0')
        try:
            self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create mixer socket')
            sys.exit()
        self.comm_threads = []  # a list of threads in use for later use when app exits

        # setup sender thread
        self.mxr_sndrthread = CommHandlers.sender(self.mxr_sock, CUE_IP, CUE_PORT)
        self.mxr_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
        self.mxr_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
        self.mxr_sndrthread.start()  # start the thread
        self.comm_threads.append(self.mxr_sndrthread)

    def on_buttonNext_clicked(self):
        print('Next')
        tblvw = self.findChild(QtWidgets.QTableView)
        selections = tblvw.selectedIndexes()  # selections is a list that contains an entry for each column in the row
        tblrow = selections[0].row()  # the row is the index to the tabledata for the cue
        tblrow += 1  # next row
        cuedata = self.tabledata[tblrow]  # data for next row
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex  # save previous cue index
        The_Show.cues.currentcueindex = int(self.tabledata[tblrow][0])  # new current cue index is the cue we want to execute
        tblvw.selectRow(tblrow)  # select the next row
        self.dispatch_cue()  # execute the cue

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
        if The_Show.cues.getcuetype(The_Show.cues.currentcueindex) == 'Mixer':
            msg = osc_message_builder.OscMessageBuilder(address='/cue/#')
            msg.add_arg(The_Show.cues.currentcueindex)
            msg = msg.build()
            self.mxr_sndrthread.queue_msg(msg)

    def on_table_click(self,index):
        """index is the row in the tableview (thus the row of the tabledata)"""
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(index.row())
        cuedata = self.tabledata[index.row()]
        The_Show.cues.selectedcueindex = int(self.tabledata[index.row()][0])

    def on_table_dblclick(self,index):
        print(index.row())
        self.editcuedlg.editidx = index.row()
        print(self.tabledata[index.row()])
        rowlist = self.tabledata[index.row()]
        self.editcuedlg.plainTextEditCueNum.setPlainText(rowlist[0])
        self.editcuedlg.plainTextEditCueNum.setDocumentTitle('Cue Number')

        self.editcuedlg.plainTextEditAct.setPlainText(rowlist[1])
        self.editcuedlg.plainTextEditAct.setDocumentTitle('Act')

        self.editcuedlg.plainTextEditScene.setPlainText(rowlist[2])
        self.editcuedlg.plainTextEditScene.setDocumentTitle('Scene')

        self.editcuedlg.plainTextEditPage.setPlainText(rowlist[3])
        self.editcuedlg.plainTextEditPage.setDocumentTitle('Page')

        self.editcuedlg.plainTextEditId.setPlainText(rowlist[4])
        self.editcuedlg.plainTextEditId.setDocumentTitle('ID')

        self.editcuedlg.plainTextEditTitle.setPlainText(rowlist[5])
        self.editcuedlg.plainTextEditTitle.setDocumentTitle('Title')

        self.editcuedlg.plainTextEditPrompt.setPlainText(rowlist[6])
        self.editcuedlg.plainTextEditPrompt.setDocumentTitle('Dialog/Prompt')

        #self.editcuedlg.show()
        self.editcuedlg.exec_()
        changedict = self.editcuedlg.chgdict
        print('returned list:',self.editcuedlg.chgdict)
        if changedict:
            print('Updating table.')
            for key, newdata in changedict.items():
                print('--------------',key,newdata)
                for coltxt, colidx in columndict.items():
                    if coltxt in key:
                        print('colidx: ', colidx, ' row: ', index.row())
                        print('coltxt: ',coltxt, ' newdata: ',newdata)
                        self.tabledata[index.row()][colidx] = newdata

                        break
        else:
            print('No table changes')
        print(self.tabledata[index.row()])
        The_Show.cues.updatecue(index.row(),self.tabledata[index.row()])
        The_Show.cues.savecuelist()

    def setfirstcue(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)

    def disptext(self):
        self.get_table_data()
        # set the table model
        header = ['Cue Number', 'Act', 'Scene', 'Page', 'ID', 'Title','Dialog/Prompt','Cue Type']
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()

    def get_table_data(self):
        qs = The_Show.cues.cuelist.findall('cue')
        self.tabledata =[]
        for q in qs:
            #print(q.attrib)
            #print(q.find('Move').text)
            if q.find('CueType').text == 'Sound' and self.SoundFXCuesVisible:
                self.append_table_data(q)
            elif q.find('CueType').text == 'Mixer' and self.MixerCuesVisible:
                self.append_table_data(q)
            elif q.find('CueType').text == 'Stage' and self.StageCuesVisible:
                self.append_table_data(q)
            elif q.find('CueType').text == 'Light' and self.LightCuesVisible:
                self.append_table_data(q)
        print(self.tabledata)

    def append_table_data(self, q):
        self.tabledata.append(
            [q.find('Move').text,
             q.find('Act').text,
             q.find('Scene').text,
             q.find('Page').text,
             q.find('Id').text,
             q.find('Title').text,
             q.find('Cue').text,
             q.find('CueType').text])

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
        The_Show.loadNewShow(fname[0])
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.disptext()
        self.setfirstcue()
        self.setWindowTitle(self.show_conf.settings('name'))

    def saveShow(self):
        print("Save show.")
        pass

    def ShowStageCues(self):
        """Toggle visibility of stage cues"""
        if self.StageCuesVisible:
            self.StageCuesVisible = False
        else:
            self.StageCuesVisible = True
        self.disptext()
        self.setfirstcue()

    def ShowSoundFXCues(self):
        """Toggle visibility of sound cues"""
        if self.SoundFXCuesVisible:
            self.SoundFXCuesVisible = False
        else:
            self.SoundFXCuesVisible = True
        self.disptext()
        self.setfirstcue()

    def ShowMixerCues(self):
        """Toggle visibility of sound cues"""
        if self.MixerCuesVisible:
            self.MixerCuesVisible = False
        else:
            self.MixerCuesVisible = True
        self.disptext()
        self.setfirstcue()

    def ShowLightCues(self):
        """Toggle visibility of Light cues"""
        if self.LightCuesVisible:
            self.LightCuesVisible = False
        else:
            self.LightCuesVisible = True
        self.disptext()
        self.setfirstcue()


    def ShowSFXApp(self):
        print("Launch SFX App.")
        self.SFXAppProc = subprocess.Popen(['python3', '/home/mac/PycharmProjs/linux-show-player/linux-show-player', '-f', '/home/mac/Shows/Pauline/sfx.lsp'])

    def EndSFXApp(self):
        self.SFXAppProc.terminate()

    def ShowMxrApp(self):
        if self.MxrAppProc != None:
            msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
            msg.add_arg(The_Show.cues.currentcueindex)
            msg = msg.build()
            self.mxr_sndrthread.queue_msg(msg)
            self.MxrAppProc = None
        else:
            print("Launch Mxr App.")
            self.MxrAppProc = subprocess.Popen(['python3', '/home/mac/PycharmProjs/ShowControl/ShowMixer/ShowMixer.py'])

    def closeEvent(self, event):
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            if self.SFXAppProc != None:
                savereply = QMessageBox.warning(self, 'Warning',
                    "Save changes in FX player before continuing!", QMessageBox.Ok, QMessageBox.Ok)
                self.EndSFXApp()
            try:  # if MxrAppProc was never created it will throw and exception on the next line...so this is probabaly not the right way...
                if self.MxrAppProc != None:
                    msg = osc_message_builder.OscMessageBuilder(address='/cue/quit')
                    msg.add_arg(The_Show.cues.currentcueindex)
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg)
                    sleep(2)  # wait for message to be sent before killing threads
            except:
                pass
            self.stopthreads()
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
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

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def sndrthreaddone(self):
        """..."""
        print('sender thread done')


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




#The_Show = Show(path.abspath(path.join(path.dirname(__file__))) + '/')
The_Show = Show(cfgdict)
The_Show.displayShow()


if __name__ == "__main__":
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
    ui.setfirstcue()
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    sys.exit(app.exec_())