'''
Created on Fri Oct 13 11:48:35 EDT 2017
Cue object that maintains the current cue list
@author: mac
'''

import sys
import inspect
import os
import shutil
import uuid
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import logging

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

class BuildChar():
    def __init__(self):
        pass
    def build_char_file(self):
        self.maptree = ET.parse('/home/mac/SharedData/ShowSetups/Shows/Fiddler/MixerMap.xml')
        self.maproot = self.maptree.getroot()
        maps = self.maproot.findall("./mixermap")
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

if __name__ == "__main__":
    BC = BuildChar()
    BC.build_char_file()