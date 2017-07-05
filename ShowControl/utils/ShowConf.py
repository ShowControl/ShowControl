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
        for child in self.doc:
            print('Child tag: {0}'.format(child.tag))
            print('Attribs: {0}'.format(child.attrib))
            if child.find('*') != None:
                chlddict = {}
                for kid in child:
                    print('kid tag: {0}'.format(kid.tag))
                    print('value: {0}'.format(kid.text))
                    chlddict[kid.tag] = kid.text.strip('\n\t')
                    self.settings[child.tag]=chlddict
            else:
                self.settings[child.tag] = child.text.strip('\n\t')

        return


    def equiptodict(self):
        equipment_file = self.cfgdict['project']['folder'] + '/' + self.settings['project']['equipment']
        tree = ET.parse(equipment_file)
        equipdoc = tree.getroot()
        # print(doc)
        allequip = equipdoc.findall('./equipment/*')
        # if allequip.__len__() != 0:
        if allequip:
            for equipitem in allequip:
                itmlist = {}
                items = equipitem.findall('./*')
                if items:
                    for item in items:
                        # print('item: {0}'.format(item.tag))
                        itemattribs = item.attrib
                        if 'id' in itemattribs:
                            if itemattribs['id'].isnumeric():
                                itemindex = int(itemattribs['id'])
                            else:
                                itemindex = itemattribs['id']
                            # print('id: {0} of {1}'.format(itemattribs['id'], itemattribs.__len__()))
                            subitems = item.findall('./*')
                            subitemdict = {}
                            for subitem in subitems:
                                subitemattribs = subitem.attrib
                                if subitemattribs:
                                    subitemdict[subitem.tag] = subitemattribs
                                else:
                                    subitemdict[subitem.tag] = subitem.text
                            itmlist[itemindex] = subitemdict
                    self.equipment[equipitem.tag] = itmlist
                else:
                    self.equipment[equipitem.tag] = equipitem.text
        # programs = equipdoc.findall('./equipment/programs/*')
        # if programs.__len__() != 0:
        #     for program in programs:
        #         print('tag: {0}'.format(program.tag))
        #         try:
        #             print('attribs: {0}'.format(program.attrib))
        #         except:
        #             pass
        #
        # mixers = equipdoc.findall('./equipment/mixers/*')
        # for child in programs:
        #     if child.attrib.__len__() != 0:
        #         print('Child tag: {0}  Attribs: {1}'.format(child.tag, child.attrib))
        #     else:
        #         print('Child tag: {0}  Text: {1}'.format(child.tag, child.text))
        #     if child.find('*') != None:
        #         chlddict = {}
        #         for kid in child:
        #             print('kid tag: {0}'.format(kid.tag))
        #             print('value: {0}'.format(kid.text))
        #             #chlddict[kid.tag] = kid.text.strip('\n\t')
        #             self.equipment[child.tag]=chlddict
        #     else:
        #         self.equipment[child.tag] = child.text.strip('\n\t')

        return

        # Get mixer info
        # mixers = doc.find('mixers')
        # self.settings['mixers'] = {}
        # for mixer in mixers:
        #     # print(mixer.attrib)
        #     mxrid = int(mixer.attrib['id'])
        #     self.settings['mixers'][mxrid] = {'mxrmodel':mixer.attrib['model'], 'mxrmfr':mixer.attrib['mfr'], 'address':mixer.attrib['address']}
        # return


if __name__ == "__main__":
    cfg = configuration()
    show_conf = ShowConf(cfg.cfgdict)
    pass