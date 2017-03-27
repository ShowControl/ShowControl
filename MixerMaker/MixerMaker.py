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
import ControlEdit_ui
import StripEdit_ui

import styles

parser = argparse.ArgumentParser()


cfgdict = cfg.toDict()

striplistheader = ['Type','Count','Name','Controls']

class ControlEdit(QtWidgets.QDialog, ControlEdit_ui.Ui_Dialog):
    def __init__(self, strip, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.current_strip = strip
        self.data_changed = False
        self.tableView_ControlsInStrip.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.action_list = ['Add', 'Edit', 'Remove']
        self.actionAdd = QAction("Add", None)
        self.actionAdd.triggered.connect(self.on_controls_rightclick)
        self.tableView_ControlsInStrip.addAction(self.actionAdd)
        self.actionEdit = QAction("Edit", None)
        self.actionEdit.triggered.connect(self.on_controls_rightclick)
        self.tableView_ControlsInStrip.addAction(self.actionEdit)
        self.actionRemove = QAction("Remove", None)
        self.actionRemove.triggered.connect(self.on_controls_rightclick)
        self.tableView_ControlsInStrip.addAction(self.actionRemove)
        self.tableView_ControlsInStrip.clicked.connect(self.tableClicked)
        self.lineEdit_Anomalies.editingFinished.connect(self.lineEdit_Anomalies_done)

    def accept(self):
        self.data_changed = True
        self.current_strip.find("./{0}".format('fader')).attrib['anom'] = 'stuff from accept'

        super(ControlEdit, self).accept()

    def reject(self):
        super(ControlEdit, self).reject()

    def lineEdit_Anomalies_done(self): #  todo-mac implement capture of changed attributes
        print(self.lineEdit_Anomalies.isModified())

    def tableClicked(self, modelidx):
        rowidx = modelidx.row()
        self.tableView_ControlsInStrip.selectRow(rowidx)
        controltype_str = self.tableView_ControlsInStrip.model().arraydata[rowidx][0]
        thisattribs = self.current_strip.find("./{0}".format(controltype_str)).attrib
        self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(controltype_str))
        self.lineEdit_CommandString.setText(thisattribs['cmd'])
        self.comboBox_CommandType.setCurrentIndex(self.comboBox_CommandType.findText(thisattribs['cmdtyp']))
        self.lineEdit_Range.setText(thisattribs['range'])
        self.lineEdit_Anomalies.setText(thisattribs['anoms'])
        self.lineEdit_DefaultValue.setText(thisattribs['val'])

    def on_controls_rightclick(self):
        pass

