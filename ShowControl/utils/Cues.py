'''
Created on Nov 2, 2014
Cue object that maintains the current cue list
@author: mac
'''

import sys
from os import path
import shutil
import uuid
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import logging
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

cue_types = ['Stage', 'Mixer','Sound','SFX', 'Light']

cue_subelements = [ 'Id',
                    'Act',
                    'Scene',
                    'Page',
                    'Title',
                    'Cue_Call',
                    'Cue_Type',
                    'Entrances',
                    'Exits',
                    'Mutes',
                    'Levels',
                    'On_Stage',
                    'Note_1',
                    'Note_2',
                    'Note_3',
                    'map']

cue_fields = ['Cue_Number',     # Cue_Number
              'Id',             # Id
              'Act',            # Act
              'Scene',          # Scene
              'Page',           # Page
              'Title',          # Title
              'Cue_Call',       # Cue_Call
              'Cue_Type',       # Cue_Type
              'Entrances',      # Entrances
              'Exits',          # Exits
              'Mutes',          # Mutes
              'Levels',         # Levels
              'On_Stage',       # On_Sta
              'Note_1',         # Note_1
              'Note_2',         # Note_2
              'Note_3',         # Note_3
              'map']            # mute map number

cue_edit_sizes =  [	'60,20',		    # Cue_Number
                    '60,20',            # Id
                    '60,20',            # Act
                    '60,20',            # Scene
                    '60,20',            # Page
                    '16000000,20',      # Title
                    '16000000,20',      # Cue_Call
                    '60,20',            # Cue_Type
                    '16000000,20',      # Mutes
                    '16000000,20',      # Entrances
                    '16000000,20',      # Exits
                    '16000000,20',      # Levels
                    '16000000,20',      # On_Stage
                    '16000000,20',      # Note_1
                    '16000000,20',      # Note_2
                    '16000000,20',      # Note_3
                    '60,20']            # mute map number

cue_subelements_tooltips = ['Cue number',											# Cue_Number
                            'Unique id for this cue',								# Id
                            'Enter act number for this cue',						# Act
                            'Enter scene number for this cue',						# Scene
                            'Enter page number in script where this cue happens',   # Page
                            'Enter title for this cue',								# Title
                            'Enter cue call for this cue',							# Cue_Call
                            'Select one or more cue types for this cue',			# Cue_Type
                            'Specifies the characters who enter for this cue',      # Entrances
                            'Specifies the characters who exit for this cue',		# Exits
                            'Specifies the mute state for all channels',			# Mutes
                            'Specifies the fader level for all channels',			# Levels
                            'Specifies characters who are on stage',				# On_Stage
                            'Enter notes about this cue',							# Note_1
                            'Enter notes about this cue',							# Note_2
                            'Enter notes about this cue',							# Note_3
                            'Enter mute map number']							    # mute map number

header = [  'Cue Number',
            'Act',
            'Scene',
            'Page',
            'Id',
            'Title',
            'Cue Call',
            'Cue Type',
            'Note 1']




