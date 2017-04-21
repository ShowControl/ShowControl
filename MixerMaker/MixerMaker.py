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
from PyQt5.QtCore import pyqtSignal
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
import SelectNew_ui

import styles

parser = argparse.ArgumentParser()


cfgdict = cfg.toDict()

striplistheader = ['Type','Count','Name','Controls']
supportedstriptypes = ['input', 'auxin', 'bus', 'main', 'stout', 'auxmaster', 'busmaster']
supportedcontroltypes = ['fader', 'mute', 'scribble']
supportedcontrolitems = ['cmd', 'cmdtyp', 'range', 'val', 'anoms']

class controlCountvalidator(QtGui.QIntValidator):
    def init(self, parent=None):
        QtGui.QIntValidator.__init__(self, parent)
    def validate(self, p_str, p_int):
        if p_str == '':
            return QtGui.QValidator.Intermediate, p_str, p_int
        userinput = int(p_str)
        if userinput > 0 and userinput <= 99:
            return QtGui.QValidator.Acceptable, p_str, p_int
        else:
            return QtGui.QValidator.Invalid, p_str, p_int
    def fixup(self, p_str):
        self.parent().lineEdit_Count.setText(self.parent().selectedstrip.attrib['cnt'])
        QMessageBox.information(self.parent(), 'Invalid Input', 'Control count must be between 1 and 99.', QMessageBox.Ok)

class SelectNewItem(QtWidgets.QDialog, SelectNew_ui.Ui_SelectNew):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
    def accept(self):
        super(SelectNewItem, self).done(self.comboBox_SelectNew.currentIndex())
        pass
    def reject(self):
        super(SelectNewItem, self).done(99)
        # super(SelectNewItem, self).reject()
        pass

