'''
Created on Nov 2, 2014
Cue object that maintains the current cue list
@author: mac
'''

import sys
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

class cuecharXML():
    """
    Builder for cues xml file
    """
    def __init__(self):
        """"""
        logging.info('In cuecharXML init')

    def toXMLdoc(self):
        # get cues xml
        # self.cuelist = ET.parse('/home/mac/Shows/CharTest/CharTest_cuesx.xml')
        self.cuelist = ET.parse('/home/mac/Shows/Fiddler/Fiddler_cuesx.xml')
        self.cuelist_root = self.cuelist.getroot()
        self.cues = self.cuelist_root.findall(".cues/actors")
        # get char xml
        # self.charlist = ET.parse('/home/mac/Shows/CharTest/CharTest_char.xml')
        # self.charlist = ET.parse('/home/mac/Shows/Fiddler/FiddlerChar_char.xml')
        self.charlist = ET.parse('/home/mac/Shows/Fiddler/Fiddler_char.xml')
        self.charlist_root = self.charlist.getroot()
        self.chars = self.charlist_root.findall(".chars/char")

        showcontrol = ET.Element('showcontrol')
        newcues = ET.SubElement(showcontrol, 'cues')
        ET.SubElement(newcues, 'version').text = '1.0'
        for cue in self.cues:
            cue_uuid = cue.get('uuid')

            cue = ET.SubElement(newcues, 'actors', attrib={'uuid':cue_uuid})
            for char in self.chars:
                char_uuid = char.get('uuid')
                newchar = ET.SubElement(cue, 'char', attrib={'uuid':char_uuid})
                ET.SubElement(newchar, 'mute').text = '1'
                ET.SubElement(newchar, 'onstage').text = '0'
                ET.SubElement(newchar, 'level').text = '0'
                ET.SubElement(newchar, 'eq', attrib={'uuid':'eq uuid'})
                ET.SubElement(newchar, 'routing', attrib={'uuid':'routing uuid'})
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
                        filename=LOG_DIR + '/Build_cuecherXML.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    cuecharobj = cuecharXML()
    cuechar_doc = cuecharobj.toXMLdoc()
    cuecharobj.write(cuechar_doc, False, '/home/mac/Shows/Fiddler/Fiddler_cuechar.xml')