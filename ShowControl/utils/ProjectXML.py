'''
Created on Fri Oct 13 11:48:35 EDT 2017
Tools for building project xml files
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

class ProjectXML():
    """
    Builder for project xml file
    """
    def __init__(self):
        """"""
        logging.info('In ProjectXML init')

    def toXMLdoc(self, title, name, venue):
        showcontrol = ET.Element('showcontrol')
        project = ET.SubElement(showcontrol, 'project')
        ET.SubElement(project, 'version').text = '1.0'
        ET.SubElement(project, 'title').text = title
        ET.SubElement(project, 'equipment', attrib={'href':venue + '_equipment.xml'})
        ET.SubElement(project, 'equipment', attrib={'href':name + '_equipment.xml'})
        ET.SubElement(project, 'mixermap', attrib={'href':'MixerMap.xml'})
        ET.SubElement(project, 'charmap', attrib={'href':name + '_char.xml'})
        ET.SubElement(project, 'actormap', attrib={'href': name + '_actor.xml'})
        ET.SubElement(project, 'cuechar', attrib={'href':name + '_cuechar.xml'})
        ET.SubElement(project, 'cues', attrib={'href':venue + '_cues.xml'})
        ET.SubElement(project, 'cues', attrib={'href':name + '_cues.xml'})
        return showcontrol

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
        oldroot, extension = path.splitext(filename)
        if revision:
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)
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
    TEST_DIR = '/home/mac/SharedData/ShowSetups/Shows/TestProj'
    TEST_PATH = os.path.join(TEST_DIR, 'Test_project.xml')
    logging.basicConfig(level="INFO",
                        filename=LOG_DIR + '/ProjectXML.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    logging.info("In Char.__main__")
    prjxml = ProjectXML()
    newdoc = prjxml.toXMLdoc('Really big shue', 'Bigshue', 'Amato')
    prjxml.write(newdoc, False, TEST_PATH)