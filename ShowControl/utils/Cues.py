'''
Created on Nov 2, 2014
Cue object that maintains the current cue list
@author: mac
'''

import sys
from os import path
from PyQt5 import Qt, QtCore, QtGui, QtWidgets

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

cue_types = ['Stage','Mixer','Sound','SFX', 'Light']

cue_subelements = ['Cue_Number',  'Id',    'Act',   'Scene', 'Page',  'Title',       'Cue_Call',    'Cue_Type', 'Entrances',   'Exits',       'Levels',      'On_Stage',    'Note_1',      'Note_2',      'Note_3']
cue_edit_sizes =  ['60,20',       '60,20', '60,20', '60,20', '60,20', '16000000,20', '16000000,20', '60,20',    '16000000,20', '16000000,20', '16000000,20', '16000000,20', '16000000,20', '16000000,20', '16000000,20']
cue_subelements_tooltips = ['Cue number',
                            'Unique id for this cue',
                            'Enter act number for this cue',
                            'Enter scene number for this cue',
                            'Enter page number in script where this cue happens',
                            'Enter title for this cue',
                            'Enter cue call for this cue',
                            'Select one or more cue types for this cue',
                            'Specifies the channels to be unmuted for this cue',
                            'Specifies the channels to be muted for this cue',
                            'Specifies the fader level for all channels',
                            'Specifies who is on stage',
                            'Enter notes about this cue',
                            'Enter notes about this cue',
                            'Enter notes about this cue']
header = ['Cue Number', 'Act', 'Scene', 'Page', 'Id', 'Title', 'Cue Call', 'Cue Type', 'Note 1']


