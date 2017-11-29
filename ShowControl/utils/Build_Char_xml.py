'''
Created on Fri Oct 13 11:48:35 EDT 2017
Cue object that maintains the current cue list
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

class BuildChar():
    def __init__(self):
        pass
    def build_char_file(self):
        self.maptree = ET.parse('/home/mac/SharedData/ShowSetups/Shows/Fiddler/MixerMap.xml')
        self.maproot = self.maptree.getroot()
        someET = minidom.parseString(ET.tostring(self.maproot)).toprettyxml()
        maps = self.maproot.find("./mixermap")
        self.map_list = []
        map = self.maproot.find("./mixermap[@count='0']")
        inputs = map.findall('input')
        # build file name
        name = 'FiddlerChar'
        cf = os.path.join('/home/mac/SharedData/ShowSetups/Shows/Fiddler/', '{}_char.xml'.format(name))
        of = open(cf,mode='w')
        of.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        of.write('<show_control>\n')
        of.write('    <version>1.0</version >\n')
        of.write('    <chars>\n')
        for mxrin in inputs:
            actor = mxrin.get('actor')
            char = mxrin.get('char')
            print(actor,char)
            of.write('      <char uuid="{}">\n'.format(uuid.uuid4()))
            of.write('       <name>"{}"</name>\n'.format(char))
            of.write('       <actor>"{}"</actor>\n'.format(actor))
            of.write('      </char>\n')
        of.write('    </chars>\n')
        of.write('</show_control>\n')
        of.close()

        # self.mm_element_list = ET.parse('/home/mac/SharedData/ShowSetups/Shows/CharTest/MixerMap.xml')
        # self.mm_list_root = self.char_element_list.getroot()
        # self.mm__element = self.charlist_root.find('showcontrol')
        # self.char_element_list = self.chars_element.findall('char')
        # tf = os.path.join(SHOWS, 'CharTest', '{}_char.xml'.format('FromMixerMap'))
        #
        # for char in self.char_element_list:
        #     print()
        return

class SplitCharsnActors():
    def __init__(self):
        pass
    def split_to_files(self):
        self.chars_tree = ET.parse('/home/mac/SharedData/ShowSetups/Shows/Fiddler/FiddlerChar_char.xml')
        self.chars_root = self.chars_tree.getroot()
        self.chars = self.chars_root.find("./chars")
        self.chars_list = self.chars.findall("./char")
        # Start the character tree
        chars_tree = ET.Element('showcontrol')
        chars_element = ET.SubElement(chars_tree, 'chars')
        ET.SubElement(chars_element, 'version').text = '1.0'
        # Start the actor tree
        actors_tree = ET.Element('showcontrol')
        actors_element = ET.SubElement(actors_tree, 'actors')
        ET.SubElement(actors_element, 'version').text = '1.0'

        for char in self.chars_list:
            char_uuid = char.get('uuid')
            char_name = char.find("./name").text
            actor = char.find("./actor").text
            actor_uuid = '{}'.format(uuid.uuid4())
            # add character to new chars element
            char_element = ET.SubElement(chars_element, 'char', {'uuid': char_uuid})
            ET.SubElement(char_element, 'name').text = char_name
            ET.SubElement(char_element, 'actor_uuid').text = actor_uuid
            # add actor to new actor element
            actor_element = ET.SubElement(actors_element, 'actor', {'uuid': actor_uuid})
            ET.SubElement(actor_element, 'name').text = actor
            ET.SubElement(actor_element, 'understudy_uuid').text = 'none'
            print('Char uuid: {}, Char name: {}, actor: {}'.format(char_uuid, char_name, actor))

        self.write(chars_tree, False, '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_char.xml')
        self.write(actors_tree, False, '/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_actor.xml')
        return

    def write(self, newchars,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newchars)
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

            # newdoctree.write(oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        filename_up = oldroot + '_up' + extension  # up >>> uglyprint
        newdoctree.write(filename_up, encoding="UTF-8", xml_declaration=True)
        of = open(filename, 'w')
        of.write(pretty_print(filename_up))
        of.close()

        logging.debug('Configuration written to: ' + filename)

        return


if __name__ == "__main__":
    # BC = BuildChar()
    # BC.build_char_file()
    SCA = SplitCharsnActors()
    SCA.split_to_files()
    pass