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

import ui_ShowMixer
from ui_preferences import Ui_Preferences


import styles

CUE_IP = "127.0.0.1"
CUE_PORT = 5005
MXR_IP = "192.168.53.40"
MXR_PORT = 10023


cfgdict = cfg.toDict()
#print(cfgdict['Show']['folder'])

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class ShowPreferences(QDialog, Ui_Preferences):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # super(object, self).__init__(self)
        self.setupUi(self)

    def accept(self):
        x = self.cbxExitwCueEngine.checkState()
        print(x)
        if x == Qt.Checked:
            cfgdict['Prefs']['exitwithce'] = 'true'
        else:
            cfgdict['Prefs']['exitwithce'] = 'false'
        cfg.updateFromDict(cfgdict)
        cfg.write()
        super(ShowPreferences, self).accept()

    def reject(self):
        super(ShowPreferences, self).reject()

class ShowMxr(Show):
    '''
    The Show class contains the information and object that constitute a show
    '''


    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        super(ShowMxr, self).__init__(cfgdict)
        self.mixer = MixerConf(path.abspath(path.join(path.dirname(__file__), '../ShowControl/', cfgdict['Mixer']['file'])),self.show_conf.settings['mxrmfr'],self.show_conf.settings['mxrmodel'])
        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])

class ChanStripDlg(QtWidgets.QMainWindow, ui_ShowMixer.Ui_MainWindow):
    ChanStrip_MinWidth = 50

    def __init__(self, cuelistfile, parent=None):
        super(ChanStripDlg, self).__init__(parent)
        QtGui.QIcon.setThemeSearchPaths(styles.QLiSPIconsThemePaths)
        QtGui.QIcon.setThemeName(styles.QLiSPIconsThemeName)
        self.__index = 0
        #  Setup thread and udp to handle mixer I/O
        try:
            self.mxr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create mixer socket')
            sys.exit()
        self.comm_threads = []  # a list of threads in use for later use when app exits

        # setup sender thread
        self.mxr_sndrthread = CommHandlers.sender(self.mxr_sock, MXR_IP, MXR_PORT)
        self.mxr_sndrthread.sndrsignal.connect(self.sndrtestfunc)  # connect to custom signal called 'signal'
        self.mxr_sndrthread.finished.connect(self.sndrthreaddone)  # connect to buitlin signal 'finished'
        self.mxr_sndrthread.start()  # start the thread
        self.comm_threads.append(self.mxr_sndrthread)
        # setup receiver thread
        self.mxr_rcvrthread = CommHandlers.receiver(self.mxr_sock, MXR_IP, MXR_PORT)
        self.mxr_rcvrthread.rcvrsignal.connect(self.rcvrtestfunc)  # connect to custom signal called 'signal'
        self.mxr_rcvrthread.finished.connect(self.rcvrthreaddone)  # conect to buitlin signal 'finished'
        self.mxr_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.mxr_rcvrthread)
        self.externalclose = False


        #  Setup thread and udp to handle commands from CueEngine
        # setup command receiver socket
        try:
            self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create mixer socket')
            sys.exit()
        self.cmd_sock.bind((CUE_IP, CUE_PORT))
        # setup command receiver thread
        self.cmd_rcvrthread = CommHandlers.cmd_receiver(self.cmd_sock)
        self.cmd_rcvrthread.cmd_rcvrsignal.connect(self.cmd_rcvrtestfunc)  # connect to custom signal called 'signal'
        self.cmd_rcvrthread.finished.connect(self.cmd_rcvrthreaddone)  # connect to builtin signal 'finished'
        self.cmd_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.cmd_rcvrthread)

        self.setupUi(self)
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.tabWidget.setCurrentIndex(0)
        self.nextButton.clicked.connect(self.on_buttonNext_clicked)
        self.jumpButton.clicked.connect(self.on_buttonJump_clicked)
        self.tableView.clicked.connect(self.tableClicked)
        self.actionOpen_Show.triggered.connect(self.openShow)
        self.actionSave_Show.triggered.connect(self.saveShow)
        self.actionClose_Show.triggered.connect(self.closeShow)
        self.actionPreferences.triggered.connect(self.editpreferences)
        self.pref_dlg=ShowPreferences()


    def addChanStrip(self):
        #layout = self.stripgridLayout
        layout = self.stripgridLayout_2
        self.channumlabels = []
        self.mutes = []
        self.levs = []
        self.sliders = []
        self.scrbls = []
        for i in range(1,chans+1):
            print(str(i))
            #Add scribble for this channel Qt::AlignHCenter
            scrbl = QtWidgets.QLabel()
            scrbl.setObjectName('scr' + '{0:02}'.format(i))
            scrbl.setText('Scribble ' + '{0:02}'.format(i))
            scrbl.setAlignment(QtCore.Qt.AlignHCenter)
            scrbl.setMinimumWidth(self.ChanStrip_MinWidth)
            scrbl.setMinimumHeight(30)
            scrbl.setWordWrap(True)
            layout.addWidget(scrbl,4,i-1,1,1)
            self.scrbls.append(scrbl)

            #Add slider for this channel
            sldr = QtWidgets.QSlider(QtCore.Qt.Vertical)
            sldr.valueChanged.connect(self.sliderprint)
            sldr.setObjectName('{0:02}'.format(i))
            sldr.setMinimumSize(self.ChanStrip_MinWidth,200)
            sldr.setRange(0,1024)
            sldr.setTickPosition(3)
            sldr.setTickInterval(10)
            sldr.setSingleStep(2)
            layout.addWidget(sldr,3,i-1,1,1)
            self.sliders.append(sldr)

            #Add label for this channel level
            lev = QtWidgets.QLabel()
            lev.setObjectName('lev' + '{0:02}'.format(i))
            lev.setText('000')
            lev.setMinimumWidth(self.ChanStrip_MinWidth)
            lev.setAlignment(QtCore.Qt.AlignHCenter)
            layout.addWidget(lev,2,i-1,1,1)
            self.levs.append(lev)

            #Add mute button for this channel
            mute = QtWidgets.QPushButton()
            mute.setCheckable(True)            
            mute.clicked.connect(self.on_buttonMute_clicked)
            mute.setObjectName('{0:02}'.format(i))
            mute.setMinimumWidth(self.ChanStrip_MinWidth)
            layout.addWidget(mute,1,i-1,1,1)
            self.mutes.append(mute)

            #Add label for this channel
            lbl = QtWidgets.QLabel()
            lbl.setObjectName('{0:02}'.format(i))
            lbl.setText('Ch' + '{0:02}'.format(i))
            lbl.setMinimumWidth(self.ChanStrip_MinWidth)
            layout.addWidget(lbl,0,i-1,1,1)
            self.channumlabels.append(lbl)
        #self.setLayout(layout)
            # #for test add junk to tab 2
            tb2layout = self.stripgridLayout_3
            self.tb2channumlabels = []
            self.tb2mutes = []
            self.tb2levs = []
            self.tb2sliders = []
            self.tb2scrbls = []
            for i in range(1,chans+1):
                print(str(i))
                # Add scribble for this channel Qt::AlignHCenter
                scrbl = QtWidgets.QLabel()
                scrbl.setObjectName('tb2scr' + '{0:02}'.format(i))
                scrbl.setText('Scribble ' + '{0:02}'.format(i))
                scrbl.setAlignment(QtCore.Qt.AlignHCenter)
                scrbl.setMinimumWidth(self.ChanStrip_MinWidth)
                scrbl.setMinimumHeight(30)
                scrbl.setWordWrap(True)
                tb2layout.addWidget(scrbl,4,i-1,1,1)
                self.tb2scrbls.append(scrbl)

                # Add slider for this channel
                sldr = QtWidgets.QSlider(QtCore.Qt.Vertical)
                sldr.valueChanged.connect(self.sliderprint)
                sldr.setObjectName('sl{0:02}'.format(i))
                sldr.setMinimumSize(self.ChanStrip_MinWidth,200)
                sldr.setRange(0,1024)
                sldr.setTickPosition(3)
                sldr.setTickInterval(10)
                sldr.setSingleStep(2)
                tb2layout.addWidget(sldr,3,i-1,1,1)
                self.tb2sliders.append(sldr)

                # Add label for this channel level
                lev = QtWidgets.QLabel()
                lev.setObjectName('tb2lev' + '{0:02}'.format(i))
                lev.setText('000')
                lev.setMinimumWidth(self.ChanStrip_MinWidth)
                lev.setAlignment(QtCore.Qt.AlignHCenter)
                tb2layout.addWidget(lev,2,i-1,1,1)
                self.tb2levs.append(lev)

                # Add mute button for this channel
                mute = QtWidgets.QPushButton()
                mute.setCheckable(True)
                mute.clicked.connect(self.on_buttonMute_clicked)
                mute.setObjectName('tb2mt{0:02}'.format(i))
                mute.setMinimumWidth(self.ChanStrip_MinWidth)
                tb2layout.addWidget(mute,1,i-1,1,1)
                self.tb2mutes.append(mute)

                # Add label for this channel
                lbl = QtWidgets.QLabel()
                lbl.setObjectName('tb2ch{0:02}'.format(i))
                lbl.setText('Ch' + '{0:02}'.format(i))
                lbl.setMinimumWidth(self.ChanStrip_MinWidth)
                tb2layout.addWidget(lbl,0,i-1,1,1)
                self.tb2channumlabels.append(lbl)

    def sliderprint(self, val):
        sending_slider = self.sender()
        scrLbl = self.findChild(QtWidgets.QLabel, name='lev' + sending_slider.objectName())
        scrLbl.setText('{0:03}'.format(val))
        osc_add = The_Show.mixer.inputsliders['Ch' + '{0:02}'.format(int(sending_slider.objectName()))].fadercmd.replace('#', sending_slider.objectName())
        msg = osc_message_builder.OscMessageBuilder(address=osc_add)
        msg.add_arg(translate(val, 0,1024,0.0, 1.0))
        msg = msg.build()
        self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def on_buttonNext_clicked(self):
        self.next_cue()

    def on_buttonJump_clicked(self):
        self.execute_cue(The_Show.cues.selectedcueindex)

    def execute_cue(self, num):
        The_Show.cues.previouscueindex = The_Show.cues.currentcueindex
        The_Show.cues.currentcueindex = num
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
#        The_Show.cues.setcurrentcuestate(The_Show.cues.currentcueindex)

        mute_changes = The_Show.cues.get_cue_mute_state(The_Show.cues.currentcueindex)
        # iterate through mute changes, if any
        if mute_changes != None:
            for key, value in mute_changes.items():
                channum = int(key.strip('ch'))
                mute = self.findChild(QtWidgets.QPushButton, name='{0:02}'.format(channum))
                osc_add = The_Show.mixer.inputsliders['Ch' + '{0:02}'.format(channum)].mutecmd.replace('#', mute.objectName())
                msg = osc_message_builder.OscMessageBuilder(address=osc_add)
                if value == 1:
                    mute.setChecked(False)
                    msg.add_arg(The_Show.mixer.mutestyle['unmute'])
                else:
                    mute.setChecked(True)
                    msg.add_arg(The_Show.mixer.mutestyle['mute'])
                msg = msg.build()
                self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

        levels = The_Show.cues.get_cue_levels(The_Show.cues.currentcueindex)
        if levels != None:
            for key, value in levels.items():
                channum = int(key.strip('ch'))
            #for ctlcnt in range(1, The_Show.mixer.inputsliders.__len__() + 1):
                sldr = self.findChild(QtWidgets.QSlider, name='{0:02}'.format(channum))
                sldlev = translate(int(value), 0, 1024, 0.0, 1.0)
                currentlevel = translate(sldr.sliderPosition(), 0, 1024, 0.0, 1.0)
                currentlevval = sldr.value()
                print('current level: {}'.format(currentlevel))
                print('sldlev: {}'.format(sldlev))
                print('value: {}'.format(value))
                if currentlevel != sldlev:
                    print('change')
                    osc_add = The_Show.mixer.inputsliders['Ch' + '{0:02}'.format(channum)].fadercmd.replace('#', sldr.objectName())
                    msg = osc_message_builder.OscMessageBuilder(address=osc_add)
                    sldr.setSliderPosition(int(value))
                    msg.add_arg(sldlev)
                    msg = msg.build()
                    self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def next_cue(self):
        nextmxrcuefound = False
        index = The_Show.cues.currentcueindex
        while not nextmxrcuefound:
            index += 1
            if index < The_Show.cues.cuecount:
                if The_Show.cues.getcuetype(index) == 'Mixer':
                    nextmxrcuefound = True
                    self.execute_cue(index)
            else:
                return

    def initmutes(self):
        
        for ctlcnt in range(1, The_Show.mixer.inputsliders.__len__() + 1):
            mute = self.findChild(QtWidgets.QPushButton, name='{0:02}'.format(ctlcnt))
            osc_add = The_Show.mixer.inputsliders['Ch' + '{0:02}'.format(ctlcnt)].mutecmd.replace('#', mute.objectName())
            msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            mute.setChecked(True)
            msg.add_arg(The_Show.mixer.mutestyle['mute'])
            msg = msg.build()
            self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def initlevels(self):
        for ctlcnt in range(1, The_Show.mixer.inputsliders.__len__() + 1):
            sldr = self.findChild(QtWidgets.QSlider, name='{0:02}'.format(ctlcnt))
            osc_add = '/ch/' + sldr.objectName() + '/mix/fader'
            osc_add = The_Show.mixer.inputsliders['Ch' + '{0:02}'.format(ctlcnt)].fadercmd.replace('#', sldr.objectName())
            msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            msg.add_arg(translate(0, 0, 1024, 0.0, 1.0))
            msg = msg.build()
            self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def on_buttonMute_clicked(self):
        mbtn=self.sender()
        print(mbtn.objectName())
        chkd = mbtn.isChecked()
        dwn=mbtn.isDown()
        osc_add='/ch/' + mbtn.objectName() + '/mix/on'
        print(osc_add)
        print(chkd)
        print(dwn)
        msg = osc_message_builder.OscMessageBuilder(address=osc_add)
        if mbtn.isChecked():
            msg.add_arg(The_Show.mixer.mutestyle['mute'])
        else:
            msg.add_arg(The_Show.mixer.mutestyle['unmute'])

        msg = msg.build()
        #client.send(msg)
        self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def on_buttonUnmute_clicked(self):
        spin=1
        chnum=self.spinChNum.value()
        print(chnum)
        print(spin)
        osc_add='/ch/' + '{0:02}'.format(chnum) + '/mix/on'
