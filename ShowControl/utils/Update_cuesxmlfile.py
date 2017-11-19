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
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

class Id_split():
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
        self.cues = self.cuelist_root.findall(".cues/cue")

        for cue in self.cues:
            cue_id_element = cue.find('.Id')
            cue_id = cue_id_element.text
            if '.' in cue_id:
                page, line = cue_id.split('.')
            else:
                page = ''
                line = cue_id
            print('integer: {}, fraction: {}'.format(page, line))
            cue_id_element.text = line
        return

    def write(self, newxml,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newxml)
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
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        newdoctree.write(filename, encoding="UTF-8", xml_declaration=True)
        logging.debug('Configuration written to: ' + filename)

        return



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename='Update_cuesfilexml.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    cuecharobj = Id_split()
    cuecharobj.toXMLdoc()
    cuecharobj.write(cuecharobj.cuelist_root, False, '/home/mac/Shows/Fiddler/Fiddler_cuesupdate.xml')