class StripNew(QtWidgets.QDialog, StripEdit_ui.Ui_Dialog):
    def __init__(self, strip_data, controls_data, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.installEventFilter(self)
        butts = self.buttonBox.buttons()
        if controls_data:
            self.strip_data = strip_data
            self.comboBox_StripType.setCurrentIndex(self.comboBox_StripType.findText(self.strip_data['type']))
        else:
            self.strip_data ={}
            self.comboBox_StripType.setCurrentIndex(-1)
        self.comboBox_StripType.currentIndexChanged['QString'].connect(self.strip_type_changed)
        self.lineEdit_Count.editingFinished.connect(self.lineEdit_Count_done)
        self.countvalidator = controlCountvalidator(self)
        self.countvalidator.setRange(1,99)
        self.lineEdit_Count.setValidator(self.countvalidator)
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
        self.tabledata = []
        if controls_data:
            print('got some')
            self.controls_data = controls_data
            for item in self.controls_data:
                self.tabledata.append([item])
        else:
            self.controls_data = {}
            print('got nothing')
        # set the table model
        self.tablemodel = MyTableModel(self.tabledata, ['Controls'], self)
        self.tableView_ControlsInStrip.horizontalHeader().setVisible(True)
        self.tableView_ControlsInStrip.setModel(self.tablemodel)
        self.tableView_ControlsInStrip.resizeColumnsToContents()
        self.control_index = 0
        self.tableView_ControlsInStrip.selectRow(self.control_index)
        if controls_data:
            selected_control = self.tableView_ControlsInStrip.model().\
                arraydata[self.tableView_ControlsInStrip.currentIndex().row()]\
                          [self.tableView_ControlsInStrip.currentIndex().column()]
            self.set_control_fields(selected_control)
            # self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(selected_control))
            # self.lineEdit_CommandString.setText(self.controls_data[selected_control]['cmd'])
            # self.comboBox_CommandType.setCurrentIndex(\
            #     self.comboBox_CommandType.findText(self.controls_data[selected_control]['cmdtyp']))
            # self.lineEdit_Range.setText(self.controls_data[selected_control]['range'])
            # self.lineEdit_DefaultValue.setText(self.controls_data[selected_control]['val'])
            # self.lineEdit_Anomalies.setText(self.controls_data[selected_control]['anoms'])
        else:
            self.comboBox_ControlType.setCurrentIndex(-1)
            self.comboBox_CommandType.setCurrentIndex(-1)

        self.lineEdit_CommandString.editingFinished.connect(self.lineEdit_CommandString_done)
        self.comboBox_CommandType.currentIndexChanged.connect(self.comboBox_CommandType_changed)
        self.lineEdit_Range.editingFinished.connect(self.lineEdit_Range_done)
        self.lineEdit_DefaultValue.editingFinished.connect(self.lineEdit_DefaultValue_done)
        self.lineEdit_Anomalies.editingFinished.connect(self.lineEdit_Anomalies_done)

        self.current_strip = ''
        self.current_controls = ''
        self.control_changed = False
        self.strip_data_changed = False
        # self.strip_data = {}
        # self.controls_data = {}
        self.data_changed = False

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.lineEdit_Count:
            print('Enter lineEdit_Count widget.')
        elif event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter and source is not self.buttonBox:
                print(event.type())
                print(event.key())
                print(Qt.Key_Return)
                self.focusNextChild()
                return True
        return QtWidgets.QWidget.eventFilter(self, source, event)

    def on_controls_rightclick(self):
        print('lineEdit_Controls right clicked')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            selnew = SelectNewItem()
            selnew.label_SelectNew.setText('Select new control type:')
            selnew.comboBox_SelectNew.addItems(supportedcontroltypes)
            newitemindex = selnew.exec()
            if newitemindex != 99:
                selectedindex = self.tableView_ControlsInStrip.currentIndex()
                value = supportedcontroltypes[newitemindex]
                newrow = [[value]] * len(self.tablemodel.arraydata)
                if not self.tablemodel.arraydata:
                    # has no rows or columns
                    self.tablemodel.arraydata.append([value])
                elif len(self.tablemodel.arraydata) > 0:
                    # has at least 1 row
                    newrow = [value] * len(self.tablemodel.arraydata)
                    self.tablemodel.arraydata.append(newrow)
                self.tablemodel.layoutChanged.emit()
                self.tableView_ControlsInStrip.resizeColumnsToContents()
                self.tableView_ControlsInStrip.selectRow(len(self.tablemodel.arraydata) - 1)
                self.controls_data[value] = {'cmd': '', 'cmdtyp': '', 'range': '', 'val': '', 'anoms': ''}
                self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(value))
                self.set_control_fields(value)
                pass
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
                # self.update_control_elements(self.control_index)
                #  clear the changed flag
                # self.control_changed = False #  clear changed flag once keep or discard is complete
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

    def set_control_fields(self, control_type):
        # control_attribs = self.selectedstrip.find("./{0}".format(control_type)).attrib
        # self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(control_type))
        # self.lineEdit_CommandString.setText(control_attribs['cmd'])
        # self.comboBox_CommandType.setCurrentIndex(self.comboBox_CommandType.findText(control_attribs['cmdtyp']))
        # self.lineEdit_Range.setText(control_attribs['range'])
        # self.lineEdit_Anomalies.setText(control_attribs['anoms'])
        # self.lineEdit_DefaultValue.setText(control_attribs['val'])
        self.comboBox_ControlType.setCurrentIndex(self.comboBox_ControlType.findText(control_type))
        self.lineEdit_CommandString.setText(self.controls_data[control_type]['cmd'])
        self.comboBox_CommandType.setCurrentIndex(self.comboBox_CommandType.findText(self.controls_data[control_type]['cmdtyp']))
        self.lineEdit_Range.setText(self.controls_data[control_type]['range'])
        self.lineEdit_Anomalies.setText(self.controls_data[control_type]['anoms'])
        self.lineEdit_DefaultValue.setText(self.controls_data[control_type]['val'])
        self.control_changed = False

    def update_control_elements(self, index):
        # controltype_str = self.tabledata[index][0]
        # print('Updating {0}'.format(controltype_str))
        # self.controls_data[controltype_str]['cmd'] = self.lineEdit_CommandString.text()
        # self.controls_data[controltype_str]['cmdtyp'] = self.comboBox_CommandType.currentText()
        # #self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmd'] = self.lineEdit_CommandString.text()
        # #self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmdtyp'] = self.comboBox_CommandType.currentText()
        # #self.selectedstrip.find("./{0}".format(controltype_str)).attrib['range'] = self.lineEdit_Range.text()
        # #self.selectedstrip.find("./{0}".format(controltype_str)).attrib['val'] = self.lineEdit_DefaultValue.text()
        # #self.selectedstrip.find("./{0}".format(controltype_str)).attrib['anoms'] = self.lineEdit_Anomalies.text()

        # #self.strip_data_changed = True
        pass

    # def add_new_strip(self):
    #     # type should have been set by the selection action of the combobox
    #     self.selectedstrip.attrib['type'] = self.comboBox_StripType.currentText()
    #     self.selectedstrip.attrib['cnt'] = self.lineEdit_Count.text()
    #     self.selectedstrip.attrib['name'] = self.lineEdit_Name.text()
    #     for index in range( len(self.tablemodel.arraydata)):
    #         print(self.tablemodel.arraydata[index][0])
    #         newcntrl = ET.Element(self.tablemodel.arraydata[index][0])
    #         newcntrl.attrib['cmd'] = self.lineEdit_CommandString.text()
    #         newcntrl.attrib['cmdtyp'] = self.comboBox_CommandType.currentText()
    #         newcntrl.attrib['range'] = self.lineEdit_Range.text()
    #         newcntrl.attrib['val'] = self.lineEdit_DefaultValue.text()
    #         newcntrl.attrib['anoms'] = self.lineEdit_Anomalies.text()
    #         self.selectedstrip.append(newcntrl)
    #     self.strip_data_changed = True
    #     pass

    def accept(self):
        if self.strip_data_changed or self.control_changed:
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to strip?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.data_changed = True
                super(StripNew, self).accept()
            elif reply == QMessageBox.No:
                self.data_changed = False
                print('not saving strip/control changes!')
                super(StripNew, self).accept()
            elif reply ==QMessageBox.Cancel:
                return
        else:
            super(StripNew, self).accept()
        super(StripNew, self).done(99)
        pass

    def reject(self):
        super(StripNew, self).reject()

    # Handle strip changes
    def strip_type_changed(self, newtype):
        self.strip_data_changed = True
        print(newtype)
        self.strip_data['type'] = newtype
        # self.selectedstrip.attrib['type'] = self.comboBox_StripType.currentText()

    def lineEdit_Count_done(self):
        if self.lineEdit_Count.isModified():
            self.strip_data_changed = True
            self.strip_data['cnt'] = self.lineEdit_Count.text()
            # self.selectedstrip.attrib['cnt'] = self.lineEdit_Count.text()

    def lineEdit_Count_enter(self):
        print('Current value of Count: {0}'.format(self.lineEdit_Count.text()))

    def lineEdit_Name_done(self):
        if self.lineEdit_Name.isModified():
            self.strip_data_changed = True
            self.strip_data['name'] = self.lineEdit_Name.text()
            # self.selectedstrip.attrib['name'] = self.lineEdit_Name.text()

    # Handle control changes
    def comboBox_ControlType_changed(self):
        self.control_changed = True

    def lineEdit_CommandString_done(self):
        if self.lineEdit_CommandString.isModified():
            self.control_changed = True
            controls_tableview_row = self.tableView_ControlsInStrip.currentIndex().row()
            controls_tableview_col = self.tableView_ControlsInStrip.currentIndex().column()
            selectedcontrol = self.tableView_ControlsInStrip.model().arraydata[controls_tableview_row][controls_tableview_col]
            self.controls_data[selectedcontrol]['cmd'] = self.lineEdit_CommandString.text()
        pass
    def comboBox_CommandType_changed(self):
        self.control_changed = True
        controls_tableview_row = self.tableView_ControlsInStrip.currentIndex().row()
        controls_tableview_col = self.tableView_ControlsInStrip.currentIndex().column()
        selectedcontrol = self.tableView_ControlsInStrip.model().arraydata[controls_tableview_row][
            controls_tableview_col]
        self.controls_data[selectedcontrol]['cmdtyp'] = self.comboBox_CommandType.currentText()
        pass
    def lineEdit_Range_done(self):
        if self.lineEdit_Range.isModified():
            controls_tableview_row = self.tableView_ControlsInStrip.currentIndex().row()
            controls_tableview_col = self.tableView_ControlsInStrip.currentIndex().column()
            selectedcontrol = self.tableView_ControlsInStrip.model().arraydata[controls_tableview_row][controls_tableview_col]
            self.control_changed = True
            self.controls_data[selectedcontrol]['range'] = self.lineEdit_Range.text()
        pass
    def lineEdit_DefaultValue_done(self):
        if self.lineEdit_DefaultValue.isModified():
            controls_tableview_row = self.tableView_ControlsInStrip.currentIndex().row()
            controls_tableview_col = self.tableView_ControlsInStrip.currentIndex().column()
            selectedcontrol = self.tableView_ControlsInStrip.model().arraydata[controls_tableview_row][controls_tableview_col]
            self.control_changed = True
            self.controls_data[selectedcontrol]['val'] = self.lineEdit_DefaultValue.text()
        pass
    def lineEdit_Anomalies_done(self):
        if self.lineEdit_Anomalies.isModified():
            print('Anomalies modified')
            controls_tableview_row = self.tableView_ControlsInStrip.currentIndex().row()
            controls_tableview_col = self.tableView_ControlsInStrip.currentIndex().column()
            selectedcontrol = self.tableView_ControlsInStrip.model().arraydata[controls_tableview_row][controls_tableview_col]
            self.control_changed = True
            self.controls_data[selectedcontrol]['anoms'] = self.lineEdit_Anomalies.text()
        pass

