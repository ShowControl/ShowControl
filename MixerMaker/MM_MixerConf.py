#!/usr/bin/env python3
"""
Created on Mar 5, 2017
MM_MixerConf mixer configuration object

@author: mac
"""
__author__ = 'mac'
import logging
# logger = logging.getLogger(__name__)
# logger.info('Top of MixerConf')
# logger.debug('debug message')
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

# from MixerControl import ControlFactory, supported_protocols, supported_controls


class MixerConf:
    def __init__(self, mixerconf_file):
        self.mixerdefs = ET.parse(mixerconf_file)
        self.mixers = self.mixerdefs.getroot()
        self.mixer_count = len(self.mixers)
        self.mfr_list = []
        self.model_list = []
        self.protocol = ''
        self.mutestyle = ''
        self.s_countbase = ''
        self.mixer_list()

    def mixer_list(self):
        for mixer in self.mixers:
            mxattribs = mixer.attrib
            self.mfr_list.append(mxattribs['mfr'])
            self.model_list.append(mxattribs['model'])

    def mixerattribs(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.protocol = mixer.find('protocol').text
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
                self.mutestyle = 'illuminated'
        elif 'dark' in mutestyleattribs:
                self.mutestyle = 'dark'
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
                self.mutestyle = 'illuminated'
        elif 'dark' in mutestyleattribs:
                self.mutestyle = 'dark'
        self.s_countbase = mixer.find('countbase').text.replace('"','')

    def mixerstrips(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        return mixer.findall('strip')