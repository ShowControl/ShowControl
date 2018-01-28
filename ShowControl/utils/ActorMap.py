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

class ActorMap():
    """
    ActorMap object contains the actor information for the project
    """
    def __init__(self, actormapfilename):
        """"""
        logging.info('In StripSet init')
        self.actormaplist = []
        self.actormapcount = 0
        self.actors = []
        self.setup_actormap(actormapfilename)

    def setup_actormap(self, filename):
        logging.info('In ActorMap setup_actormap')
        self.actormaplist = ET.parse(filename)
        self.actors = self.actormaplist.findall('.actors')
        self.actormapcount = len(self.actors)

    def get_actor_by_uuid(self, uuid):
        """return the <actors> element for this uuid
        the <actors> element contains an element for each mixer strip
        each character element contains info for this actors
        for example, the mute status or slider level, etc."""
        actor_name = ""
        understudy_uuid = ""
        try:
            actor_element = self.actormaplist.find(".actors/actor[@uuid='" + uuid + "']")
        except:
            logging.error("actor uuid: {} not found!".format(uuid))
        try:
            actor_name = actor_element.find("name").text
        except:
            logging.error("actor uuid: {} name not found not found!".format(uuid))
        try:
            understudy_uuid = actor_element.find("understudy_uuid").text
        except:
            logging.error("actor uuid: {} understudy not found!".format(uuid))
        return [actor_name, understudy_uuid]