class StripEdit(QtWidgets.QDialog, StripEdit_ui.Ui_Dialog):
    def __init__(self, selectedmixer, selectedstriptype, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.comboBox_StripType.currentIndexChanged['QString'].connect(self.strip_type_changed)
        self.lineEdit_Count.editingFinished.connect(self.lineEdit_Count_done)
        self.lineEdit_Name.editingFinished.connect(self.lineEdit_Name_done)
        self.tableView_ControlsInStrip.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.action_list = ['Add', 'Remove']
        self.actionAdd = QAction("Add", None)
        self.actionAdd.triggered.connect(self.on_controls_rightclick)
        self.tableView_ControlsInStrip.addAction(self.actionAdd)
        self.actionRemove = QAction("Remove", None)
        self.actionRemove.triggered.connect(self.on_controls_rightclick)
        self.tableView_ControlsInStrip.addAction(self.actionRemove)
        self.tableView_ControlsInStrip.clicked.connect(self.controlstableClicked)
        self.selectedstrip = selectedmixer.find("./strip[@type='{0}']".format(selectedstriptype))
        self.stripcontrols = self.selectedstrip.findall('*')
        stripcontrols_str = ''
        self.tabledata = []
        for control in self.stripcontrols:
            self.tabledata.append([control.tag])
        # set the table model
        tablemodel = MyTableModel(self.tabledata, ['Controls'], self)
        self.tableView_ControlsInStrip.setModel(tablemodel)
        self.tableView_ControlsInStrip.resizeColumnsToContents()
        self.control_index = 0
        self.tableView_ControlsInStrip.selectRow(self.control_index)
        self.tableView_ControlsInStrip.pressed.connect(self.table_row_changed)
        controltype_str = self.tabledata[self.control_index][0]
        self.set_control_fields(controltype_str)
        self.comboBox_ControlType.setEditable(False)
        self.comboBox_ControlType.setEnabled(False)
        self.lineEdit_CommandString.editingFinished.connect(self.lineEdit_CommandString_done)
        self.comboBox_CommandType.currentIndexChanged.connect(self.comboBox_CommandType_changed)
        self.lineEdit_Range.editingFinished.connect(self.lineEdit_Range_done)
        self.lineEdit_DefaultValue.editingFinished.connect(self.lineEdit_DefaultValue_done)
        self.lineEdit_Anomalies.editingFinished.connect(self.lineEdit_Anomalies_done)

        self.current_strip = ''
        self.current_controls = ''
        self.control_changed = False
        self.strip_data_changed = False

    def on_controls_rightclick(self):
        print('lineEdit_Controls right clicked')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            pass
        elif sender_text == 'Remove':
            # self.editcontrols()
            pass

    def controlstableClicked(self, modelidx):
        rowidx = modelidx.row()
        if rowidx != self.control_index and self.control_changed:
            # print('Control index changing to {0}'.format(rowidx))
            # print('Old index {0} has changed data'.format(self.control_index))
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to control?',
                                     QMessageBox.Yes |QMessageBox.No |  QMessageBox.Cancel,
                                     QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                #  save the changed elements/attributes
                self.update_control_elements(self.control_index)
                #  clear the changed flag
                self.control_changed = False #  clear changed flag once keep or discard is complete
                #  set the new control index
                self.control_index = rowidx
                self.tableView_ControlsInStrip.selectRow(self.control_index)
                controltype_str = self.tableView_ControlsInStrip.model().arraydata[self.control_index][0]
                self.set_control_fields(controltype_str)
            elif reply == QMessageBox.No:
                # clear the changed flag
                self.control_changed = False  # clear changed flag once keep or discard is complete
                #  set the new control index
                self.control_index = rowidx
                self.tableView_ControlsInStrip.selectRow(self.control_index)
                controltype_str = self.tableView_ControlsInStrip.model().arraydata[self.control_index][0]
                self.set_control_fields(controltype_str)
            elif reply == QMessageBox.Cancel:
                self.tableView_ControlsInStrip.selectRow(self.control_index)
                pass
        else:
            self.control_index = rowidx
            print('table index {0} pressed'.format(rowidx))
            self.tableView_ControlsInStrip.selectRow(self.control_index)
            controltype_str = self.tableView_ControlsInStrip.model().arraydata[self.control_index][0]
            self.set_control_fields(controltype_str)

    def table_row_changed(self, index):
        # if index != self.control_index and self.control_changed:
        #     print('Control index changing to {0}'.format(index.row()))
        #     print('Old index {0} has changed data'.format(self.control_index))
        #     #  todo-mac make call to confirm keep or discard changes, if keep, update the elements
        #     reply = QMessageBox.question(self, 'Save Changes', 'Save changes to control?',
        #                              QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        #                              QMessageBox.Cancel)
        #     if reply == QMessageBox.Save:
        #         self.control_changed = False #  clear changed flag once keep or discard is complete
        #         #  self.update_control_elements
        # else:
        #     self.control_index = index.row()
        #     print('table index {0} pressed'.format(index.row()))
        pass

    def set_control_fields(self, control_type):
        control_attribs = self.selectedstrip.find("./{0}".format(control_type)).attrib
        self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(control_type))
        self.lineEdit_CommandString.setText(control_attribs['cmd'])
        self.comboBox_CommandType.setCurrentIndex(self.comboBox_CommandType.findText(control_attribs['cmdtyp']))
        self.lineEdit_Range.setText(control_attribs['range'])
        self.lineEdit_Anomalies.setText(control_attribs['anoms'])
        self.lineEdit_DefaultValue.setText(control_attribs['val'])
        self.control_changed = False

    def update_control_elements(self, index):
        controltype_str = self.tabledata[index][0]
        print('Updating {0}'.format(controltype_str))
        self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmd'] = self.lineEdit_CommandString.text()
        self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmdtyp'] = self.comboBox_CommandType.currentText()
        self.selectedstrip.find("./{0}".format(controltype_str)).attrib['range'] = self.lineEdit_Range.text()
        self.selectedstrip.find("./{0}".format(controltype_str)).attrib['val'] = self.lineEdit_DefaultValue.text()
        self.selectedstrip.find("./{0}".format(controltype_str)).attrib['anoms'] = self.lineEdit_Anomalies.text()
        self.strip_data_changed = True
        pass

    def accept(self):
        if self.strip_data_changed:
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to strip?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                print('saving changed strip/control')
                if self.control_changed:    # indicates control has been changed, but no other control was accessed
                                            # thus the changes weren't saved to the element tree
                    self.update_control_elements(self.tableView_ControlsInStrip.currentIndex().row())
                super(StripEdit, self).accept()
            elif reply == QMessageBox.No:
                print('not saving strip/control changes!')
                super(StripEdit, self).accept()
        else:
            super(StripEdit, self).accept()
        self.data_changed = True
        super(StripEdit, self).done(99)
        pass

    def reject(self):
        super(StripEdit, self).reject()

    # Handle strip changes
    def strip_type_changed(self, newtype):
        self.strip_data_changed = True
        print(newtype)
        self.selectedstrip.attrib['type'] = self.comboBox_StripType.currentText()

    def lineEdit_Count_done(self):
        if self.lineEdit_Count.isModified():
            self.strip_data_changed = True
            self.selectedstrip.attrib['cnt'] = self.lineEdit_Count.text()
        pass

    def lineEdit_Name_done(self):
        if self.lineEdit_Name.isModified():
            self.strip_data_changed = True
            self.selectedstrip.attrib['name'] = self.lineEdit_Name.text()
        pass

    # Handle control changes
    def comboBox_ControlType_changed(self):
        self.control_changed = True
        pass
    def lineEdit_CommandString_done(self):
        if self.lineEdit_CommandString.isModified():
            self.control_changed = True
        pass
    def comboBox_CommandType_changed(self):
        self.control_changed = True
        pass
    def lineEdit_Range_done(self):
        if self.lineEdit_Range.isModified():
            self.control_changed = True
        pass
    def lineEdit_DefaultValue_done(self):
        if self.lineEdit_DefaultValue.isModified():
            self.control_changed = True
        pass
    def lineEdit_Anomalies_done(self):
        if self.lineEdit_Anomalies.isModified():
            self.control_changed = True
        pass


    def editcontrols(self):
        editcontrols_dlg = ControlEdit(self.current_strip)
        self.tabledata = []
        for control in self.current_controls:
            self.tabledata.append([control.tag])
        # set the table model
        tablemodel = MyTableModel(self.tabledata, ['Controls'], self)
        # tblview = self.window().findChild(QtWidgets.QTableView, name='tableWidget')
        editcontrols_dlg.tableView_ControlsInStrip.setModel(tablemodel)
        editcontrols_dlg.tableView_ControlsInStrip.resizeColumnsToContents()
        editcontrols_dlg.tableView_ControlsInStrip.selectRow(0)
        controltype_str = self.tabledata[0][0]
        # thiscontrol = self.current_controls.find("./{0}".format(controltype_str))
        thisattribs = self.current_strip.find("./{0}".format(controltype_str)).attrib
        editcontrols_dlg.comboBox_ControlType.setCurrentIndex(
            editcontrols_dlg.comboBox_ControlType.findText(controltype_str))
        editcontrols_dlg.lineEdit_CommandString.setText(thisattribs['cmd'])
        editcontrols_dlg.comboBox_CommandType.setCurrentIndex(
            editcontrols_dlg.comboBox_CommandType.findText(thisattribs['cmdtyp']))
        editcontrols_dlg.lineEdit_Range.setText(thisattribs['range'])
        editcontrols_dlg.lineEdit_Anomalies.setText(thisattribs['anoms'])
        editcontrols_dlg.lineEdit_DefaultValue.setText(thisattribs['val'])
        editcontrols_dlg.exec_()
        if editcontrols_dlg.data_changed == True:  # todo-mac this needs to get all the controls not just one
            self.current_strip.find("./{0}".format(controltype_str)).attrib[
                'anoms'] = editcontrols_dlg.lineEdit_Anomalies.text()
            self.current_strip.find("./{0}".format(controltype_str)).attrib[
                'cmd'] = editcontrols_dlg.lineEdit_CommandString.text()
            self.current_strip.find("./{0}".format(controltype_str)).attrib[
                'val'] = editcontrols_dlg.lineEdit_DefaultValue.text()
            self.current_strip.find("./{0}".format(controltype_str)).attrib[
                'range'] = editcontrols_dlg.lineEdit_Range.text()
            self.mixers.savemixers(False, 'TestMixerSave.xml')


