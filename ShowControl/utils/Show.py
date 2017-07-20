import logging
from ShowConf import ShowConf
from Cues import CueList

class Show():
    '''
    The Show class contains the information and object that constitute a show
    '''
    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        logging.info('In Show.py')
        self.cfgdict = cfgdict
        self.show_confpath = self.cfgdict['configuration']['project']['folder'] + '/'
        self.show_conf = ShowConf(self.cfgdict)
        # todo mac - hardwired to look only at href1
        '''This is currently hardwired to only one cue file.
        show_conf.settings['cues'] is a dictionary with a href to all cue files spec'd in the project.xml
        but no process to munge multiple cues at this point 7/13/17'''
        # begin hardwire
        cuefile_dict = self.show_conf.settings['cues']
        # project specific cue files are in href1
        cuefile = cuefile_dict['href1']
        # end hardwire
        self.cues = CueList(self.show_confpath + cuefile)
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
#        self.cues.setcurrentcuestate(self.cues.currentcueindex)

    def loadNewShow(self, cfgdict):
        '''
            :param sho_configpath: path to new ShowConf.xml
            :return:
        '''
        # -------------------begin: Old stuff
        # print(cfgdict)
        # self.show_confpath, showfile = path.split(newpath)
        # #self.show_confpath = path.dirname(newpath)
        # self.show_confpath = self.show_confpath + '/'
        # self.cfgdict['project']['folder'] = self.show_confpath
        # self.cfgdict['project']['file'] = showfile
        # cfg.updateFromDict(self.cfgdict)
        # cfg.write()
        # self.show_conf = ShowConf(self.show_confpath + self.cfgdict['project']['file'])
        # self.cues = CueList(self.show_confpath + self.show_conf.settings['mxrcue'])
        # self.cues.currentcueindex = 0
        # self.cues.setcurrentcuestate(self.cues.currentcueindex)
        # self.displayShow()
        # -------------------end: Old stuff
        self.cfgdict = cfgdict
        self.show_confpath = self.cfgdict['configuration']['project']['folder'] + '/'
        self.show_conf = ShowConf(self.cfgdict)
        self.cues = CueList(self.show_confpath + self.show_conf.settings['project']['cues'])
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
        self.displayShow()


    def reloadShow(self, cfgdict):
        self.show_confpath = cfgdict['project']['folder'] + '/'
        self.show_conf = ShowConf(cfgdict)
        self.cues = CueList(self.show_confpath + self.show_conf.settings['project']['cues'])
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
        self.displayShow()

    def displayShow(self):
        '''
        Update the state of the mixer display to reflect the newly loaded show
        '''
        #print(self.cues)
        qs = self.cues.cuelist.findall('cue')
        # for q in qs:
        #      print(q.attrib)