class CueList:
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
        self.cuetree = ET.ElementTree(file=cuefilename)
        self.cuelist = ET.parse(cuefilename)
        self.cuelist_root = self.cuelist.getroot()
        self.currentcueindex = 0
        self.previouscueindex = 0
        self.previewcueindex = 0
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)

    def get_cue_mute_state(self, cueindex):
        '''
                Constructor
                '''
        # print('{0:03}'.format(cueindex))
        mutestate = {}

        thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        # print(ET.dump(thiscue))
        try:
            ents = thiscue.find('Entrances')
            #             print(ET.dump(ents))
            #             print(ents.text)
            if ents != None:
                entlist = ents.text
                for entidx in entlist.split(","):
                    mutestate[entidx.strip()] = 1
            else:
                return mutestate
                # todo-mac this currently works since EVERY cue has an <Entrances> and <Exits> elements
        except:
            print('Entrances Index ' + '{0:03}'.format(cueindex) + ' not found!')
        try:
            exts = thiscue.find('Exits')
            #             print(ET.dump(exts))
            #             print(exts.text)
            if exts != None:
                extlist = exts.text
                for extidx in extlist.split(","):
                    mutestate[extidx.strip()] = 0
            return mutestate
            # todo-mac this currently works since EVERY cue has an <Entrances> and <Exits> elements
        except:
            print('Entrances Index ' + '{0:03}'.format(cueindex) + ' not found!')

    def get_cue_levels(self, cueindex):
        levelstate = {}
        thiscue = self.cuelist.find("./cue[@num='"+'{0:03}'.format(cueindex)+"']")
        #print(ET.dump(thiscue))
        try:
            levels = thiscue.find('Levels')
            if levels != None:
                levelslist = levels.text
                levelstate = dict(item.split(":") for item in levelslist.split(","))
                print(levelstate)
            return levelstate
        except:
            print('Levels not found!')

    def getcuetype(self, cueindex):
        thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        print(ET.dump(thiscue))
        try:
            cuetype = thiscue.find('CueType')
            if cuetype != None:
                type_list = cuetype.text.split(',')
                # return cuetype.text
                return type_list
            else:
                return ['']
        except:
            print('Cue type for index ' + '{0:03}'.format(cueindex) + ' not found!')

    def setcueelement(self, cueindex, levels):
        thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        print(ET.dump(thiscue))
        try:
            cuetype = thiscue.find('Levels')
            if cuetype != None:
                cuetype.text = levels
            else:
                cuetype = ET.SubElement(thiscue, 'Levels')
                cuetype.text = levels
            # thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
            # newcuetype = thiscue.find('Exits')
            # print(newcuetype.text)
        except:
            print('Cue type for index ' + '{0:03}'.format(cueindex) + ' not found!')
        self.cuelist.write('update.xml')

    def addnewcue(self, cue_dict={}):

        show = self.cuelist.getroot()
        newcue = ET.Element('cue',attrib={'num':'{0:03}'.format(self.cuecount)})
        for subele in cue_subelements:
            newele = ET.SubElement(newcue, subele)
            if subele in cue_dict:
                newele.text = cue_dict[subele]
            else:
                newele.text = '{0}'.format(self.cuecount)
        show.append(newcue)

        ET.dump(show)
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)
        # self.cuelist.write('addelementtest.xml')

    def insertcue(self, cueindex, cue_data=[]):
        # cueidx is the index that we're inserting above, so
        # create an empty place by incrementing the cue num for this and each subsequent cue
        for anidx in range(cueindex, self.cuecount):
            cuenum = '{0:03}'.format(anidx)
            thiscue = self.cuelist.find("cue[@num='"+cuenum+"']")
            thisidx = thiscue.get('num')
            thiscue.set('num', '{0:03}'.format(int(thisidx) + 1))
            print(thiscue.get('num'))
        # now we have an empty place
        # create the ne cue
        show = self.cuelist.getroot()
        newcue = ET.Element('cue',attrib={'num':'{0:03}'.format(cueindex)})
        for i in range(cue_subelements.__len__()):
            newele = ET.SubElement(newcue, cue_subelements[i])
            newele.text = cue_data[i]
        show.insert(cueindex, newcue)

        # ET.dump(show)
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)

    # def insertcue(self, cueindex, cue_dict={}):
    #     # cueidx is the index that we're inserting above, so
    #     # create an empty place by incrementing the cue num for this and each subsequent cue
    #     for anidx in range(cueindex, self.cuecount):
    #         cuenum = '{0:03}'.format(anidx)
    #         thiscue = self.cuelist.find("cue[@num='"+cuenum+"']")
    #         thisidx = thiscue.get('num')
    #         thiscue.set('num', '{0:03}'.format(int(thisidx) + 1))
    #         print(thiscue.get('num'))
    #     # now we have an empty place
    #     # create the ne cue
    #     show = self.cuelist.getroot()
    #     newcue = ET.Element('cue',attrib={'num':'{0:03}'.format(cueindex)})
    #     for subele in cue_subelements:
    #         newele = ET.SubElement(newcue, subele)
    #         if subele in cue_dict:
    #             newele.text = cue_dict[subele]
    #         else:
    #             newele.text = '{0}'.format(self.cuecount)
    #     show.insert(cueindex, newcue)
    #
    #     # ET.dump(show)
    #     cues = self.cuelist.findall('cue')
    #     self.cuecount = len(cues)

    def getcuelist(self, cueindex):
        cuenum = '{0:03}'.format(cueindex)
        thiscue = self.cuelist.find("cue[@num='"+cuenum+"']")
        cuecontents_list = []
        for i in range(cue_subelements.__len__()):
            cuecontents_list.append(thiscue.find(cue_subelements[i].replace('_','')).text)
        return cuecontents_list

    def updatecue(self, cueindex, newcuelist):
        cuenum = '{0:03}'.format(cueindex)
        cuetomod = self.cuelist.find("cue[@num='"+cuenum+"']")

        for i in range(cue_subelements.__len__()):
            cuetomod.find(cue_subelements[i].replace('_','')).text = newcuelist[i]

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
            self.cuelist.write(oldroot + '-{0}'.format(rev) + extension)
        else:
            self.cuelist.write(filename)

if __name__ == "__main__":
    app = QtWidgets.QApplication([''])
    cues = CueList('/home/mac/Shows/Pauline/ThreeCue.xml')
    # ET.dump(cues.cuelist)
    # cues.addnewcue({'Scene':'1','Title':'A new Cue'})
    # ET.dump(cues.cuelist)
    # cues.savecuelist()
    cues.savecuelist(True, '/home/mac/Shows/Pauline/ThreeCue.xml')
    cues.insertcue(2, {'Scene':'1','Title':'A new inserted Cue'})
    cues.savecuelist(False, '/home/mac/Shows/Pauline/Update.xml')
    # a = ET.Element('cue',attrib={'num':'000'})
    # c = ET.SubElement(a, 'child1')
    # c.text = "some text"
    # d = ET.SubElement(a, 'child2')
    # b = ET.Element('elem_b')
    # root = ET.Element('show')
    # root.extend((a, b, a))
    # tree = ET.ElementTree(root)
    # ET.dump(tree)