'''
Created on Nov 2, 2014

@author: mac
'''
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET


class MixerCharMap:
    '''
    classdocs
    '''


    def __init__(self, mapfilename):
        '''
        Constructor
        '''
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
