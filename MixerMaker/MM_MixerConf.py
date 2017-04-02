#!/usr/bin/env python3
"""
Created on Mar 5, 2017
MM_MixerConf mixer configuration object

@author: mac
"""
__author__ = 'mac'

import argparse
import inspect
import os
import socket
import sys
import re
from os import path
import logging
import copy

# logger = logging.getLogger(__name__)
# logger.info('Top of MixerConf')
# logger.debug('debug message')

import sys

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

# from MixerControl import ControlFactory, supported_protocols, supported_controls
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pythonosc import osc_message
from pythonosc import osc_message_builder


class MixerConf:
    def __init__(self, mixerconf_file):
        self.mixerdefsorig = ET.parse(mixerconf_file)
        self.mixerdefs = copy.deepcopy(self.mixerdefsorig)
        self.mixers = self.mixerdefs.getroot()
        self.mixer_count = len(self.mixers)
        self.mfr_list = []
        self.model_list = []
        self.protocol = ''
        self.mutestyle = ''
        self.s_countbase = ''
        self.mixer_list()
        self.selected_mixer = None
        self.defs_modified = False

    def mixer_list(self):
        for mixer in self.mixers:
            mxattribs = mixer.attrib
            self.mfr_list.append(mxattribs['mfr'])
            self.model_list.append(mxattribs['model'])

    def mixerattribs(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.protocol = mixer.find('protocol').text
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
                self.mutestyle = 'illuminated'
        elif 'dark' in mutestyleattribs:
                self.mutestyle = 'dark'
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
                self.mutestyle = 'illuminated'
        elif 'dark' in mutestyleattribs:
                self.mutestyle = 'dark'
        self.s_countbase = mixer.find('countbase').text.replace('"','')

    def mixerstrips(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        return mixer.findall('strip')

    def set_selected_mixer(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    self.selected_mixer = mixer
                    break

    def get_selected_mixer_element(self, tag, attribname, attribvalue):
        """Get the tag text if attribname == ''
        else get the element 'tag', that has 'attribname'='attribvalue'"""
        if attribname == '':
            #  return element text
            #  typically used to get an element with
            #  a unique tag and only a single value
            return self.selected_mixer.find(tag).text
        else:
            #  return element 'tag', that has 'attribname'='attribvalue'
            return self.selected_mixer.find("./{0}[@{1}='{2}']".format(tag, attribname, attribvalue))

    def get_selected_mixer_element_attrib(self, tag, attribname):
        """Get the specified tag's specified attribname's value"""
        #  return element 'tag', that has 'attribname'='attribvalue'
        return self.selected_mixer.find(tag).attrib[attribname]

    def get_selected_strip_control_element(self, strip, tag):
        return strip.find(tag).attrib

    def set_element_attrib(self, element, attribname, newval):
        """Set the named attribute in element to newval"""
        element.attrib[attribname] = newval

    def set_control_attrib(self, strip, tag, attribname, newval):
        control_element = strip.find(tag)
        control_element.attrib[attribname] = newval

    def savemixers(self, revision=True, filename=''):
        """save the current state of the mixer definitions.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the mixer definitions file,
        typically call with revision=True before an add or insert
        If revision=False, save the current state of the cuelist
        in the file specified by filename"""
        if filename == '':
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('The mixers not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        if revision:
            oldroot, extension = path.splitext(filename)
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            self.mixerdefs.write(oldroot + '-{0}'.format(rev) + extension)
        else:
            self.mixerdefs.write(filename)

    def makenewstrip(self, mixer, striptype):
        newstrip = ET.Element('strip', attrib={'type':striptype, 'cnt':'', 'name':''})
        # newcontrol = ET.SubElement(newstrip, 'fader')
        mixer.insert(mixer.__len__(), newstrip)
        return newstrip

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    fileNames = []
    fdlg = QtWidgets.QFileDialog()
    fdlg.setFilter(QDir.AllEntries | QDir.Hidden)
    if (fdlg.exec()):
        fileNames = fdlg.selectedFiles()
    fdlg.close()
    if len(fileNames) != 0:
        conffile = fileNames[0]
    print('File>Open: {0}'.format(fileNames))

    mixers = MixerConf(conffile)
    print(mixers.mixer_count)
    print(mixers.mfr_list)
    print(mixers.model_list)
    mixers.set_selected_mixer('Behringer', 'X32')
    ET.dump(mixers.selected_mixer)
    mixers.set_element_attrib(mixers.selected_mixer, 'model', 'X32++')
    print(mixers.get_selected_mixer_element('protocol', '', ''))
    print('illuminated = ' + mixers.get_selected_mixer_element_attrib('mutestyle', 'illuminated'))
    selectedmixerstrip = mixers.get_selected_mixer_element('strip', 'type', 'input')
    mixers.set_element_attrib(selectedmixerstrip, 'name', 'Ccc')
    selectedmixerstripcontrol = mixers.get_selected_strip_control_element(selectedmixerstrip, 'fader')
    mixers.set_control_attrib(selectedmixerstrip, 'fader', 'anoms', 'fake')
    mixers.savemixers( False, 'TestMixerSave.xml')
    pass