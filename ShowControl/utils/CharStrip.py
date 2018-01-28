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
    CueChar object contains the character state for each actors of a project
    """
    def __init__(self, charstripfilename):
        """"""
        logging.info('In CharStrip init')
        self.charstriplist = []
        self.charstripcount = 0
        self.cue = []
        self.setup_charstrip(charstripfilename)

    def setup_charstrip(self, filename):
        logging.info('In CharStrip setup_charstrip')
        # cuecharlist contains all elements *under* <showcontrol>
        self.charstriplist = ET.parse(filename)
        # getroot() return <showcontrol> and elements under it
        #self.cuecharlist_root = self.cuecharlist.getroot()
        cues = self.charstriplist.findall('.cues')
        self.charstripcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        self.cue = self.charstriplist.find(".cues/actors[@uuid='" + uuid + "']")
        return self.cue

    def get_charstrip_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        strip_uuid = ""
        try:
            char = self.cue.find(".char[@uuid='" + uuid + "']")
            strip_uuid = char.find("strip").get("uuid")
        except:
            logging.error("char uuid: {}, strip_uuid: {}".format(uuid, strip_uuid))
        return strip_uuid
