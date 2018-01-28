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
import xml.dom.minidom as md
try:
    from lxml import ET
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as ET

pretty_print = lambda f: '\n'.join([line for line in md.parse(open(f)).toprettyxml(indent=' '*2).split('\n') if line.strip()])

class CheckProject():
    def __init__(self):
        self.cuefile = '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuesx.xml'
        self.charfile = '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_char.xml'
        self.cuecharfile = '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuechar.xml'
        return

    def checkit(self):
        # read the cues
        self.cues_tree = ET.parse(self.cuefile)
        self.cues_root = self.cues_tree.getroot()
        self.cues = self.cues_root.find("./cues")
        self.cues_list = self.cues.findall("./actors")
        self.cuefile_cuecount = len(self.cues_list)
        logging.info('Cue file: {}, actors count: {}'.format(self.cuefile,self.cuefile_cuecount))

        # read the characters
        self.char_tree = ET.parse(self.charfile)
        self.chars_root = self.char_tree.getroot()
        self.chars = self.chars_root.find("./chars")
        self.chars_list = self.chars.findall("./char")
        self.charfile_charcount = len(self.chars_list)
        logging.info('Char file: {}, char count: {}'.format(self.charfile,self.charfile_charcount))

        # read cuechar file
        self.cuechar_tree = ET.parse(self.cuecharfile)
        self.cuechar_root = self.cuechar_tree.getroot()
        self.cuechar_cues = self.cuechar_root.find("./cues")
        self.cuechar_cue_list = self.cuechar_cues.findall("./actors")
        self.cuecharfile_cuecount = len(self.cuechar_cue_list)
        logging.info('CueChar file: {}, actors count: {}'.format(self.cuecharfile,self.cuecharfile_cuecount))
        if self.cuecharfile_cuecount == self.cuecharfile_cuecount:
            logging.info("Cue count is correct")
        else:
            logging.info("Cue count mismatch")
        for cue in self.cuechar_cue_list:
            cue_uuid = cue.get('uuid')
            cuechar_cue_chars = cue.findall("./char")
            cuechar_cue_chars_count = len(cuechar_cue_chars)
            logging.info("Cue uuid: {}, char count: {}".format(cue_uuid, cuechar_cue_chars_count))

        # # read the strips
        # self.mixers_tree = ET.parse('/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_projectmixers.xml')
        # self.mixers_root = self.mixers_tree.getroot()
        # self.mixers = self.mixers_root.findall("./mixers/mixer")
        # self.strip_list = []
        # for mixer in self.mixers:
        #     self.strip_list.extend(mixer.findall("./strip"))
        #
        #     # Start the character tree
        #     cuestrip_tree = ET.Element('showcontrol')
        #     ET.SubElement(cuestrip_tree, 'version').text = '1.0'
        #     cuestrip_element = ET.SubElement(cuestrip_tree, 'cues')
        #     for actors in self.cues_list:
        #         strip_index = 0
        #         cue_uuid = actors.get('uuid')
        #         cue_element = ET.SubElement(cuestrip_element, 'actors', {'uuid' : cue_uuid})
        #         for index, char in enumerate(self.chars_list):
        #             char_uuid = char.get('uuid')
        #             char_name = char.find('name').text
        #             char_element = ET.SubElement(cue_element, 'char', {'uuid' : char_uuid})
        #             while True:
        #                 if self.strip_list[strip_index].find('type').text == 'input':
        #                     ET.SubElement(char_element, 'strip', {'uuid' : self.strip_list[strip_index].get('uuid')})
        #                     strip_index += 1
        #                     break
        #                 else:
        #                     strip_index += 1
        #
        #             print('uuid: {} name: {}'.format(char_uuid, char_name))
        # self.write(cuestrip_tree, False, '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_charstrip.xml')
        #
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
                        filename=LOG_DIR + '/CheckProject.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')

    CP = CheckProject()
    CP.checkit()
    pass