class CueList():
    '''
    CueList object contains information defining the cues for a show
    '''
    def __init__(self, cuefilename):
        '''
        Constructor
        cuelist is a tree object with all cues for the show
        mutestate is a dictionary that maintains the current mute state
                based on what entrances and exits appear in the cuelist
        levelstate is a dictionary that maintains the current level of each slider
        currentindex is an integer that indicates the current cue
        previewcueindex is an integer that indicates the cue being previewed , if a preview is active 
        '''
        logging.info('In CueList init')

        self.setup_cues(cuefilename)
        # self.cuetree = ET.ElementTree(file=cuefilename)
        # self.cuelist = ET.parse(cuefilename)
        # self.cuelist_root = self.cuelist.getroot()
        # self.currentcueindex = 0
        # self.previouscueindex = 0
        # self.previewcueindex = 0
        # cues = self.cuelist.findall('cue')
        # self.cuecount = len(cues)

    def setup_cues(self, cuefilename):
        logging.info('In CueList setup_cues')
        self.cuetree = ET.ElementTree(file=cuefilename)
        self.cuelist = ET.parse(cuefilename)
        self.cuelist_root = self.cuelist.getroot()
        self.currentcueindex = 0
        self.previouscueindex = 0
        self.previewcueindex = 0
        self.selectedcueindex = None
        #self.cues_element = self.cuelist_root.find('cues')
        #self.cuelist.find(".cues/cue[@num='001']")
        cues = self.cuelist.findall('.cues/cue')
        self.cuecount = len(cues)

    def get_cue_mute_state_by_index(self, cueindex):
        """Get the mutes element of the cue specified by cueindex.
        Compare it to the next (direction==1)/previous(direction==-1) Mixer cues mute state and
        return a list of channels to mute or unmute.
        If cueindex is 0, then just return the entire mute state, as this is
        the initial cue."""
        mutestate = {}
        if cueindex < 0:
            logging.info('cueindex received: {}, setting to 0.'.format(cueindex))
            cueindex = 0
        elif cueindex >= self.cuecount:
            logging.info('cueindex received: {}, setting to last cue.'.format(cueindex))
            cueindex = self.cuecount - 1
        #thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        try:
            dirty_current_mutes = thiscue.find('Mutes').text
            current_mutes = dirty_current_mutes.strip()
            current_mutes_list = current_mutes.split(',')
        except AttributeError:
            current_mutes_list = None
        for index in range(current_mutes_list.__len__()):
            key, value = current_mutes_list[index].split(':')
            mutestate[key] = int(value)
        return mutestate

    def get_cue_mute_state_delta(self, cueindex, direction=1):
        """Get the mutes element of the cue specified by cueindex.
        Compare it to the next (direction==1)/previous(direction==-1) Mixer cues mute state and
        return a list of channels to mute or unmute.
        If cueindex is 0, then just return the entire mute state, as this is
        the initial cue."""
        mutestate = {}
        #thiscue = self.cuelist.find("./Cue[@num='" + '{0:03}'.format(cueindex) + "']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        try:
            dirty_current_mutes = thiscue.find('Mutes').text
            current_mutes = dirty_current_mutes.strip()
            current_mutes_list = current_mutes.split(',')
        except AttributeError:
            current_mutes_list = None
        if cueindex != 0:
            prevcue_index = cueindex
            while True:
                prevcue_index -= 1
                #prevcue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(prevcue_index) + "']")
                prevcue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(prevcue_index) + "']")
                dirty_prevcue_types = prevcue.find('CueType').text
                prevcue_types = dirty_prevcue_types.strip()
                prevcue_types_list = prevcue_types.split(',')
                if 'Mixer' in prevcue_types_list:
                    break

            dirty_prevmutes = prevcue.find('Mutes').text
            prevmutes = dirty_prevmutes.strip()
            prevmutes_list = prevmutes.split(',')
            for index in range(current_mutes_list.__len__()):
                if current_mutes_list[index] != prevmutes_list[index]:
                    key, value = current_mutes_list[index].split(':')
                    mutestate[key] = int(value)
        else:  # index zero is a special case, since there was no previous cue
            for index in range(current_mutes_list.__len__()):
                    key, value = current_mutes_list[index].split(':')
                    mutestate[key] = int(value)
        return mutestate

    def get_cue_levels(self, cueindex):
        """Get the Level element of the cue specified by cueindex
        return a dictionary of all channel levels"""
        levelstate = {}  # todo-mac maybe should return only deltas as is done in get_cue_mute_state???
        #thiscue = self.cuelist.find("./cue[@num='"+'{0:03}'.format(cueindex)+"']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        #print(ET.dump(thiscue))
        try:
            levels = thiscue.find('Levels')
            if levels != None:
                levelslist = levels.text
                levelstate = dict(item.split(":") for item in levelslist.split(","))
                #print(levelstate)
            return levelstate
        except:
            print('Levels not found!')
            logging.error('CueList.get_cue_levels: Levels element not found')

    def getcuetype(self, cueindex):
        #thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        try:
            cuetype = thiscue.find('CueType')
            if cuetype != None:
                dirty_type_list = cuetype.text.split(',')
                type_list = [s.strip() for s in dirty_type_list]
                # return cuetype.text
                return type_list
            else:
                return ['']
        except:
            print('Cue type for index ' + '{0:03}'.format(cueindex) + ' not found!')

    def get_cue_element_by_name(self, cueindex, element_name):
        #thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        try:
            element = thiscue.find(element_name)
            if element != None:
                return element
            else:
                return None
        except:
            print('Cue element {} for index ' + '{:03}'.format(element_name,cueindex) + ' not found!')

    def setcueelement(self, cueindex, element_text, element_name):
        # find the cue specified by cueindex
        #thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        thiscue = self.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(cueindex) + "']")
        try:
            cuetype = thiscue.find(element_name)
            if cuetype != None:
                cuetype.text = element_text
            else:
                cuetype = ET.SubElement(thiscue, 'Levels')
                cuetype.text = element_text
        except:
            print('Cue element {0} for index {1:03} not found!'.format(element_name, cueindex))
        self.cuelist.write('update.xml')

    def addnewcue(self, cue_data=[]):
        cues_element = self.cuelist.find(".cues")
        cues = cues_element.findall(".cue")
        cue_count = len(cues)
        newcue = ET.Element('cue',attrib={'uuid':'{0}'.format(uuid.uuid4()), 'num':'{0:03}'.format(cue_count)})

        #newcue = ET.Element('cue',attrib={'uuid':'{0}'.format(uuid.uuid4()), 'num':'{0:03}'.format(self.cuecount)})
        for i in range(cue_subelements.__len__()):
            newele = ET.SubElement(newcue, cue_subelements[i].replace('_',''))
            newele.text = cue_data[i]
        cues_element.append(newcue)

        # ET.dump(cues_element)
        cues = self.cuelist.findall('.cues/cue')
        self.cuecount = len(cues)
        # self.cuelist.write('addelementtest.xml')

        return [newcue.get('uuid'), newcue.get('num')]

    def insertcue(self, cueindex, cue_data=[]):
        # cueidx is the index that we're inserting above, so
        # create an empty place by incrementing the cue num for this and each subsequent cue
        for anidx in reversed(range(cueindex, self.cuecount)):
            cuenum = '{0:03}'.format(anidx)
            thiscue = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
            thisidx = thiscue.get('num')
            thiscue.set('num', '{0:03}'.format(int(thisidx) + 1))
            print(thiscue.get('num'))
        # now we have an empty place
        # create the new cue
        # show = self.cuelist.getroot()
        # ET.dump(show)
        cues_element = self.cuelist.find(".cues")
        newcue = ET.Element('cue',attrib={'uuid':'{0}'.format(uuid.uuid4()), 'num':'{0:03}'.format(cueindex)})
        for i in range(cue_subelements.__len__()):
            newele = ET.SubElement(newcue, cue_subelements[i].replace('_',''))
            newele.text = cue_data[i]
        cues_element.insert(cueindex + 1, newcue)
        # show.insert(cueindex, newcue)
        # ET.dump(show)
        cues = self.cuelist.findall('.cues/cue')
        self.cuecount = len(cues)
        return

    def deletecue(self, cueindex):
        '''Delete the cue specified by index
        and re-index the list'''
        # find the cue
        cuenum = '{0:03}'.format(cueindex)
        thiscue = self.cuelist.find(".cues/cue[@num='" + cuenum + "']")
        # delete the cue from the tree
        self.cuelist_root.remove(thiscue)
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)
        print('cuecount: {}'.format(self.cuecount))
        for anidx in range(cueindex + 1, self.cuecount + 1):
            cuenum = '{0:03}'.format(anidx)
            thiscue = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
            thisidx = thiscue.get('num')
            thiscue.set('num', '{0:03}'.format(int(anidx) - 1))
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)

    def delete_cue_by_uuid(self, cueuuid):
        '''Delete the cue specified by index
        and re-index the list'''
        # find the cue
        cues_element = self.cuelist.find(".cues")
        thiscue = cues_element.find(".cue[@uuid='" + cueuuid + "']")
        cueindex = int(thiscue.get('num'))
        # delete the cue from the tree
        cues_element.remove(thiscue)
        cues = cues_element.findall('cue')
        self.cuecount = len(cues)
        print('cuecount: {}'.format(self.cuecount))
        for anidx in range(cueindex + 1, self.cuecount + 1):
            cuenum = '{0:03}'.format(anidx)
            thiscue = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
            thisidx = thiscue.get('num')
            thiscue.set('num', '{0:03}'.format(int(anidx) - 1))
        cues = self.cuelist.findall('.cues/cue')
        self.cuecount = len(cues)

    def getcuelist(self, cueindex):
        cuenum = '{0:03}'.format(cueindex)
        thiscue = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
        cuecontents_list = []  # [thiscue.attrib['num']]
        for i in range(cue_subelements.__len__()):
            cuecontents_list.append(thiscue.find(cue_subelements[i].replace('_','')).text)
        return cuecontents_list

    def getcuelistbyuuid(self, cue_uuid):
        thiscue = self.cuelist.find(".cues/cue[@uuid='"+cue_uuid+"']")
        cuecontents_list = []  # [thiscue.attrib['num']]
        for i in range(cue_subelements.__len__()):
            cuecontents_list.append(thiscue.find(cue_subelements[i].replace('_','')).text)
        return cuecontents_list

    def getcurrentcueuuid(self, cueindex):
        cuenum = '{0:03}'.format(cueindex)
        thiscue = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
        currentuuid = thiscue.get('uuid')
        return currentuuid

    def getcueindexbyuuid(self, uuid):
        #cuenum = '{0:03}'.format(cueindex)
        thiscue = self.cuelist.find(".cues/cue[@uuid='"+ uuid +"']")
        cueindex = thiscue.get('num')
        return cueindex

    def updatecue(self, cueindex, newcuelist):
        cuenum = '{0:03}'.format(cueindex)
        cuetomod = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")

        for i in range(cue_subelements.__len__()):
            cuetomod.find(cue_subelements[i].replace('_','')).text = newcuelist[i]

    def updatecueelement(self, cueindex, elementname, newelementvalue):
        cuenum = '{0:03}'.format(cueindex)
        cuetomod = self.cuelist.find(".cues/cue[@num='"+cuenum+"']")
        cuetomod.find(elementname).text = newelementvalue

    def savecuelist(self, revision=True, filename=''):
        """save the current state of the cuelist.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the cuelist,
        typically call with revision=True before an add or insert
        If revision=False, save the current state of the cuelist
        in the file specified by filename"""
        if filename == '':
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('The cues not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        if revision:
            oldroot, extension = path.splitext(filename)
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            # commented this out to make chage below
            # self.cuelist.write(oldroot + '-{0}'.format(rev) + extension)
            # modified to copy existing to revision
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)
            #self.cuelist.write(oldroot + '-{0}'.format(rev) + extension)
        # else:
            # self.cuelist.write(filename)
        self.cuelist.write(filename)

