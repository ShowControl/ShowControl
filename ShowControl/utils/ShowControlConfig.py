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
from os import path
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

CFG_DIR = HOME + '/.showcontrol'
CFG_PATH = CFG_DIR + '/ShowControl_config.xml'

class configuration():
    def __init__(self):
        self.settings = {}
        tree = ET.parse(CFG_PATH)
        self.doc = tree.getroot()
        print('Root tag: {0}'.format(self.doc.tag))
        print('{0} attribs: {1}'.format(self.doc.tag, self.doc.attrib))
        self.cfgdict = self.toDict()
        return

    def toDict(self):
        retdict = {}
        for child in self.doc:
            print('Child tag: {0}'.format(child.tag))
            print('Attribs: {0}'.format(child.attrib))
            if child.find('*') != None:
                chlddict = {}
                for kid in child:
                    print('kid tag: {0}'.format(kid.tag))
                    print('value: {0}'.format(kid.text))
                    chlddict[kid.tag] = kid.text.strip('\n\t')
                    retdict[child.tag]=chlddict
            else:
                retdict[child.tag] = child.text.strip('\n\t')

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
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Configuration not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        if revision:
            oldroot, extension = path.splitext(filename)
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            newdoctree.write(oldroot + '-{0}'.format(rev) + extension)
        else:
            newdoctree.write(filename)

        return

    def reload(self):
        tree = ET.parse(CFG_PATH)
        self.doc = tree.getroot()



if __name__ == "__main__":
    conf = configuration()
    cfgdict = conf.toDict()
    newconf = conf.updateFromDict()
    conf.write(newconf, True, CFG_PATH)
    pass