'''
Created on Fri Oct 13 11:48:35 EDT 2017
Cue object that maintains the current cue list
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

class Char():
    """
    CueList object contains information defining the cues for a show
    """
    def __init__(self):
        """"""
        logging.info('In Cast init')
        self.char_list = []

    def setup_cast(self, charfilename):
        """Load the specified xml file """
        logging.info('In Chars setup_cast')
        self.char_element_tree = ET.parse(charfilename)
        self.charlist_root = self.char_element_tree.getroot()
        self.chars_element = self.charlist_root.find('chars')
        self.char_element_list = self.chars_element.findall('char')
        self.charcount = len(self.char_element_list)
        return

    # def chars_toDict(self):
    #     logging.info('In Chars cast_toDict')
    #     for char in self.char_element_list:
    #         self.char_dict[char.get('uuid')] = (char.find('name').text,char.find('actor').text)
    #     return

    def chars_to_list_of_tuples(self):
        """Create a list of tuples from the character xml element list
        where each list element is a tuple (uuid, charname, actor)"""
        logging.info('In Chars cast_toDict')
        for char in self.char_element_list:
            self.char_list.append((char.get('uuid').strip('"'), char.find('name').text.strip('"'),char.find('actor').text.strip('"')))
        return

    def chars_toxmldoc(self):
        """Create a new showcontrol element from the current state of the list of character tuples"""
        newcharelements = {}
        showcontrol = ET.Element('showcontrol')
        ET.SubElement(showcontrol, 'version').text = '1.0'
        chars = ET.SubElement(showcontrol, 'chars')
        for char in self.char_list:
            charchild = ET.SubElement(chars, 'char', attrib={'uuid':char[0]})
            ET.SubElement(charchild, 'name').text = char[1]
            ET.SubElement(charchild, 'actor').text = char[2]
        return showcontrol

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

    def create_new_project(self, folder, name):
        """create a new project
        folder = project folder
        name = new project name"""
        self.new_project_file(folder, name)
        self.new_char_list(folder, name)
        return

    def new_project_file(self, folder, name):
        # create the new project folder
        newpath = os.path.join(folder, name)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        logging.info('new_project_file: {}'.format(newpath))
        return

    def new_char_list(self, folder, name):
        """create an empty character list xml file"""
        # build file name
        cf = os.path.join(folder, name, '{}_char.xml'.format(name))
        of = open(cf,mode='w')
        of.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        of.write('<show_control>\n')
        of.write('    <version>1.0</version >\n')
        of.write('    <chars>\n')
        of.write('      <char uuid="{}">\n'.format(uuid.uuid4()))
        of.write('       <name>"First char"</name>\n')
        of.write('       <actor>"Played by"</actor>\n')
        of.write('      </char>\n')
        of.write('    </chars>\n')
        of.write('</show_control>\n')
        of.close()


if __name__ == "__main__":
    HOME = os.path.expanduser("~")

    CFG_DIR = HOME + '/.config/ShowControl'
    CFG_PATH = CFG_DIR + '/ShowControl_config.xml'
    LOG_DIR = HOME + '/.log/ShowControl'
    SHOWS = '/home/mac/SharedData/ShowSetups/Shows'
    TEST_DIR = '/home/mac/SharedData/ShowSetups/Shows/TestProj'
    TEST_PATH = TEST_DIR + 'Characters.xml'
    logging.basicConfig(level="INFO",
                        filename=LOG_DIR + '/Char.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info("In Char.__main__")
    chars = Char(TEST_PATH)
    # chars.create_new_project(SHOWS, 'CharTest')
    tf = os.path.join(SHOWS, 'CharTest', '{}_char.xml'.format('CharTest'))
    chars.setup_cast(tf)
    chars.chars_to_list_of_tuples()
    newchars = chars.chars_toxmldoc()
    chars.write(newchars, True, tf)