#!/usr/bin/env python3
"""
Created on Oct 19, 2014
MixerConf mixer configuration object

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

#from SCLog import SCLog

from MixerControl import ControlFactory, supported_protocols, supported_controls


class MixerConf():
    '''
    Created on Oct 19, 2014
    MixerConf object returns the configuration of the mixer specified
    by the mixername and mixermodel arguments.
    
    It searches the file specified in mixerconf_file for the mixer specified
    by the mixername and mixermodel arguments.  
    
    MixerConf structure:
    MixerConf
        protocol (string)
        mutestyle (dictionary)
        mxrstrips (dictionary)
        mxrconsole (list)
        IP (string)
        PORT (int)
        MIDICHAN (int)
    @author: mac
    '''
    def __init__(self, mixerconf_file, mixername, mixermodel, mixeraddress):
        logging.info('MixerConf __init__')
        self.mutestyle = {}
        ''' dictionary of mutestyle  and values that activate a mute or unmute for the mixer
        mutestyle referes to how the mixer indicates the channel is muted
        for example, the Yamaha 01V indicates a channel is un-muted with an illuminated light
        other mixer indicate a muted channel with an illuminated light
        mutestyle['mutestyle'] will be the string 'illuminated' or 'dark'
                               as read from <mixerdefs>.xml for each particular mixer
        for mutestyle['mute'] will be the value to send to mute the mixer
        for mutestyle['unmute'] will be the value to send to unmute the mixer'''

        '''mxrstrips is a dictionary of controls for a type of strip.
        mxrstrips will have a key for each strip type (input, output, auuxin, etc.)
        each strip type will have a dictionary of it's associated control objects.
        Controls objects are based on the protocol of the mixer. (See MixerControl.py)'''
        self.mxrstrips = {}

        '''mxrconsole is a list of all the strips on the mixer.
        This is used for the layout on the GUI and to work on a sigle strip
        or interate through all strips on the mixer.
        Each element of the list will have a dictionary with the strip name and strip type'''
        self.mxrconsole = []

        mixerdefs = ET.parse(mixerconf_file)
        mixers = mixerdefs.getroot()
        #print('mixers: ' + str(mixers))
        for mixer in mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.protocol = mixer.find('protocol').text
        #print('protocol: ' + self.protocol)
        self.IP = ''
        self.PORT = 0
        self.MIDICHAN = 0
        if self.protocol == 'osc':
            self.IP, port = mixeraddress.split(',')
            self.PORT = int(port)
        elif self.protocol == 'midi':
            self.MIDICHAN = int(mixeraddress)
        mutestyleattribs = mixer.find('mutestyle').attrib
        if 'illuminated' in mutestyleattribs:
            self.mutestyle['mutestyle'] = 'illuminated'
        else:
            self.mutestyle['mutestyle'] = 'dark'
        self.mutestyle['mute'] = int(mutestyleattribs['mute'])
        self.mutestyle['unmute'] = int(mutestyleattribs['unmute'])

        s_countbase = mixer.find('countbase').text
        i_countbase = int(s_countbase.replace('\"', ''))
        firstchan = 1  # wonky way to fix issue with X32: CH1 >> 01, yamaha: CH1 is 0 offset from a midi value
        if i_countbase == 1:
            firstchan = 0
        strips = mixer.findall('strip')
        for strip in strips:
            stripattribs = strip.attrib
            self.mxrstrips[stripattribs['type']] = {}
            for cntrltype in supported_controls:
                try:
                    cntrl = strip.find(cntrltype)
                    cntrlattribs = cntrl.attrib
                    cntrlcls = ControlFactory.create_control(cntrltype, self.protocol)
                    commandstring = cntrlattribs['cmd']
                    if self.protocol == 'midi' and cntrlattribs['cmd'] != '':
                        controlchange, changenumbase, val = cntrlattribs['cmd'].split(',')
                        commandstring = '{0},{1},{2}'.\
                                            format(controlchange.replace('#', '{:1x}'.format(self.MIDICHAN)),\
                                            changenumbase, val)
                    cntrlcls.fill(cntrlattribs['cmdtyp'], commandstring, cntrlattribs['range'], cntrlattribs['anoms'])
                    self.mxrstrips[stripattribs['type']].update({cntrltype: cntrlcls})
                except:
                    pass
            self.cntrlcount = int(stripattribs['cnt'])
            for x in range(i_countbase, self.cntrlcount + i_countbase):
                self.mxrconsole.append(
                    {'name': stripattribs['name'] + '{0:02}'.format(x + firstchan), 'type': stripattribs['type'],
                     'channum': x})

