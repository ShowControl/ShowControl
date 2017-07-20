'''
Created on Nov 2, 2014

@author: mac
'''
import logging
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

#from SCLog import SCLog


class MixerCharMap():
    '''
    classdocs
    '''


    def __init__(self, mapfilename):
        '''
        Constructor
        '''
        logging.info('In MixerCharMap.')
        self.maptree = ET.parse(mapfilename)

    def getmixermapinputs(self, uuid):
        maproot = self.maptree.getroot()
        mapelement = maproot.find("./mixermap[@uuid='" + uuid + "']")
        mixermapinputs = mapelement.findall("./input")
        return mixermapinputs

    def getmixermapcharcount(self, uuid):
        maproot = self.maptree.getroot()
        mapelement = maproot.find("./mixermap[@uuid='" + uuid + "']")
        charcount = mapelement.get('charcount')
        return int(charcount)

if __name__ == "__main__":
    map = MixerCharMap('/home/mac/Shows/Fiddler/MixerMap.xml')
    map.getmixermapcharcount('cd914ed3-b286-4de6-a346-d101ca4f45f1')
    pass