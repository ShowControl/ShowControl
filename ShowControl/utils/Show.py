#!/usr/bin/env python3
'''

Created on Nov 16, 2014

@author: mac
'''

from os import path

from ShowConf import ShowConf
from MixerConf import MixerConf
from MixerMap import MixerCharMap
from Cues import CueList
import configuration as cfg

class Show:
    '''
    The Show class contains the information and object that constitute a show
    '''


    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        self.cfgdict = cfgdict
        self.show_confpath = self.cfgdict['Show']['folder'] + '/'
        self.show_conf = ShowConf(self.show_confpath + cfgdict['Show']['file'])
        self.mixer = MixerConf(path.abspath(path.join(path.dirname(__file__), '../', cfgdict['Mixer']['file'])),self.show_conf.settings['mxrmfr'],self.show_conf.settings['mxrmodel'])
        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'], self.mixer.input_count)
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
        self.cues.selectedcueindex = 0
        self.cues.setcurrentcuestate(self.cues.currentcueindex)

    def loadNewShow(self, newpath):
        '''
            :param sho_configpath: path to new ShowConf.xml
            :return:
        '''
        print(self.cfgdict)
        self.show_confpath, showfile = path.split(newpath)
        #self.show_confpath = path.dirname(newpath)
        self.show_confpath = self.show_confpath + '/'
        self.cfgdict['Show']['folder'] = self.show_confpath
        self.cfgdict['Show']['file'] = showfile
        cfg.updateFromDict(self.cfgdict)
        cfg.write()
        self.show_conf = ShowConf(self.show_confpath + self.cfgdict['Show']['file'])
        self.mixer = MixerConf(path.abspath(path.join(path.dirname(__file__), '../ShowControl/', self.cfgdict['Mixer']['file'])),self.show_conf.settings['mxrmfr'],self.show_conf.settings['mxrmodel'])
        self.chrchnmap = MixerCharMap(self.show_confpath + self.show_conf.settings['mxrmap'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'], self.mixer.input_count)
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
        self.cues.selectedcueindex = 0
        self.cues.setcurrentcuestate(self.cues.currentcueindex)
        self.displayShow()

    def displayShow(self):
        '''
        Update the state of the mixer display to reflect the newly loaded show
        '''
        print(path.join(path.dirname(__file__)))
        print(path.abspath(path.join(path.dirname(__file__))) + '/')
        #print('Show Object:',The_Show)
        #print(The_Show.show_conf.settings['mxrmapfile'])
        insliders = self.mixer.inputsliders
        #print('Input Slider Count: ' + str(len(insliders)))
        for x in range(1, len(insliders)+1):
            sliderconf = insliders['Ch' + '{0:02}'.format(x)]
            #print('level: ' + str(sliderconf.level))
            #print('scribble: ' + sliderconf.scribble_text)
        outsliders = self.mixer.outputsliders
        #print('Output Slider Count: ' + str(len(outsliders)))
        for x in range(1, len(outsliders)+1):
            sliderconf = outsliders['Ch' + '{0:02}'.format(x)]
            #print('level: ' + str(sliderconf.level))
            #print('scribble: ' + sliderconf.scribble_text)

        #print(The_Show.cues)
        qs = self.cues.cuelist.findall('cue')
        for q in qs:
             print(q.attrib)

        #print(The_Show.chrchnmap)
        chs = self.chrchnmap.maplist.findall('input')
        # for ch in chs:
        #     print(ch.attrib)
