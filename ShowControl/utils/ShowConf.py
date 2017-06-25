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
cfg = configuration()

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
    def __init__(self, showconf_file):
        self.settings = {}
        tree = ET.parse(showconf_file)
        doc = tree.getroot()
        # print(doc)

        # Get mixer info
        mixers = doc.find('mixers')
        self.settings['mixers'] = {}
        for mixer in mixers:
            # print(mixer.attrib)
            mxrid = int(mixer.attrib['id'])
            self.settings['mixers'][mxrid] = {'mxrmodel':mixer.attrib['model'], 'mxrmfr':mixer.attrib['mfr'], 'address':mixer.attrib['address']}
        # print(self.settings['mixers'][1]['mxrmodel'])

        #Get mixer chan to actor/char map file name
        mxrmap = doc.find('mixermap')
        attribs = mxrmap.attrib
        self.settings["mxrmap"] = attribs['file']

        #Get mixer chan to actor/char map file name
        cues = doc.find('cuefile')
        attribs = cues.attrib
        self.settings["cuefile"] = attribs['file']
        
        # print(self.settings)
        self.name = doc.find('title')
        # print('ShowConf.__init__ name: ',self.name.text)
        self.settings['title'] = self.name.text

if __name__ == "__main__":
    show_confpath = cfg.cfgdict['project']['folder'] + '/'
    show_conf = ShowConf(show_confpath + cfg.cfgdict['project']['file'])
    pass