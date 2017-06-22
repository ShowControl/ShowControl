#!/usr/bin/env python3

from configparser import ConfigParser
from shutil import copyfile
import os

HOME = os.path.expanduser("~")

DEFAULT_CFG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/default.cfg'))

CFG_DIR = HOME + '/.showcontrol'
CFG_PATH = CFG_DIR + '/config.cfg'

def checkUserConf():
    """First run of any ShowControl app creates ~/.showcontrol folder
    and adds default ~/.showcontrol/config.cfg
    If this is a new version it copies config.cfg to config.cfg.old"""
    newcfg = True
    if(not os.path.exists(CFG_PATH)):
        if(not os.path.exists(CFG_DIR)):
            os.makedirs(CFG_DIR)
    else:
        default = ConfigParser()
        default.read(DEFAULT_CFG_PATH)
        current = ConfigParser()
        current.read(CFG_PATH)
        if('Version' in current):
            newcfg = current['Version']['Number'] != default['Version']['Number']
        if(newcfg):
            copyfile(CFG_PATH, CFG_PATH + '.old')
            print('Old configuration file backup -> ' + CFG_PATH + '.old')

    if(newcfg):
        copyfile(DEFAULT_CFG_PATH, CFG_PATH)
        print('Create configuration file -> ' + CFG_PATH)
    else:
        print("Configuration is up to date")

checkUserConf()

config = ConfigParser()
config.read(CFG_PATH)

def toDict():
    """Create the config dictionary from the keysin config.cfg"""
    conf_dict = {}
    for key in config.keys():
        conf_dict[key] = {}
        for skey in config[key].keys():
            conf_dict[key][skey] = config[key][skey]
    return conf_dict

def updateFromDict(conf):
    """Update the config info from modified config dictionary"""
    for key in conf.keys():
        for skey in conf[key].keys():
            config[key][skey] = conf[key][skey]

def write():
    """Save the config dictionary to config.cfg"""
    with open(CFG_PATH, 'w') as cfgfile:
        config.write(cfgfile)

if __name__ == "__main__":
    testdict = toDict()
    pass