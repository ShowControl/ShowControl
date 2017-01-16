'''
Created on Nov 2, 2014
Cue object that maintains the current cue list
@author: mac
'''
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET


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
        self.cuelist = ET.parse(cuefilename)
        # self.mutestate = {}
        # for x in range(1, chancount+1):
        #     self.mutestate['ch' + '{0}'.format(x)] = 0
        # self.levelstate = {}
        self.currentcueindex = 0
        self.previewcueindex = 0
        cues = self.cuelist.findall('cue')
        self.cuecount = len(cues)

    def get_cue_mute_state(self, cueindex):
        '''
                Constructor
                '''
        # print('{0:03}'.format(cueindex))
        mutestate = {}
        #for x in range(1, chancount+1):
        #    self.mutestate['ch' + '{0}'.format(x)] = 0

        thiscue = self.cuelist.find("./cue[@num='" + '{0:03}'.format(cueindex) + "']")
        print(ET.dump(thiscue))
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


#     def setcurrentcuestate(self, cueindex):
#         '''
#         Constructor
#         '''
#         #print('{0:03}'.format(cueindex))
#         thiscue = self.cuelist.find("./cue[@num='"+'{0:03}'.format(cueindex)+"']")
#         print(ET.dump(thiscue))
#         try:
#             ents = thiscue.find('Entrances')
# #             print(ET.dump(ents))
# #             print(ents.text)
#             if ents != None:
#                 entlist = ents.text
#                 for entidx in entlist.split(","):
#                     self.mutestate[entidx.strip()] = 1
#         except:
#             print('Entrances Index ' + '{0:03}'.format(cueindex) + ' not found!')
#         try:
#             exts = thiscue.find('Exits')
#             if exts != None:
#                 extlist = exts.text
#                 for extidx in extlist.split(","):
#                     self.mutestate[extidx.strip()] = 0
#         except:
#             print('Exits Index ' + '{0:03}'.format(cueindex) + ' not found!')
#         #print(self.mutestate)
#         try:
#             levels = thiscue.find('Levels')
#             if levels != None:
#                 levelslist = levels.text
#                 self.levelstate = dict(item.split(":") for item in levelslist.split(","))
#                 print(self.levelstate)
#         except:
#             print('Levels not found!')

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

    def setpreviewcuestate(self, cueindex):
        '''
        Constructor
        '''
        
        