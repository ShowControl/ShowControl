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
import time
import psutil

logging.basicConfig(filename='ShowMixer.log', filemode='w', level=logging.DEBUG)

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from pythonosc import osc_message
from pythonosc import osc_message_builder

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET



currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print('currentdir: ' + currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
showmixerdir = os.path.dirname(currentdir) + '/ShowMixer'
print('syblingdir:' + syblingdir)
parentdir = os.path.dirname(currentdir)
print('parendir: ' + parentdir)
print('sys.path before: {}'.format(sys.path))
sys.path.insert(0,syblingdir)
sys.path.insert(0,showmixerdir)

print('sys.path: {}'.format(sys.path))

from Show import Show
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

from MixerConf import MixerConf
from MixerMap import MixerCharMap



#import styles

asparser = argparse.ArgumentParser()


import MuteMap_ui
import styles

def has_handle(fpath):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return False

class CommAddresses:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT

class MyWatcher(QFileSystemWatcher):
    def __init__(self):
        super(MyWatcher, self).__init__()
        self.installEventFilter(self.watcher_event_filter)

    def watcher_event_filter(self, event):
        print('Event type: {}'.format(event.type))

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

        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mixermap'])


class MuteMapDlg(QtWidgets.QDialog, MuteMap_ui.Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('MuteMap - {}'.format(The_Show.show_conf.settings['title']))

        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(screen.x() + int(0.05 * screen.width()), screen.y(), screen.width() * 0.98, screen.height() * 0.9)
        #self.setGeometry(10, screen.y(), 1500,screen.height() * 0.9)
        self.move(1900,10)

        self.ShowMixerAppDev = CommAddresses(The_Show.show_conf.equipment['program']['ShowMixer']['IP_address'],
                                       int(The_Show.show_conf.equipment['program']['ShowMixer']['port']))
        logging.info('ShowMixer receives commands from IP: {} PORT: {}'.format(self.ShowMixerAppDev.IP,
                                                                               self.ShowMixerAppDev.PORT))
        self.CueAppDev = CommAddresses(The_Show.show_conf.equipment['program']['CueEngine']['IP_address'],
                                      int(The_Show.show_conf.equipment['program']['CueEngine']['port']))
        logging.info('CueEngine response will be sent to IP: {} PORT: {}'.format(self.CueAppDev.IP, self.CueAppDev.PORT))

        self.MuteMapAppDev = CommAddresses(The_Show.show_conf.equipment['program']['MuteMap']['IP_address'],
                                      int(The_Show.show_conf.equipment['program']['MuteMap']['port']))
        logging.info('CueEngine response will be sent to IP: {} PORT: {}'.format(self.MuteMapAppDev.IP, self.MuteMapAppDev.PORT))

        self.comm_threads = []  # a list of all threads in use for later use when app exits

        #  Setup thread and udp to handle commands from CueEngine
        # setup command receiver socket
        try:
            self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create mixer socket')  #todo-mac need exception and logging here
            sys.exit()
        #self.cmd_sock.bind((CUE_IP, CUE_PORT))
        self.cmd_sock.bind((self.MuteMapAppDev.IP, self.MuteMapAppDev.PORT))
        # setup command receiver thread
        self.cmd_rcvrthread = CommHandlers.cmd_receiver(self.cmd_sock)
        self.cmd_rcvrthread.cmd_rcvrsignal.connect(self.cmd_rcvrtestfunc)  # connect to custom signal called 'signal'
        self.cmd_rcvrthread.finished.connect(self.cmd_rcvrthreaddone)  # connect to builtin signal 'finished'
        self.cmd_rcvrthread.start()  # start the thread
        self.comm_threads.append(self.cmd_rcvrthread)
        self.externalclose = False


        self.tableheader_horz = self.get_header_horz()
        self.tableheader_vert = []
        self.tableView.doubleClicked.connect(self.on_table_dblclick)
        self.tableView.clicked.connect(self.on_table_click)
        self.get_table_data()
        self.tablemodel = MyTableModel(self.tabledata, self.tableheader_horz, self.tableheader_vert, self)
        self.tableView.setModel(self.tablemodel)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        i = self.tableView.model().index(0, 0)
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(The_Show.show_conf.cfgdict['configuration']['project']['folder'] + '/' + The_Show.show_conf.settings['cues']['href1'])

        self.watcher.fileChanged.connect(self.cue_file_modified)

    def cue_file_modified(self, path):
        print('{} changed!'.format(path))
        sndr = self.sender()
        # watcher sends signal as soon as file is opened by other process
        # and this signal also gets called twice for each write, not sure why
        # added following handle check to make sure writing process had completed
        wait_count = 0
        while has_handle(path) and wait_count < 10:
            time.sleep(0.1)
            wait_count += 1
        The_Show.reloadShow(cfg.cfgdict)
        self.tablemodel = None
        self.tableheader_horz = self.get_header_horz()
        self.tableheader_vert = []
        self.get_table_data()
        self.tablemodel = MyTableModel(self.tabledata, self.tableheader_horz, self.tableheader_vert, self)
        self.tableView.setModel(self.tablemodel)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)

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
            self.append_table_data(q)
        return

    def append_table_data(self, q):
        tmp_list = '{0:03}'.format(int(q.attrib['num']))
        dirty_mutes_list = q.find('Mutes').text.split(',')
        mutes_list = [s.strip() for s in dirty_mutes_list]
        mutes_list_sorted = self.sort_controls(mutes_list)
        #row_list = tmp_list + mutes_list_sorted
        row_list = mutes_list_sorted
        self.tabledata.append(row_list)
        self.tableheader_vert.append(tmp_list)

    def sort_controls(self, control_list=[]):
        chlist = []
        auxlist = []
        buslist = []
        mainlist = []
        for control in control_list:
            if 'bus' in control:
                buslist.append(control)
            elif 'aux' in control:
                auxlist.append(control)
            elif 'main' in control:
                mainlist.append(control)
            elif 'ch' in control:
                chlist.append(control)
        buslist = sorted(buslist)
        auxlist = sorted(auxlist)
        mainlist = sorted(mainlist)
        chlist = sorted(chlist)
        sorted_controls = chlist + auxlist + buslist + mainlist
        return sorted_controls

    def on_table_dblclick(self):
        print('Table double click')
        return

    def on_table_click(self, modelidx):
        print('Table click row: {}, col:{}'.format(modelidx.row(), modelidx.column()))
        if modelidx.column() == 0:
            self.tableView.setCurrentIndex(modelidx)
            return
        curval = self.tablemodel.arraydata[modelidx.row()][modelidx.column()]
        if curval[-1] == '0':
            self.tablemodel.setData(modelidx, curval[:-1] + '1', Qt.EditRole)
        elif curval[-1] == '1':
            self.tablemodel.setData(modelidx, curval[:-1] + '0', Qt.EditRole)
        return

    def get_header_horz(self):
        char_count = The_Show.chrchnmap.getmixermapcharcount('f40e83e1-f69f-4fd7-bd22-5baae2d1fd07')
        input_element_list = The_Show.chrchnmap.getmixermapinputs('f40e83e1-f69f-4fd7-bd22-5baae2d1fd07')
        mixer_chans = The_Show.mixers[0].mxrconsole.__len__()
        char_list = []
        chn_hdr_list = []
        for chn_idx in range(0, mixer_chans):
            try:
                chn_hdr = input_element_list[chn_idx].get('char')
            except IndexError:
                #print(The_Show.mixers[0].mxrconsole[chn_idx]['name'])
                chn_hdr = The_Show.mixers[0].mxrconsole[chn_idx]['name']
            chn_hdr_list.append(chn_hdr)
        # for input in input_element_list:
        #     mixer_id = input.get('mixerid')
        #     chan = input.get('chan')
        #     char = input.get('char')
        #     char_list.append(char)
        # return char_list
        return chn_hdr_list

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

    def cmd_rcvrtestfunc(self, sigstr):
        """..."""
        msg = osc_message.OscMessage(sigstr)
        print('In cmd_rcvrtestfunc, OSC address: {}'.format(msg.address))
        for idx, param in enumerate(msg.params):
            print('param[{0}]: {1}'.format(idx, param))
        if msg.address == '/cue':
            if msg.params[0] == "Next":
                print('OSC msg.params[0]: {}'.format(msg.params[0]))
                self.next_cue()
        elif msg.address == '/cue/#':
            print('cue # : {}'.format(msg.params[0]))
            #self.execute_cue(msg.params[0])
            The_Show.cues.currentcueindex = int(msg.params[0])
            self.tableView.setCurrentIndex(self.tablemodel.createIndex(The_Show.cues.currentcueindex, 0))
            #self.tableView.showRow(The_Show.cues.currentcueindex)
        elif msg.address == '/cue/uuid':
            print('cue uuid : {}'.format(msg.params[0]))
            #self.execute_cue_uuid(msg.params[0])
        elif msg.address == '/cue/quit':
            print('cue external quit')
            self.externalclose = True
            self.close()

    '''called when builtin signal 'finished' is emitted by worker thread'''
    def cmd_rcvrthreaddone(self):
        """..."""
        print('command receiver thread done')
    '''gets called by main to tell the thread to stop'''

    def stopthreads(self):
        """..."""
        for t in self.comm_threads:
            t.setstopflag()
        t.wait(500)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata_horz, headerdata_vert, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata_horz = headerdata_horz
        self.headerdata_vert = headerdata_vert

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
        if not index.isValid():
            print('Invalid index in MyModel>data')
            retval = QtCore.QVariant()
        elif role == QtCore.Qt.BackgroundRole:
            #print('row: {}, col:{}'.format(index.row(),index.column()))
            # if index.column() == 0:
            #     retval = QtCore.QVariant()
            # else:
            cell_contents = self.arraydata[index.row()][index.column()]
            if cell_contents[-1] == '0':
                #retval = QBrush(Qt.lightGray)
                retval = QtCore.QVariant()
            else:
                retval = QBrush(Qt.red)
            #retval = QtCore.QVariant()
            # pm = QtGui.QPixmap('/home/mac/SharedData/PycharmProjs/MuteMap/Mute_dark.png')
            # pm_s = pm.scaled(64,64)
            # retval = pm_s #QtGui.QPixmap('/home/mac/SharedData/PycharmProjs/MuteMap/Mute_dark.png')
        elif role == QtCore.Qt.DisplayRole:
            #retval = QtCore.QVariant()
            retval = QtCore.QVariant(self.arraydata[index.row()][index.column()])
        else:
            retval = QtCore.QVariant()

        return retval
        # if not index.isValid():
        #     return QVariant()
        # elif role != QtCore.Qt.DisplayRole:
        #     return QtCore.QVariant()
        # return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def setData(self, index, value, role):  # Set data in the model
        if role == QtCore.Qt.EditRole and index.isValid():
            print(index.row())
            self.arraydata[index.row()][index.column()] = value
            print('Return from rowCount: {0}'.format(self.rowCount(index)))
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        # elif role == QtCore.Qt.BackgroundRole:
        #     #return QtGui.QPixmap('/home/mac/SharedData/PycharmProjs/MuteMap/Mute_dark.png')
        #     pass
        #     if index.column() != 0:
        #         try:
        #             if self.arraydata[index.row()][index.column()][-1] == '0' or index.column() == 0:
        #                 return Qt.lightGray
        #                 #return QtGui.QPixmap('/home/mac/SharedData/PycharmProjs/MuteMap/Mute_dark.png')
        #             else:
        #                 return Qt.red
        #                 #return QtGui.QPixmap('/home/mac/SharedData/PycharmProjs/MuteMap/Mute_illum.png')
        #         except IndexError:
        #             print('Bad index, Row: {}, Column:{}'.format(index.row(),index.column()))
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
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = MuteMapDlg()

    ui.show()
    logging.info('Shutdown')
    sys.exit(app.exec_())
