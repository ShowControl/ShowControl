'''
Created on Nov 2, 2014
Cue object that maintains the current cue list
@author: mac
'''

import sys
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

cue_subelements = ['Move', 'ID', 'Act', 'Scene', 'Page', 'Title', 'Cue', 'CueType', 'Entrances', 'Exits', 'Levels', 'On_Stage', 'Note_1', 'Note_2', 'Note_3']

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
                return cuetype.text
            else:
                return ''
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


        # newmove = ET.SubElement(newcue, 'Move')
        # newmove.text = '{0}'.format(self.cuecount)
        # newid = ET.SubElement(newcue, 'Move')
        # newid.text = '{0}'.format(self.cuecount)
        # # ET.SubElement( newcue, newmove)
        # ET.dump(newcue)
        # # show = self.cuetree.getroot()
        # # print('show length: {0}'.format(show.__len__()))
        # show1 = self.cuelist.getroot()
        # print('show length: {0}'.format(show1.__len__()))
        # try:
        #     # show.append(newcue)
        #     # print('show length: {0}'.format(show.__len__()))
        #     show1.append(newcue)
        #     print('show length: {0}'.format(show1.__len__()))
        # except:
        #     print('Error')
        ET.dump(show)
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)
        self.cuelist.write('addelementtest.xml')

    # def setpreviewcuestate(self, cueindex):
    #     '''
    #     Constructor
    #     '''
        
if __name__ == "__main__":
    cues = CueList('/home/mac/Shows/Pauline/OneCue.xml')
    ET.dump(cues.cuelist)
    cues.addnewcue({'Scene':'1','Title':'A new Cue'})
    ET.dump(cues.cuelist)
    # a = ET.Element('cue',attrib={'num':'000'})
    # c = ET.SubElement(a, 'child1')
    # c.text = "some text"
    # d = ET.SubElement(a, 'child2')
    # b = ET.Element('elem_b')
    # root = ET.Element('show')
    # root.extend((a, b, a))
    # tree = ET.ElementTree(root)
    # ET.dump(tree)