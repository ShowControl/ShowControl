import configuration as cfg

import styles

#cfgdict = cfg.toDict()

from ShowConf import ShowConf
from Cues import CueList


class Show:
    '''
    The Show class contains the information and object that constitute a show
    '''
    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        self.show_confpath = cfgdict['Show']['folder'] + '/'
        self.show_conf = ShowConf(self.show_confpath + cfgdict['Show']['file'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'])
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
#        self.cues.setcurrentcuestate(self.cues.currentcueindex)

    def loadNewShow(self, newpath):
        '''
            :param sho_configpath: path to new ShowConf.xml
            :return:
        '''
        print(cfgdict)
        self.show_confpath, showfile = path.split(newpath)
        #self.show_confpath = path.dirname(newpath)
        self.show_confpath = self.show_confpath + '/'
        cfgdict['Show']['folder'] = self.show_confpath
        cfgdict['Show']['file'] = showfile
        cfg.updateFromDict(cfgdict)
        cfg.write()
        self.show_conf = ShowConf(self.show_confpath + cfgdict['Show']['file'])
        self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'])
        self.cues.currentcueindex = 0
        self.cues.setcurrentcuestate(self.cues.currentcueindex)
        self.displayShow()

    def displayShow(self):
        '''
        Update the state of the mixer display to reflect the newly loaded show
        '''
        #print(self.cues)
        qs = self.cues.cuelist.findall('cue')
        for q in qs:
             print(q.attrib)