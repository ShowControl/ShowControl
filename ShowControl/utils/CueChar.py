'''
Created on Wed Oct 25 10:09:54 EDT 2017
CueChar object that maintains the character state for each cue
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

class CueChar():
    """
    CueChar object contains the character state for each cue of a project
    """
    def __init__(self, cuecharfilename):
        """"""
        logging.info('In CueChar init')
        self.setup_cuechar(cuecharfilename)

    def setup_cuechar(self, filename):
        logging.info('In CueList setup_cues')
        self.cuecharlist = ET.parse(filename)
        self.cuecharlist_root = self.cuecharlist.getroot()
        #self.cues_element = self.cuelist_root.find('cues')
        #self.cuelist.find(".cues/cue[@num='001']")
        cues = self.cuecharlist.findall('.cues/cue')
        self.cuecharcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        cue = self.cuecharlist_root.find(".cues/cue[@uuid='" + uuid + "']")
        return