# class StripEdit(QtWidgets.QDialog, StripEdit_ui.Ui_Dialog):
#     def __init__(self, strip, controls, parent=None):
#         QDialog.__init__(self, parent)
#         self.setupUi(self)
#         self.label_Controls.setContextMenuPolicy(Qt.ActionsContextMenu)
#         self.action_list = ['Add', 'Edit', 'Remove']
#         self.actionAdd = QAction("Add", None)
#         self.actionAdd.triggered.connect(self.on_controls_rightclick)
#         self.label_Controls.addAction(self.actionAdd)
#         self.actionEdit = QAction("Edit", None)
#         self.actionEdit.triggered.connect(self.on_controls_rightclick)
#         self.label_Controls.addAction(self.actionEdit)
#         self.actionRemove = QAction("Remove", None)
#         self.actionRemove.triggered.connect(self.on_controls_rightclick)
#         self.label_Controls.addAction(self.actionRemove)
#         self.current_strip = strip
#         self.current_controls = controls
#
#     def on_controls_rightclick(self):
#         print('lineEdit_Controls right clicked')
#         sender_text = self.sender().text()
#         if sender_text == 'Add':
#             pass
#         elif sender_text == 'Edit':
#             self.editcontrols()
#             pass
#
#     def editcontrols(self):
#         editcontrols_dlg = ControlEdit(self.current_strip)
#         self.tabledata = []
#         for control in self.current_controls:
#             self.tabledata.append([control.tag])
#         # set the table model
#         tablemodel = MyTableModel(self.tabledata, ['Controls'], self)
#         # tblview = self.window().findChild(QtWidgets.QTableView, name='tableWidget')
#         editcontrols_dlg.tableView_ControlsInStrip.setModel(tablemodel)
#         editcontrols_dlg.tableView_ControlsInStrip.resizeColumnsToContents()
#         editcontrols_dlg.tableView_ControlsInStrip.selectRow(0)
#         controltype_str = self.tabledata[0][0]
#         # thiscontrol = self.current_controls.find("./{0}".format(controltype_str))
#         thisattribs = self.current_strip.find("./{0}".format(controltype_str)).attrib
#         editcontrols_dlg.comboBox_ControlType.setCurrentIndex(editcontrols_dlg.comboBox_ControlType.findText(controltype_str))
#         editcontrols_dlg.lineEdit_CommandString.setText(thisattribs['cmd'])
#         editcontrols_dlg.comboBox_CommandType.setCurrentIndex(editcontrols_dlg.comboBox_CommandType.findText(thisattribs['cmdtyp']))
#         editcontrols_dlg.lineEdit_Range.setText(thisattribs['range'])
#         editcontrols_dlg.lineEdit_Anomalies.setText(thisattribs['anoms'])
#         editcontrols_dlg.lineEdit_DefaultValue.setText(thisattribs['val'])
#         editcontrols_dlg.exec_()
#         if editcontrols_dlg.data_changed == True: #  todo-mac this needs to get all the controls not just one
#             self.current_strip.find("./{0}".format(controltype_str)).attrib['anoms'] = editcontrols_dlg.lineEdit_Anomalies.text()
#             self.current_strip.find("./{0}".format(controltype_str)).attrib['cmd'] = editcontrols_dlg.lineEdit_CommandString.text()
#             self.current_strip.find("./{0}".format(controltype_str)).attrib['val'] = editcontrols_dlg.lineEdit_DefaultValue.text()
#             self.current_strip.find("./{0}".format(controltype_str)).attrib['range'] = editcontrols_dlg.lineEdit_Range.text()
#             self.mixers.savemixers( False, 'TestMixerSave.xml')

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
        self.mixers_modified = False
        self.mixers = {}
        self.mixerindex = 0
        self.stripmodelindex = 0
        self.tableheader = []
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
        self.mixers.set_selected_mixer(self.mixers.mfr_list[index], self.mixers.model_list[index])
        self.lineEditBrand.setText(self.mixers.selected_mixer.attrib['mfr'])
        self.lineEditModel.setText(self.mixers.selected_mixer.attrib['model'])
        self.mixers.mixerattribs(self.mixers.mfr_list[index], self.mixers.model_list[index])
        if self.mixers.get_selected_mixer_element('protocol', '', '') == 'osc':
            self.radioButtonOSC.setChecked(True)
        else:
            self.radioButtonMIDI.setChecked(True)
        mutestyleattribs = self.mixers.selected_mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
            self.comboBoxMuteStyle.setCurrentIndex(0)
        else:
            self.comboBoxMuteStyle.setCurrentIndex(1)
        if self.mixers.get_selected_mixer_element('countbase', '', '').replace('"','') == '0':
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
        self.mixers.savemixers(True, self.conffile)
        self.mixers_modified = False

    def exitMixer(self):
        print('File>Exit')

    def closeEvent(self, event):
        """..."""
        if self.mixers_modified:
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to mixers?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.mixers.savemixers(False, 'TestMixerSave.xml')
                self.mixers_modified = False
            elif reply == QMessageBox.No:
                pass
            elif reply == QMessageBox.Cancel:
                pass

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
        # strips = self.mixers.mixerstrips(self.mixers.mfr_list[self.mixerindex], self.mixers.model_list[self.mixerindex])
        self.tabledata =[]
        row_list = []
        for strip in strips:
            striptype = strip.attrib['type']
            stripcount = strip.attrib['cnt']
            stripname = strip.attrib['name']
            stripcontrols = strip.findall('*')
            stripcontrols_str = ''
            for stripcontrol in stripcontrols:
                if stripcontrols_str == '':
                    stripcontrols_str += '{0}'.format(stripcontrol.tag)
                else:
                    stripcontrols_str += ', {0}'.format(stripcontrol.tag)
            row_list.extend([striptype,stripcount,stripname, stripcontrols_str])
            self.tabledata.append([striptype,stripcount,stripname, stripcontrols_str])

    # def tableClicked(self, modelidx):
    #     self.stripmodelindex = modelidx.row()
    #     self.tableView.selectRow(self.stripmodelindex)

    def on_table_rightclick(self):
        print('right click')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            print(sender_text)
            print(
                'stripAdd_clicked with row {0}, column {1} selected.'.format(self.tableView.selectedIndexes()[0].row(),
                                                                             self.tableView.selectedIndexes()[
                                                                                 0].column()))
        elif sender_text == 'Edit':
            print(sender_text)
        elif sender_text == 'Remove':
            print(sender_text)
        pass

    def on_table_dblclick(self,index):
        print('double click on row: {0}'.format(index.row()))
        pass

    def on_table_click(self,index):
        self.stripmodelindex = index.row()
        self.tableView.selectRow(self.stripmodelindex)
        print('click on row: {0}'.format(index.row()))
        pass

    def stripAdd_clicked(self):
        print('stripAdd_clicked with row {0}, column {1} selected.'.format(self.tableView.selectedIndexes()[0].row(),
                                                                           self.tableView.selectedIndexes()[0].column()))
        print(self.tableView.model().rowCount(None))

    def stripEdit_clicked(self):
        print('stripEdit_clicked')
        self.editStrip()

    def stripRemove_clicked(self):
        print('stripRemove_clicked')

    def editStrip(self):
        index = self.tableView.selectedIndexes()[0].row()
        striptype = self.tabledata[index][0]
        #  ET.dump(self.mixers.mixers[self.mixerindex].find("./strip[@type='input']"))
        #  ET.dump(self.mixers.mixers[self.mixerindex].find("./strip[@type='{0}']".format(striptype)))
        thisstrip = self.mixers.mixers[self.mixerindex].find("./strip[@type='{0}']".format(striptype))
        stripcontrols = thisstrip.findall('*')
        stripcontrols_str = ''
        for stripcontrol in stripcontrols:
            if stripcontrols_str == '':
                stripcontrols_str += '{0}'.format(stripcontrol.tag)
            else:
                stripcontrols_str += ', {0}'.format(stripcontrol.tag)

        editStrip_dlg = StripEdit(self.mixers.selected_mixer, striptype)
        type_index = editStrip_dlg.comboBox_StripType.findText(striptype)
        editStrip_dlg.comboBox_StripType.setCurrentIndex(type_index)
        editStrip_dlg.lineEdit_Count.setText(thisstrip.attrib['cnt'])
        editStrip_dlg.lineEdit_Name.setText(thisstrip.attrib['name'])
        # editStrip_dlg.label_Controls.setText(stripcontrols_str)
        retval = editStrip_dlg.exec()
        if editStrip_dlg.strip_data_changed:
            self.mixers_modified = True
            self.disptext()
        pass

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