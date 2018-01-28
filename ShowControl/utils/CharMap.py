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

class CharMap():
    """
    CHarMAp object contains the characters of a project
    """
    def __init__(self, charmapfilename):
        """"""
        logging.info('In StripSet init')
        self.charmaplist = []
        self.charmapcount = 0
        self.chars = []
        self.setup_charmap(charmapfilename)

    def setup_charmap(self, filename):
        logging.info('In CharMap setup_charmap')
        self.charmaplist = ET.parse(filename)
        self.chars = self.charmaplist.findall('.chars/char')
        self.charmapcount = len(self.chars)
        return

    def get_char_by_uuid(self, uuid):
        """return the <chars> element for this uuid
        the <chars> element contains an element for each mixer strip
        each character element contains info for this chars
        for example, the mute status or slider level, etc."""
        char_name = ""
        actor_uuid = ""
        try:
            char_element = self.charmaplist.find(".chars/char[@uuid='" + uuid + "']")
        except:
            logging.error("char uuid: {} not found!".format(uuid))
        try:
            char_name = char_element.find("name").text
        except:
            logging.error("char uuid: {} name not found not found!".format(uuid))
        try:
            actor_uuid = char_element.find("actor").text
        except:
            logging.error("char uuid: {} actor not found!".format(uuid))
        return [char_name, actor_uuid]
