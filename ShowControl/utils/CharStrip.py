"""
Created on Tue Dec 26 10:45:05 EST 2017
CharStrip object that maintains the map of character uuid to mixer strip uuid
@author: mac

"""

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

class CharStrip():
    """
    CueChar object contains the character state for each cue of a project
    """
    def __init__(self, charstripfilename):
        """"""
        logging.info('In CharStrip init')
        self.setup_cuechar(charstripfilename)

    def setup_cuechar(self, filename):
        logging.info('In CharStrip setup_cuechar')
        # cuecharlist contains all elements *under* <showcontrol>
        self.charstriplist = ET.parse(filename)
        # getroot() return <showcontrol> and elements under it
        #self.cuecharlist_root = self.cuecharlist.getroot()
        cues = self.charstriplist.findall('.chars')
        self.charstripcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        """return the <cue> element for this uuid
        the <cue> element contains an element for each character
        each character element contains info for this cue
        for example, the mute status or slider level, etc."""
        char = self.charstriplist.find(".chars/char[@uuid='" + uuid + "']")
        return char

