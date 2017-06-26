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

from Show import Show
from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
import CommHandlers
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, header, cue_fields

cfg = configuration()
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

class CueBuilder:
    def __init__(self, cuefilename):
        return

if __name__ == "__main__":
    print(CFG_PATH)