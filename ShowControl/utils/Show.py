import logging
from ShowControl.utils.ShowConf import ShowConf
from ShowControl.utils.Cues import CueList
from ShowControl.utils.CueChar import CueChar
from ShowControl.utils.CharStrip import CharStrip
from ShowControl.utils.StripChar import StripChar
from ShowControl.utils.StripSet import StripSet
from ShowControl.utils.ActorMap import ActorMap
from ShowControl.utils.CharMap import CharMap


class Show():
    '''
    The Show class contains the information and object that constitute a show
    '''
    def __init__(self, cfgdict):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('Show')
        self.logger.info('In Show.init')
        self.logger.debug('debug in Show.init')
        self.cfgdict = cfgdict
        self.logger.debug('cfgdict: {}'.format(cfgdict))
        self.show_confpath = self.cfgdict['configuration']['project']['folder'] + '/'
        self.show_conf = ShowConf(self.cfgdict)
        # todo mac - hardwired to look only at href1
        '''This is currently hardwired to only one actors file.
        show_conf.settings['cues'] is a dictionary with a href to all actors files spec'd in the project.xml
        but no process to munge multiple cues at this point 7/13/17'''
        # begin hardwire
        cuefile_dict = self.show_conf.settings['cues']
        # project specific actors files are in href1
        cuefile = cuefile_dict['href1']
        # end hardwire
        self.cues = CueList(self.show_confpath + cuefile)
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
#        self.cues.setcurrentcuestate(self.cues.currentcueindex)
        charmap_file = self.show_conf.settings['charmap']
        actormap_file = self.show_conf.settings['actormap']
        cuechar_file = self.show_conf.settings['cuechar']
        charstrip_file = self.show_conf.settings['charstrip']
        stripchar_file = self.show_conf.settings['stripchar']
        stripset_file = self.show_conf.settings['stripset']
        self.cuechar = CueChar(self.show_confpath + cuechar_file)
        # self.charstrip = CharStrip(self.show_confpath + charstrip_file)
        # self.stripchar = StripChar(self.show_confpath + stripchar_file)
        self.stripset = StripSet(self.show_confpath + stripset_file)
        self.actormap = ActorMap(self.show_confpath + actormap_file)
        self.charmap = CharMap(self.show_confpath + charmap_file)
        return

    def loadNewShow(self, cfgdict):
        '''
            :param sho_configpath: path to new ShowConf.xml
            :return:
        '''
        self.logger.info('In Show.loadNewShow')

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
        self.logger.debug('cfgdict: {}'.format(cfgdict))
        self.show_confpath = self.cfgdict['configuration']['project']['folder'] + '/'
        self.show_conf = ShowConf(self.cfgdict)
        self.cues = CueList(self.show_confpath + self.show_conf.settings['project']['cues'])
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0

        self.displayShow()


    def reloadShow(self, cfgdict):
        self.show_confpath = cfgdict['configuration']['project']['folder'] + '/'
        self.show_conf = ShowConf(cfgdict)
        # todo mac - hardwired to look only at href1
        '''This is currently hardwired to only one actors file.
        show_conf.settings['cues'] is a dictionary with a href to all actors files spec'd in the project.xml'''
        #self.cues = CueList(self.show_confpath + self.show_conf.settings['cues']['href1'])
        # changed to below, from above, shouldn't have to recreate the cues object, just reload with new file
        self.cues.setup_cues(self.show_confpath + self.show_conf.settings['cues']['href1'])
        self.cues.currentcueindex = 0
        self.cues.previouscueindex = 0
        self.displayShow()

    def displayShow(self):
        '''
        Update the state of the mixer display to reflect the newly loaded show
        '''
        #print(self.cues)
        qs = self.cues.cuelist.findall('actors')
        # for q in qs:
        #      print(q.attrib)