class CuesXML():
    """
    Builder for cues xml file
    """
    def __init__(self):
        """"""
        logging.info('In CuesXML init')

    def toXMLdoc(self):
        showcontrol = ET.Element('showcontrol')
        cues = ET.SubElement(showcontrol, 'cues')
        ET.SubElement(cues, 'version').text = '1.0'
        cue = ET.SubElement(cues, 'cue', attrib={'uuid':'{0}'.format(uuid.uuid4()), 'num':'{0:03}'.format(0)})
        ET.SubElement(cue, 'Id').text = '0'
        ET.SubElement(cue, 'Act').text = '0'
        ET.SubElement(cue, 'Scene').text = 'Pre Show'
        ET.SubElement(cue, 'Page').text = '0'
        ET.SubElement(cue, 'Title').text = 'Initial State'
        ET.SubElement(cue, 'CueCall').text = 'Program Start'
        ET.SubElement(cue, 'CueType').text = 'Stage,Mixer,Sound'
        ET.SubElement(cue, 'Mutes').text = ''
        ET.SubElement(cue, 'Entrances').text = ''
        ET.SubElement(cue, 'Exits').text = ''
        ET.SubElement(cue, 'Levels').text = ''
        ET.SubElement(cue, 'OnStage').text = ''
        ET.SubElement(cue, 'Note1').text = ''
        ET.SubElement(cue, 'Note2').text = ''
        ET.SubElement(cue, 'Note3').text = ''
        ET.SubElement(cue, 'map').text = '0'
        return showcontrol

    def write(self, newxml,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newxml)
        if filename == '':
            logging.debug('Configuration not saved, no filename provided!')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Configuration not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        if revision:
            oldroot, extension = path.splitext(filename)
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        newdoctree.write(filename, xml_declaration=True)
        logging.debug('Configuration written to: ' + filename)

        return


