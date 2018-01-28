"""
Created on Mon Jan  8 14:18:09 EST 2018
StripChar object that maintains the map of mixer strip uuid to character uuid
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

class StripChar():
    """
    StripChar object contains the character state for each actors of a project
    """
    def __init__(self, stripcharfilename):
        """"""
        logging.info('In StripChar init')
        self.stripcharlist = []
        self.stripcharcount = 0
        self.cue = []
        self.setup_charstrip(stripcharfilename)

    def setup_charstrip(self, filename):
        logging.info('In CharStrip setup_charstrip')
        self.stripcharlist = ET.parse(filename)
        cues = self.stripcharlist.findall('.cues')
        self.stripcharcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        self.cue = self.stripcharlist.find(".cues/actors[@uuid='" + uuid + "']")
        return self.cue

    def get_stripchar_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        char_uuid = ""
        try:
            strip = self.cue.find(".strip[@uuid='" + uuid + "']")
            char_uuid = strip.find("char").get("uuid")
        except:
            logging.error("strip uuid: {}, char_uuid: {}".format(uuid, char_uuid))
        return char_uuid
