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
        return

    def getconfdict(self):
        for child in self.doc:
            print('Child tag: {0}'.format(child.tag))
            print('Attribs: {0}'.format(child.attrib))

        return

if __name__ == "__main__":
    conf = configuration()
    conf.getconfdict()
    pass