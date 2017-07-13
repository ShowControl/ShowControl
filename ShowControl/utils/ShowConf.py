#!/usr/bin/env python3
'''
Created on Oct 19, 2014
Show configuration object
contains information defining the show
@author: mac
'''

import os
import sys
import inspect
from os import path

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)

from ShowControlConfig import configuration, CFG_DIR, CFG_PATH
#cfg = configuration()

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

class ShowConf:
    '''
    Created on Oct 19, 2014
    ShowConf object contains information defining the show
    returns a dictionary containing the settings defining a show
    reads settings from file showconf_file
    keys in ShowConf dictionary:
        name       : <name of the show>
        mixers     : dictionary of mixer for the show containing
                    {<id>: {"mxrmfr": <str>, "mxrmodel": <str>}}
        xxx mxrmfr     : <mixer manufacturer> xxx
        xxx mxrmodel   : <mixer model> xxx
        mxrmapfile : <xml file containing channel to actor map>
        cuefile : <xml file containing mixer cues for the show>
    @author: mac
    '''
    def __init__(self, cfgdict):
        self.cfgdict = cfgdict
        self.settings = {}
        self.equipment = {}
        showconf_file = self.cfgdict['project']['folder'] + '/' + self.cfgdict['project']['file']
        tree = ET.parse(showconf_file)
        self.doc = tree.getroot()
        # print(doc)
        self.projecttodict()
        self.equiptodict()
        # #Get mixer chan to actor/char map file name
        # mxrmap = self.doc.find('mixermap')
        # attribs = mxrmap.attrib
        # self.settings["mxrmap"] = attribs['file']

        #Get mixer chan to actor/char map file name
        # cues = self.doc.find('cuefile')
        # attribs = cues.attrib
        # self.settings["cuefile"] = attribs['file']
        
        # print(self.settings)
        # self.name = self.doc.find('title')
        # print('ShowConf.__init__ name: ',self.name.text)
        # self.settings['title'] = self.name.text
        return

    def projecttodict(self):
        version_element = self.doc.find('./project/version')
        version = version_element.text
        self.settings['version'] = version
        title_element = self.doc.find('./project/title')
        title = title_element.text
        self.settings['title'] = title
        eq_dict = {}
        eq_files = {}
        equipment_elements = self.doc.findall('./project/equipment')
        for i, eq_element in enumerate(equipment_elements):
            eq_files['href{0}'.format(i)] = eq_element.get('href')
        eq_dict['equipment'] = eq_files
        cues_elements = self.doc.findall('./project/cues')
        cues_dict = {}
        cues_files = {}
        self.settings['equipment'] = eq_files
        for i, cues_element in enumerate(cues_elements):
            cues_files['href{0}'.format(i)] = cues_element.get('href')
        cues_dict['equipment'] = cues_files
        self.settings['cues'] = cues_files
        return


    def equiptodict(self):
        equip_files_dict = self.settings['equipment']
        key_list = list(equip_files_dict.keys())
        key_list.sort()
        key_count  = len(key_list)
        mixer_dict = {}
        program_dict = {}
        for key in key_list:
            print(equip_files_dict[key])
            equipment_file = self.cfgdict['project']['folder'] + '/' + equip_files_dict[key]
            tree = ET.parse(equipment_file)
            equipdoc = tree.getroot()
            # print(doc)
            version_element = equipdoc.find('./equipment/version')
            version = version_element.text
            self.equipment['version'] = version
            # handle mixers
            mixers_dict = equipdoc.findall('./equipment/mixers/mixer')
            for mixer in mixers_dict:
                id = mixer.get('id')
                mfr = mixer.find('./mfr').text
                model = mixer.find('./model').text
                IP_address = mixer.find('./IP_address').text
                port = mixer.find('./port').text
                midi_address = mixer.find('./MIDI_address').text
                mixer_dict[id] = {'mfr': mfr, 'model': model, 'IP_address' : IP_address, 'port' : port, 'MIDI_address' : midi_address}
                pass
            self.equipment['mixers'] = mixer_dict
            # handle programs
            programs_dict = equipdoc.findall('./equipment/program')
            for program in programs_dict:
                id = program.get('id')
                portnum = program.find('./port').text
                IP_address = program.find('./IP_address').text
                midi_address = program.find('./MIDI_address').text
                program_dict[id] = {'port': portnum, 'IP_address' : IP_address, 'MIDI_address' : midi_address}
                pass
            self.equipment['program'] = program_dict

        return


if __name__ == "__main__":
    cfg = configuration()
    show_conf = ShowConf(cfg.cfgdict)
    pass