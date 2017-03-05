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

    def mixer_list(self):
        ret_list = []
        for mixer in self.mixers:
            mxattribs = mixer.attrib
            ret_list.append(mxattribs['mfr'])
        return ret_list

    def mixermodel_list(self):
        ret_list = []
        for mixer in self.mixers:
            mxattribs = mixer.attrib
            ret_list.append(mxattribs['model'])
        return ret_list

    def mixerprotocol(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.protocol = mixer.find('protocol').text
        return self.protocol

    def mixermutestyle(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
                self.mutestyle = 'illuminated'
        elif 'dark' in mutestyleattribs:
                self.mutestyle = 'dark'
        return self.mutestyle

    def mixercountbase(self, mixername, mixermodel):
        for mixer in self.mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.s_countbase = mixer.find('countbase').text.replace('"','')
        return self.s_countbase