class StripEdit(QtWidgets.QDialog, StripEdit_ui.Ui_Dialog):
    def __init__(self, selectedmixer, selectedstriptype, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # self.installEventFilter(self)
        butts = self.buttonBox.buttons()
        self.comboBox_StripType.currentIndexChanged['QString'].connect(self.strip_type_changed)
        self.lineEdit_Count.editingFinished.connect(self.lineEdit_Count_done)
        # self.lineEdit_Count.installEventFilter(self)
        self.countvalidator = controlCountvalidator(self)
        self.countvalidator.setRange(1,99)
        self.lineEdit_Count.setValidator(self.countvalidator)
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
        self.tabledata = []
        self.selectedstriptype = selectedstriptype
        self.selectedstrip = selectedmixer.find("./strip[@type='{0}']".format(selectedstriptype))
        if selectedstriptype != 'new':
            self.stripcontrols = self.selectedstrip.findall('*')
            stripcontrols_str = ''
            for control in self.stripcontrols:
                self.tabledata.append([control.tag])
        else:
            self.tabledata =[]
        # set the table model
        self.tablemodel = MyTableModel(self.tabledata, ['Controls'], self)
        self.tableView_ControlsInStrip.horizontalHeader().setVisible(True)
        self.tableView_ControlsInStrip.setModel(self.tablemodel)
        self.tableView_ControlsInStrip.resizeColumnsToContents()
        self.control_index = 0
        self.tableView_ControlsInStrip.selectRow(self.control_index)
        self.tableView_ControlsInStrip.pressed.connect(self.table_row_changed)
        if selectedstriptype != 'new':
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

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and source is self.lineEdit_Count:
            print('Enter lineEdit_Count widget.')
        elif event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter and source is not self.buttonBox:
                print(event.type())
                print(event.key())
                print(Qt.Key_Return)
                return True
        return QtWidgets.QWidget.eventFilter(self, source, event)

    def on_controls_rightclick(self):
        print('lineEdit_Controls right clicked')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            selnew = SelectNewItem()
            selnew.label_SelectNew.setText('Select new control type:')
            selnew.comboBox_SelectNew.addItems(supportedcontroltypes)
            newitemindex = selnew.exec()
            if newitemindex != 99:
                selectedindex = self.tableView_ControlsInStrip.currentIndex()
                value = supportedcontroltypes[newitemindex]
                newrow = [[value]] * len(self.tablemodel.arraydata)
                if not self.tablemodel.arraydata:
                    # has no rows or columns
                    self.tablemodel.arraydata.append([value])
                elif len(self.tablemodel.arraydata) > 0:
                    # has at least 1 row
                    newrow = [value] * len(self.tablemodel.arraydata)
                    self.tablemodel.arraydata.append(newrow)
                self.tablemodel.layoutChanged.emit()
                self.tableView_ControlsInStrip.resizeColumnsToContents()
                self.tableView_ControlsInStrip.selectRow(0)

                pass
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

    def add_new_strip(self):
        # type should have been set by the selection action of the combobox
        self.selectedstrip.attrib['type'] = self.comboBox_StripType.currentText()
        self.selectedstrip.attrib['cnt'] = self.lineEdit_Count.text()
        self.selectedstrip.attrib['name'] = self.lineEdit_Name.text()
        for index in range( len(self.tablemodel.arraydata)):
            print(self.tablemodel.arraydata[index][0])
            newcntrl = ET.Element(self.tablemodel.arraydata[index][0])
            newcntrl.attrib['cmd'] = self.lineEdit_CommandString.text()
            newcntrl.attrib['cmdtyp'] = self.comboBox_CommandType.currentText()
            newcntrl.attrib['range'] = self.lineEdit_Range.text()
            newcntrl.attrib['val'] = self.lineEdit_DefaultValue.text()
            newcntrl.attrib['anoms'] = self.lineEdit_Anomalies.text()
            self.selectedstrip.append(newcntrl)
        # controltype_str = self.tabledata[index][0]
        # print('Updating {0}'.format(controltype_str))
        # self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmd'] = self.lineEdit_CommandString.text()
        # self.selectedstrip.find("./{0}".format(controltype_str)).attrib['cmdtyp'] = self.comboBox_CommandType.currentText()
        # self.selectedstrip.find("./{0}".format(controltype_str)).attrib['range'] = self.lineEdit_Range.text()
        # self.selectedstrip.find("./{0}".format(controltype_str)).attrib['val'] = self.lineEdit_DefaultValue.text()
        # self.selectedstrip.find("./{0}".format(controltype_str)).attrib['anoms'] = self.lineEdit_Anomalies.text()
        self.strip_data_changed = True
        pass

    def accept(self):
        if self.strip_data_changed:
            reply = QMessageBox.question(self, 'Save Changes', 'Save changes to strip?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                if self.selectedstriptype != 'new':
                    print('saving changed strip/control')
                    if self.control_changed:    # indicates control has been changed, but no other control was accessed
                                                # thus the changes weren't saved to the element tree
                        self.update_control_elements(self.tableView_ControlsInStrip.currentIndex().row())
                else:
                    self.add_new_strip()
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

    def lineEdit_Count_enter(self):
        print('Current value of Count: {0}'.format(self.lineEdit_Count.text()))

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

class MixerMakerDlg(QtWidgets.QMainWindow, MixerMaker_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MixerMakerDlg, self).__init__(parent)
        self.setupUi(self)
        self.comboBoxPickMixer.activated.connect(self.populateMixer)
        self.actionOpen.triggered.connect(self.openMixer)
        self.actionExit.triggered.connect(self.close)
        self.actionNew.triggered.connect(self.newMixersFile)
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

        self.pushButton_AddMixer.clicked.connect(self.on_AddMixer_clicked)
        self.lineEditBrand.editingFinished.connect(self.lineEditBrand_done)
        self.lineEditModel.editingFinished.connect(self.lineEditModel_done)

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

    def on_AddMixer_clicked(self):
        # Confirm brand and model not empty
        print('In on_AddMixer_clicked:')
        print(self.lineEditBrand.text())
        print(self.lineEditModel.text())
        if not self.lineEditBrand.text() or not self.lineEditModel.text() or not self.mixers:
            print('brand or model empty')
            QMessageBox.information(self, 'Empty Description',
                                    'Required to add mixer:\n1: Mixers definition file loaded\n2: Enter mixer brand\n3: Enter unique model',
                                    QMessageBox.Ok)
            return
        if self.mixers:
            # Confirm model string unique if other mixers loaded
            print('Mixers loaded')
            if self.mixers.mixer_count == 0:
                # add the first mixer
                self.addMixerToTree()
            else:
                # confirm the new mixer is unique
                for mixer in self.mixers.mixers:
                    print(mixer.attrib)
                    mxattribs = mixer.attrib
                    if 'model' in mxattribs.keys():
                        if mxattribs['model'] == self.lineEditModel.text()\
                                and mxattribs['mfr'] == self.lineEditBrand.text():
                            QMessageBox.information(self,
                                                    'Mixer Not Added',
                                                    'Mixer model must be unique./nUse dash for variations.',
                                                    QMessageBox.Ok)
                            break
                        else:
                            self.addMixerToTree()
                            # newmixer = self.mixers.addnewmixer(self.lineEditBrand.text(), self.lineEditModel.text())
                            # mutestyleattribs = {}
                            # if self.comboBoxMuteStyle.currentIndex() == 0:
                            #     mutestyleattribs['illuminated'] = '1'
                            #     mutestyleattribs['mute'] = '0'
                            #     mutestyleattribs['umute'] = '1'
                            # else:
                            #     mutestyleattribs['dark'] = '1'
                            #     mutestyleattribs['mute'] = '0'
                            #     mutestyleattribs['umute'] = '127'
                            # self.mixers.addnewmixerdetails(newmixer,
                            #                                self.buttonGroup_Protocol.checkedButton().text(),
                            #                                mutestyleattribs,
                            #                                self.comboBoxCountBase.currentText())
                            # self.comboBoxPickMixer.clear()
                            # self.comboBoxPickMixer.addItems(
                            #     ['{0}, {1}'.format(a, b) for a, b in zip(self.mixers.mfr_list, self.mixers.model_list)])
                            # self.disptext()
                            break
        return

    def addMixerToTree(self):
        newmixer = self.mixers.addnewmixer(self.lineEditBrand.text(), self.lineEditModel.text())
        mutestyleattribs = {}
        if self.comboBoxMuteStyle.currentIndex() == 0:
            mutestyleattribs['illuminated'] = '1'
            mutestyleattribs['mute'] = '0'
            mutestyleattribs['umute'] = '1'
        else:
            mutestyleattribs['dark'] = '1'
            mutestyleattribs['mute'] = '0'
            mutestyleattribs['umute'] = '127'
        self.mixers.addnewmixerdetails(newmixer,
                                       self.buttonGroup_Protocol.checkedButton().text(),
                                       mutestyleattribs,
                                       self.comboBoxCountBase.currentText())
        self.comboBoxPickMixer.clear()
        self.comboBoxPickMixer.addItems(
            ['{0}, {1}'.format(a, b) for a, b in zip(self.mixers.mfr_list, self.mixers.model_list)])
        self.disptext()

    def lineEditBrand_done(self):
        if self.lineEditBrand.isModified():
            self.mixers_modified = True
        pass

    def lineEditModel_done(self):
        if self.lineEditModel.isModified():
            self.mixers_modified = True
        pass

    def newMixersFile(self):
        mixerselement = ET.Element('mixers')
        newtree = ET.ElementTree(mixerselement)
        newtree.write('TestNewMixersFile.xml',encoding="utf-8", xml_declaration=True)
        print('Create New mixers file.')

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
            QMessageBox.No, QMessageBox.Yes)
        return reply

    def disptext(self):
        self.get_table_data()
        # set the table model
        tablemodel = MyTableModel(self.tabledata, striplistheader, self)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        self.tableView.selectRow(0)

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

    def on_table_rightclick(self):
        print('right click')
        sender_text = self.sender().text()
        if sender_text == 'Add':
            print(sender_text)
            print(
                'stripAdd_clicked with row {0}, column {1} selected.'.format(self.tableView.selectedIndexes()[0].row(),
                                                                             self.tableView.selectedIndexes()[
                                                                                 0].column()))
            self.addStrip()
        elif sender_text == 'Edit':
            print(sender_text)
            self.editStrip()
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
        self.addStrip()
        # print('stripAdd_clicked with row {0}, column {1} selected.'.format(self.tableView.selectedIndexes()[0].row(),
        #                                                                    self.tableView.selectedIndexes()[0].column()))
        # print(self.tableView.model().rowCount(None))

    def stripEdit_clicked(self):
        print('stripEdit_clicked')
        self.editStrip()

    def stripRemove_clicked(self):
        print('stripRemove_clicked')

    def editStrip(self):
        #todo-mac need to confirm mixer has been selected and
        #also, if the handle a new mixer with no strip yet
        if self.mixers.selected_mixer:
            if self.mixers.mixerstrips(self.mixers.selected_mixer.attrib['mfr'],self.mixers.selected_mixer.attrib['model']):
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

                strip_data = thisstrip.attrib
                controls_data = {}
                for stripcontrol in stripcontrols:
                    controls_data[stripcontrol.tag] = stripcontrol.attrib
                editStrip_dlg = StripNew(strip_data, controls_data)
                retval = editStrip_dlg.exec()
                if editStrip_dlg.data_changed:
                    self.mixers_modified = True
                    self.disptext()
                pass
            else:
                self.addStrip()
        else:
            QMessageBox.information(self, 'Select Mixer',
                                    'A mixer must be selected before editing strips.',
                                    QMessageBox.Ok)

    def addStrip(self):
        if self.mixers.selected_mixer:
            editStrip_dlg = StripNew({},{})
            retval = editStrip_dlg.exec()
            print('Returned from StripAdd: {0}'.format(editStrip_dlg.data_changed))
            if editStrip_dlg.data_changed:
                newstrip = self.mixers.makenewstrip(self.mixers.selected_mixer,
                                         editStrip_dlg.strip_data['type'],
                                         editStrip_dlg.strip_data['cnt'],
                                         editStrip_dlg.strip_data['name'])
                for control in editStrip_dlg.controls_data:
                    self.mixers.addcontrol(newstrip, control, editStrip_dlg.controls_data[control])
                self.mixers_modified = True
                self.disptext()
        else:
            QMessageBox.information(self, 'Select Mixer',
                                    'A mixer must be selected before adding strips.',
                                    QMessageBox.Ok)


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