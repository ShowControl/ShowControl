"""
Created on Wed Oct 25 10:09:54 EDT 2017
CueChar object that maintains the character state for each cue
@author: mac

Updated on Fri Nov 10 09:20:06 EST 2017
@author: mac
This update is a new attempt to smooth out handling of xml
class CueChar() is now the cue manipulation class
class CreateCueChar() handles creating empty cuechar files when creating a new project

"""

import sys
import inspect
import os
from os import path
import shutil
import uuid
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import logging

import xml.dom.minidom as md
try:
    from lxml import ET
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as ET

pretty_print = lambda f: '\n'.join([line for line in md.parse(open(f)).toprettyxml(indent=' '*2).split('\n') if line.strip()])

class CueChar():
    """
    CueChar object contains the character state for each actors of a project
    """
    def __init__(self, cuecharfilename):
        """"""
        logging.info('In CueChar init')
        self.setup_cuechar(cuecharfilename)

    def setup_cuechar(self, filename):
        logging.info('In CueChar setup_cuechar')
        # cuecharlist contains all elements *under* <showcontrol>
        self.cuecharlist = ET.parse(filename)
        # getroot() return <showcontrol> and elements under it
        #self.cuecharlist_root = self.cuecharlist.getroot()
        cues = self.cuecharlist.findall('.cues/cue')
        self.cue = []
        self.cuecharcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        self.cue = self.cuecharlist.find(".cues/cue[@uuid='" + uuid + "']")
        return self.cue

    def get_char_by_uuid(self, uuid):
        """return character strip set for current actors"""
        char_stripset = None
        try:
            char_stripset = self.cue.find(".char[@uuid='" + uuid + "']")
        except:
            logging.error('char uuid: {} not found!'.format(uuid))
        return char_stripset

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
        oldroot, extension = path.splitext(filename)
        if revision:
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)

            # newdoctree.write(oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        # else:
        #     newdoctree.write(filename)
        #     self.logging.debug('Configuration written to: ' + filename)
        filename_up = oldroot + '_up' + extension  # up >>> uglyprint
        newdoctree.write(filename_up, encoding="UTF-8", xml_declaration=True)
        of = open(filename, 'w')
        of.write(pretty_print(filename_up))
        of.close()

        logging.debug('Configuration written to: ' + filename)

        return

class CreateCueChar():
    """
    CreateCueChar class is used exclusively to create a new cuechar file
    for a new project
    """
    def __init__(self, cuecharfilename, first_cue_uuid, char_list):
        """"""
        logging.info('In CueChar init')
        if not path.isfile(cuecharfilename):
            # build new cuechar file
            self.cuecharlist = ET.Element('showcontrol')
            project = ET.SubElement(self.cuecharlist, 'cues')
            ET.SubElement(project, 'version').text = '1.0'
            cues_element = self.cuecharlist.find('.cues')
            new_cue = ET.SubElement(cues_element, 'actors', {'uuid': first_cue_uuid})
            for char in char_list:
                new_char_ele = ET.SubElement(new_cue, 'char', {'uuid': char[0]})
                ET.SubElement(new_char_ele, 'mute').text = '1'
                ET.SubElement(new_char_ele, 'onstage').text = '0'
                ET.SubElement(new_char_ele, 'level').text = '0'
                ET.SubElement(new_char_ele, 'eq', attrib={'uuid': 'eq uuid'})
                ET.SubElement(new_char_ele, 'routing', attrib={'uuid': 'routing uuid'})
            self.write(self.cuecharlist, False, cuecharfilename)
        return

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
        oldroot, extension = path.splitext(filename)
        if revision:
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)

            # newdoctree.write(oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        filename_up = oldroot + '_up' + extension  # up >>> uglyprint
        newdoctree.write(filename_up, encoding="UTF-8", xml_declaration=True)
        of = open(filename, 'w')
        of.write(pretty_print(filename_up))
        of.close()

        logging.debug('Configuration written to: ' + filename)

        return

if __name__ == "__main__":
    HOME = os.path.expanduser("~")

    CFG_DIR = HOME + '/.config/ShowControl'
    CFG_PATH = CFG_DIR + '/ShowControl_config.xml'
    LOG_DIR = HOME + '/.log/ShowControl'
    SHOWS = '/home/mac/SharedData/ShowSetups/Shows'
    TEST_DIR = '/home/mac/SharedData/ShowSetups/Shows/Fiddler/'
    TEST_PATH = TEST_DIR + 'FiddlerChar_cuechar.xml'
    logging.basicConfig(level="INFO",
                        filename=LOG_DIR + '/CueChar.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info("In CueChar.__main__")
    cuechar_object = CueChar(TEST_PATH)
    cue = cuechar_object.get_cue_by_uuid('f40e83e1-f69f-4fd7-bd22-5baae2d1fd07')
    pass