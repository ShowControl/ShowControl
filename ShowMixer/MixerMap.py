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
        self.maproot = self.maptree.getroot()
        self.current_map_index = 0
        self.previous_map_index = 0
        maps = self.maproot.findall("./mixermap")
        self.map_list = []
        for key in range(len(maps)):
            print(key)
            map = self.maproot.find("./mixermap[@count='" + str(key) + "']")
            self.map_list.append(map.get('uuid'))
        print(self.map_list)
        self.mapcount = len(self.map_list)  # this is not the count= in the mixermap element,
                                            # but the count of mixermaps in the xml file
        maps = None

    def update_state(self,uuid):
        for count, uuid_string in enumerate(self.map_list):
            if uuid in uuid_string: # this uuid now the current, this uuid - becomes the previous
                self.current_map_index = count
                self.previous_map_index = count - 1
                if self.current_map_index > 0:
                    self.previous_map_index = self.current_map_index - 1
                else:
                    self.previous_map_index = 0
                break
        return

    def getuuidindex(self,uuid):
        for count, uuid_string in enumerate(self.map_list):
            if uuid in uuid_string: # this uuid now the current, this uuid - becomes the previous
                return count
        return None

    def getmixermapinputs(self, uuid):
        #maproot = self.maptree.getroot()
        mapelement = self.maproot.find("./mixermap[@uuid='" + uuid + "']")
        mixermapinputs = mapelement.findall("./input")
        return mixermapinputs

    def getmixermapbus(self, uuid):
        #maproot = self.maptree.getroot()
        mapelement = self.maproot.find("./mixermap[@uuid='" + uuid + "']")
        mixermapbuses = mapelement.findall("./bus")
        return mixermapbuses

    def getmixermapaux(self, uuid):
        #maproot = self.maptree.getroot()
        mapelement = self.maproot.find("./mixermap[@uuid='" + uuid + "']")
        mixermapauxes = mapelement.findall("./aux")
        return mixermapauxes

    def getmixermapcharcount(self, uuid):
        #maproot = self.maptree.getroot()
        try:
            mapelement = self.maproot.find("./mixermap[@uuid='" + uuid + "']")
            charcount = mapelement.get('charcount')
        except AttributeError as e:
            logging.error('{}, uuid {} not found!'.format(e, uuid))
            charcount = 0
        return int(charcount)

    def mapchange(self, uuid):
        """If the uuid exists:
        return True ==> map change needs to happen"""
        mapelement = self.maproot.find("./mixermap[@uuid='" + uuid + "']")
        if mapelement:
            return True
        else:
            return False

    def get_map_element_by_count(self, count=0):
        map = None
        try:
            map = self.maproot.find("./mixermap[@count='" + '{}'.format(count) + "']")
        except:
            print('mixermap count: {}'.format(count) + ' not found!')
        return map


if __name__ == "__main__":
    map = MixerCharMap('/home/mac/Shows/Fiddler/MixerMap.xml')
    print(map.getmixermapcharcount('cd914ed3-b286-4de6-a346-d101ca4f45f1'))
    map.update_state('f40e83e1-f69f-4fd7-bd22-5baae2d1fd07')
    map.update_state('18ab449b-1779-449c-8233-656d3fee69b2')
    pass