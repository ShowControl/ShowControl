'''
Created on Wed Nov 29 14:38:19 EST 2017
Char object that maintains the current cue list
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

import xml.dom.minidom as md
try:
    from lxml import ET
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as ET

pretty_print = lambda f: '\n'.join([line for line in md.parse(open(f)).toprettyxml(indent=' '*2).split('\n') if line.strip()])

class Actor():
    """
    Actor object contains actor list for a project
    """
    def __init__(self):
        """"""
        logging.info('In Actor init')
        self.actor_list = []

    def setup_cast(self, charfilename):
        """Load the specified xml file """
        logging.info('In Actors setup_cast')
        self.actor_element_tree = ET.parse(charfilename)
        self.actorlist_root = self.actor_element_tree.getroot()
        self.actors_element = self.actorlist_root.find('actors')
        self.actor_element_list = self.actors_element.findall('actor')
        self.actorcount = len(self.actor_element_list)
        return

    def actors_to_list_of_tuples(self):
        """Create a list of tuples from the character xml element list
        where each list element is a tuple (uuid, charname, actor)"""
        logging.info('In Actors cast_toDict')
        for actor in self.actor_element_list:
            self.actor_list.append((actor.get('uuid').strip('"'),
                                    actor.find('name').text.strip('"'),
                                    actor.find('understudy_uuid').text.strip('"')))
        return

    def actors_toxmldoc(self):
        """Create a new showcontrol element from the current state of the list of actor tuples"""
        newactorelements = {}
        showcontrol = ET.Element('showcontrol')
        ET.SubElement(showcontrol, 'version').text = '1.0'
        actors = ET.SubElement(showcontrol, 'actors')
        for actor in self.actor_list:
            actorchild = ET.SubElement(actors, 'actor', attrib={'uuid':actor[0]})
            ET.SubElement(actorchild, 'name').text = actor[1]
            ET.SubElement(actorchild, 'understudy_uuid').text = actor[2]
        return showcontrol

    def write(self, newActors,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newActors)
        if filename == '':
            logging.debug('Configuration not saved, no filename provided!')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Configuration not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        oldroot, extension = path.splitext(filename)
        if revision:
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        filename_up = oldroot + '_up' + extension  # up >>> uglyprint
        newdoctree.write(filename_up, encoding="UTF-8", xml_declaration=True)
        of = open(filename, 'w')
        of.write(pretty_print(filename_up))
        of.close()

        logging.debug('Configuration written to: ' + filename)

        return

    def create_new_project(self, folder, name):
        """create a new project
        folder = project folder
        name = new project name"""
        self.new_project_file(folder, name)
        self.new_actor_list(folder, name)
        return

    def new_project_file(self, folder, name):
        # create the new project folder
        newpath = os.path.join(folder, name)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        logging.info('new_project_file: {}'.format(newpath))
        return

    def new_actor_list(self, folder, name):
        """create an empty character list xml file"""
        # build file name
        actor_uuid = '{}'.format(uuid.uuid4())
        cf = os.path.join(folder, name, '{}_actor.xml'.format(name))
        of = open(cf,mode='w')
        of.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        of.write('<show_control>\n')
        of.write('    <version>1.0</version >\n')
        of.write('    <actors>\n')
        of.write('      <actor uuid="' + actor_uuid + '">\n')
        of.write('       <name>"Actor name"</name>\n')
        of.write('       <understudy_uuid>"None"</understudy_uuid>\n')
        of.write('      </actor>\n')
        of.write('    </actors>\n')
        of.write('</show_control>\n')
        of.close()
        return actor_uuid