if __name__ == "__main__":
    #/home/mac/SharedData/PycharmProjs/ShowControl/ShowControl/utils/
    logging.basicConfig(level=logging.INFO,
                        filename='CueList.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')

    app = QtWidgets.QApplication([''])
    cues = CueList('/home/mac/Shows/Fiddler/Fiddler_cuesx.xml')
    cues.getcuetype(0)
    ET.dump(cues.cuelist)
    allcues = cues.cuelist.findall(".cues/cue")
    showcontrol = ET.Element('showcontrol')
    sortedcues = ET.SubElement(showcontrol, 'cues')
    ET.SubElement(sortedcues, 'version').text = '1.0'
    for count, cue in enumerate(allcues):
        cuenum = cue.get("num")
        print('count: {}, num: {} {}'.format(count, cuenum, count == int(cuenum)))
        if count == int(cuenum):
            # save it in new doc
            sortedcues.append(cue)
        else: # find the cue element for this count and save it in the new doc
            nextcue = cues.cuelist.find(".cues/cue[@num='" + '{0:03}'.format(count) + "']")
            sortedcues.append(nextcue)
    ET.dump(showcontrol)
    cuesxml = CuesXML()
    cuesxml.write(showcontrol, False, '/home/mac/Shows/Fiddler/sorted_Fiddler_cuesx.xml')
    # somecue = cues.cuelist.find(".cues/cue[@num='000']")
    # cue_elements = cues.cuelist.findall("./cue")
    # for index, cue in enumerate(cue_elements):
    #     Levels_element = cue.find('./Levels')
    #     Level_val = cues.get_cue_levels(index)
    #     pass
    # somecuelist = cues.getcuelist(149)
    # from_element = cues.get_cue_element_by_name(4, 'Mutes').text.split(',')
    # to_element = cues.get_cue_element_by_name(56,'Mutes').text.split(',')
    # delta_mutes = [mute for mute in to_element if mute not in from_element]
    # if mixermap_element:
    #     input_maps = mixermap_element.findall('input')
    #     for input_map in input_maps:
    #         mixerid = input_map.get('mixerid')
    #         mixerchan = input_map.get('chan')
    #         actor = input_map.get('actor')
    #         char = input_map.get('char')
    #         print('Mixer id: {}, chan: {}, actor: {}, char: {}'.format(mixerid, mixerchan, actor, char))
    pass
    # cues.addnewcue({'Scene':'1','Title':'A new Cue'})
    # ET.dump(cues.cuelist)
    # cues.savecuelist()
    #cues.savecuelist(True, '/home/mac/Shows/Pauline/ThreeCue.xml')
    #cues.insertcue(2, {'Scene':'1','Title':'A new inserted cue'})
    #cues.savecuelist(False, '/home/mac/Shows/Pauline/Update.xml')
    # a = ET.Element('cue',attrib={'num':'000'})
    # c = ET.SubElement(a, 'child1')
    # c.text = "some text"
    # d = ET.SubElement(a, 'child2')
    # b = ET.Element('elem_b')
    # root = ET.Element('show')
    # root.extend((a, b, a))
    # tree = ET.ElementTree(root)
    # ET.dump(tree)