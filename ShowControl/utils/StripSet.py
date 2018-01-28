"""
Created on Sat Jan 27 10:25:49 EST 2018
StripSet object that maintains the map of
mixer strip uuid to character uuid or stripset uuid
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

class StripSet():
    """
    StripSet object contains the set of details about the strip settings
    """
    def __init__(self, stripsetfilename):
        """"""
        logging.info('In StripSet init')
        self.stripsetlist = []
        self.stripsetcount = 0
        self.cue = []
        self.setup_stripset(stripsetfilename)

    def setup_stripset(self, filename):
        logging.info('In StripSet setup_stripset')
        self.stripsetlist = ET.parse(filename)
        cues = self.stripsetlist.findall('.cues')
        self.stripsetcount = len(cues)

    def get_cue_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each character
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        self.cue = self.stripsetlist.find(".cues/cue[@uuid='" + uuid + "']")
        return self.cue

    def get_stripset_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each mixer strip
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        char_uuid = ""
        stripset_uuid = ""
        try:
            strip = self.cue.find(".strip[@uuid='" + uuid + "']")
        except:
            logging.error("strip uuid: {} not found!".format(uuid))
        try:
            char_uuid = strip.find("char").get("uuid")
        except:
            logging.error("strip uuid: {}, char not found!".format(uuid))
        try:
            stripset_uuid = strip.find("stripset").get("uuid")
        except:
            logging.error("strip uuid: {}, stripset not found!".format(uuid))
        return [char_uuid, stripset_uuid]
