#!/usr/bin/env python3
'''
Created on Oct 19, 2014
Show configuration object
contains information defining the show
@author: mac
'''

import os
import sys
import inspect
import shutil
from os import path
import logging

from PyQt5 import QtWidgets

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

HOME = os.path.expanduser("~")

CFG_DIR = HOME + '/.config/ShowControl'
CFG_PATH = CFG_DIR + '/ShowControl_config.xml'
LOG_DIR = HOME + '/.log/ShowControl'

class configuration():
    def __init__(self):
        self.logger = logging.getLogger('Show')
        self.logger.info('In configuration.init')
        self.logger.info('message from configuration')
        self.settings = {}
        tree = ET.parse(CFG_PATH)
        self.doc = tree.getroot()
        self.logger.debug(ET.tostring(self.doc))
        #print('Root tag: {0}'.format(self.doc.tag))
        #print('{0} attribs: {1}'.format(self.doc.tag, self.doc.attrib))
        self.logger.debug('Root tag: {0}'.format(self.doc.tag))
        self.logger.debug('{0} attribs: {1}'.format(self.doc.tag, self.doc.attrib))
        self.cfgdict = self.toDict()
        return

    def toDict(self):
        # todo - mac need to handle <prefs><n component><n subelements>
        retdict = {'configuration': {}}
        configuration_element = self.doc.find('./configuration')

        # get version of configuration file
        version_element = configuration_element.find('./version')
        try:
            version_val = version_element.text
            version_val = version_val.strip()
        except AttributeError:
            version_val = None # todo - mac should throw warning about no version
        retdict['configuration']['version'] = version_val

        # get project configuration
        project_element = configuration_element.find('./project')
        folder_element = project_element.find('./folder')
        try:
            folder = folder_element.text
            folder = folder.strip()
        except AttributeError:
            folder = None # todo - mac throw warning about no folder
        file_element = project_element.find('./file')
        try:
            file = file_element.text
            file = file.strip()
        except AttributeError:
            file = None # todo - mac throw warning about no file
        retdict['configuration']['project'] = {'file': file, 'folder' : folder}
        mixers_element = configuration_element.find('./mixers')
        folder_element = mixers_element.find('./folder')
        try:
            folder = folder_element.text
            folder = folder.strip()
        except AttributeError:
            folder = None # todo - mac throw warning about no folder
        file_element = mixers_element.find('./file')
        try:
            file = file_element.text
            file = file.strip()
        except AttributeError:
            file = None # todo - mac throw warning about no file
        retdict['configuration']['mixers'] = {'file': file, 'folder' : folder}

        prefs_element = configuration_element.find('./prefs')
        exitwithce_element = mixers_element.find('./exitwithce')
        try:
            exitwithce_val = exitwithce_element.text
            exitwithce_val = exitwithce_val.strip()
        except AttributeError:
            exitwithce_val = None # todo - mac throw warning about no folder
        retdict['configuration']['prefs'] = {'exitwithce': exitwithce_val}

        # for child in self.doc:
        #     print('Child tag: {0}'.format(child.tag))
        #     print('Attribs: {0}'.format(child.attrib))
        #     if child.find('*') != None:
        #         chlddict = {}
        #         for kid in child:
        #             print('kid tag: {0}'.format(kid.tag))
        #             print('value: {0}'.format(kid.text))
        #             chlddict[kid.tag] = kid.text.strip('\n\t')
        #             retdict[child.tag]=chlddict
        #     else:
        #         retdict[child.tag] = child.text.strip('\n\t')
        logging.info(str(retdict))
        return retdict

    def updateFromDict(self):
        newdoc = ET.Element('show_control')
        for key in self.cfgdict:
            print('key: {0}'.format(key))
            firstlevelel = ET.SubElement(newdoc, key)
            if type(self.cfgdict[key]) is not dict:
                print('**')
                print(self.cfgdict[key])
                firstlevelel.text = self.cfgdict[key]
            else:
                children = self.cfgdict[key]
                for child in children:
                    print('child: {0}, childval: {1}'.format(child, children[child]))
                    secondlevel = ET.SubElement(firstlevelel, child)
                    child_item = children[child]
                    if type(child_item) is dict:
                        for item in child_item:
                            thirdlevel = ET.SubElement(secondlevel, item)
                            thirdlevel.text = child_item[item]
                    else:
                        secondlevel.text = children[child]
                    pass
        return newdoc

    def write(self, newconfig,  revision=True, filename=''):
        """save the new config file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newconfig)
        if filename == '':
            self.logger.debug('Configuration not saved, no filename provided!')
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
            self.logger.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        # else:
        #     newdoctree.write(filename)
        #     self.logging.debug('Configuration written to: ' + filename)
        newdoctree.write(filename, xml_declaration=True)
        self.logger.debug('Configuration written to: ' + filename)

        return

    def reload(self):
        tree = ET.parse(CFG_PATH)
        self.doc = tree.getroot()



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename='ShowControlConfig.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    conf = configuration()
    cfgdict = conf.toDict()
    logging.info(str(cfgdict))
    # newconf = conf.updateFromDict()
    # conf.write(newconf, True, CFG_PATH)
    pass