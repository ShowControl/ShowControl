'''
Created on Wed Oct 25 10:09:54 EDT 2017
CueChar object that maintains the character state for each cue
@author: mac
'''

import sys
import inspect
import os
from os import path
import shutil
import uuid
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import logging

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

class CueChar():
    """
    CueChar object contains the character state for each cue of a project
    """
    def __init__(self, cuecharfilename):
        """"""
        logging.info('In CueChar init')
        self.setup_cuechar(cuecharfilename)

    def setup_cuechar(self, filename):
        logging.info('In CueList setup_cues')
        self.cuecharlist = ET.parse(filename)
        self.cuecharlist_root = self.cuecharlist.getroot()
        #self.cues_element = self.cuelist_root.find('cues')
        #self.cuelist.find(".cues/cue[@num='001']")
        cues = self.cuecharlist.findall('.cues/cue')
        self.cuecharcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        cue = self.cuecharlist_root.find(".cues/cue[@uuid='" + uuid + "']")
        return

    def add_new_char(self, new_char_uuid):
        cues = self.cuecharlist.findall('.cues/cue')
        for cue in cues:
            chars = cue.findall(".char")
            print('In add_new_char, char count before: {}'.format(len(chars)))
            new_char_ele = ET.SubElement(cue, 'char', {'uuid':new_char_uuid})
            ET.SubElement(new_char_ele, 'mute').text = '1'
            ET.SubElement(new_char_ele, 'onstage').text = '0'
            ET.SubElement(new_char_ele, 'level').text = '0'
            ET.SubElement(new_char_ele, 'eq', attrib={'uuid': 'eq uuid'})
            ET.SubElement(new_char_ele, 'routing', attrib={'uuid': 'routing uuid'})
            # print('In add_new_char, char count after: {}'.format(len(chars)))

    def delete_char(self, uuid):
        print("CueChar delete_char, uuid: {}".format(uuid))
        cues = self.cuecharlist.findall('.cues/cue')
        for cue in cues:
            delete_candidate = cue.find(".char[@uuid='" + uuid + "']")
            cue.remove( delete_candidate )

    def add_cue(self, cue_uuid, char_list):
        print('CueChar add_cue, uuid: {}'.format(cue_uuid))
        cues_element = self.cuecharlist.find('.cues')
        new_cue = ET.SubElement(cues_element, 'cue', {'uuid': cue_uuid})
        for char in char_list:
            new_char_ele = ET.SubElement(new_cue, 'char', {'uuid':char[0]})
            ET.SubElement(new_char_ele, 'mute').text = '1'
            ET.SubElement(new_char_ele, 'onstage').text = '0'
            ET.SubElement(new_char_ele, 'level').text = '0'
            ET.SubElement(new_char_ele, 'eq', attrib={'uuid': 'eq uuid'})
            ET.SubElement(new_char_ele, 'routing', attrib={'uuid': 'routing uuid'})

    def delete_cue(self, cue_uuid):
        print('CueChar delete_cue, uuid: {}'.format(cue_uuid))
        cues_element = self.cuecharlist.find('.cues')
        cue_element = cues_element.find(".cue[@uuid='" + cue_uuid + "']")
        cues_element.remove(cue_element)

    def write(self, newchars,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newchars)
        if filename == '':
            logging.debug('Configuration not saved, no filename provided!')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Configuration not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        if revision:
            oldroot, extension = path.splitext(filename)
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)

            # newdoctree.write(oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        # else:
        #     newdoctree.write(filename)
        #     self.logging.debug('Configuration written to: ' + filename)
        newdoctree.write(filename, xml_declaration=True)
        logging.debug('Configuration written to: ' + filename)

        return