#        osc_add='/ch/02/mix/on'
        msg = osc_message_builder.OscMessageBuilder(address=osc_add)
        msg.add_arg(1)
        msg = msg.build()
        #client.send(msg)
        self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)

    def setfirstcue(self):
        tblvw = self.findChild(QtWidgets.QTableView)
        tblvw.selectRow(The_Show.cues.currentcueindex)
        self.execute_cue(The_Show.cues.currentcueindex)

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
        self.set_scribble(The_Show.chrchnmap.maplist)
        self.setWindowTitle(The_Show.show_conf.settings['name'])
        self.initmutes()
        self.initlevels()
        self.disptext()
        self.setfirstcue()

    def saveShow(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        print(fname)

    def closeShow(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        print(fname)

    def editpreferences(self):
        if cfgdict['Prefs']['exitwithce'] == 'true':
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Checked)
        else:
            self.pref_dlg.cbxExitwCueEngine.setCheckState(Qt.Unchecked)
        self.pref_dlg.show()
        #self.itb = QDialog()
        #self.ui_prefdlg = Ui_Preferences()
        #self.ui_prefdlg.setupUi(self.itb)
        #self.itb.show()

    def set_scribble(self, mxrmap):
        charcount = int(mxrmap.getroot().attrib['charcount'])

        chans = mxrmap.findall('input')
        for chan in chans:
            cnum = int(chan.attrib['chan'])
            osc_add='/ch/' + '{0:02}'.format(cnum) + '/config/name'
            msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            tmpstr = chan.attrib['actor'][:5]
            #print('Temp String: ' + tmpstr)
            msg.add_arg(chan.attrib['actor'][:5])
            msg = msg.build()
            #client.send(msg)
            self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)
            thislbl = self.findChild(QtWidgets.QLabel, name='scr'+ '{0:02}'.format(cnum))
            thislbl.setText(tmpstr)

    def disptext(self):
        self.get_table_data()
        # set the table model
        header = ['Cue', 'Id', 'Act', 'Scene', 'Page','Title','Dialog/Prompt']
        tablemodel = MyTableModel(self.tabledata, header, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        #self.tableView.connect(self.tableClicked, QtCore.SIGNAL("clicked()"))

    def get_table_data(self):
        qs = The_Show.cues.cuelist.findall('cue')
        self.tabledata =[]
        for q in qs:
            #print(q.attrib)
            #print(q.find('Move').text)
            self.tabledata.append([q.find('Move').text,
                     q.find('Id').text,
                     q.find('Scene').text,
                     q.find('Page').text,
                     q.find('Title').text,
                     q.find('Cue').text])
        #print(self.tabledata)

    def tableClicked(self, modelidx):
        rowidx = modelidx.row()
        The_Show.cues.selectedcueindex = rowidx
        self.tableView.selectRow(The_Show.cues.selectedcueindex)
        print('table clicked, row{}'.format(rowidx))

    def closeEvent(self, event):
        """..."""
        reply = self.confirmQuit()
        if reply == QMessageBox.Yes:
            self.stopthreads()
            event.accept()
        else:
            event.ignore()

    def confirmQuit(self):
        """..."""
        if self.externalclose:
            reply =  QMessageBox.Yes
        else:
            reply = QMessageBox.question(self, 'Confirm Quit',
                "Are you sure you want to quit?", QMessageBox.Yes |
                QMessageBox.No, QMessageBox.No)
        return reply

    '''sender functions'''
    '''testfucn
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def sndrtestfunc(self, sigstr):
        """..."""
        print(sigstr)
        self.statusBar().showMessage(sigstr)

    def cmd_rcvrtestfunc(self, sigstr):
        """..."""
        msg = osc_message.OscMessage(sigstr)
        print(msg.address)
        for param in msg.params:
            print(param)
        if msg.address == '/cue':
            if msg.params[0] == "NEXT":
                self.next_cue()
        elif msg.address == '/cue/#':
            self.execute_cue(msg.params[0])
        elif msg.address == '/cue/quit':
            self.externalclose = True
            self.close()

    def sndrqput(self, msg):
        """..."""
        self.sndrthread.queue_msg(msg)

    '''receiver functions
        - gets called when the signal called 'signal' is emitted from thread called 'thread' '''
    def rcvrtestfunc(self, sigstr):
        """..."""
        print(sigstr)
        self.statusBar().showMessage(sigstr)

    '''gets called by main to tell the thread to stop'''
    def stopthreads(self):
        """..."""
        for t in self.comm_threads:
            t.setstopflag()
            t.wait(500)

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def sndrthreaddone(self):
        """..."""
        print('sender thread done')

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def rcvrthreaddone(self):
        """..."""
        print('receiver thread done')

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def cmd_rcvrthreaddone(self):
        """..."""
        print('command receiver thread done')



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
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def setData(self, index, value, role):
        pass         # not sure what to put here

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()


The_Show = ShowMxr(cfgdict)
The_Show.displayShow()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(""" QPushButton {color: blue;
#                          background-color: yellow;
#                          selection-color: blue;
#                          selection-background-color: green;}""")
    #app.setStyleSheet("QPushButton {pressed-color: red }")
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = len(The_Show.mixer.inputsliders)
    #ui = ChanStripDlg(path.abspath(path.join(path.dirname(__file__))) + '/Scrooge Moves.xml')
    ui = ChanStripDlg(path.abspath(path.join(path.dirname(cfgdict['Show']['folder']))))
    ui.resize(chans*ui.ChanStrip_MinWidth,800)
    ui.addChanStrip()
    ui.disptext()
    ui.set_scribble(The_Show.chrchnmap.maplist)
    ui.initmutes()
    ui.initlevels()
    ui.setfirstcue()
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
    args = parser.parse_args()

    ui.show()
    sys.exit(app.exec_())