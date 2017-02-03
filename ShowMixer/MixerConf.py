#!/usr/bin/env python3
'''
Created on Oct 19, 2014
MixerConf mixer configuration object

@author: mac
'''
try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

from MixerControl import ControlFactory, supported_protocols, supported_controls


class InputControl:
    def __init__(self, level, scribble_text, fadercmd, mutecmd, scribblecmd):
        # self.level = level
        # self.scribble_text = scribble_text
        self.fadercmd = fadercmd
        self.mutecmd = mutecmd
        self.scribblecmd = scribblecmd

class OutputControl:
    def __init__(self, level, scribble_text):
        self.level = level
        self.scribble_text = scribble_text

# class Strip():
#     def __init__(self, controls, protocol):
#         """controls - list of controls on this strip"""
#         for control in controls:
#             self.control = ControlFactory.create_control(control, protocol)

class MixerConf:
    '''
    Created on Oct 19, 2014
    MixerConf object returns the configuration of the mixer specified
    by the mixername and mixermodel arguments.
    
    It searches the file specified in mixerconf_file for the mixer specified
    by the mixername and mixermodel arguments.  
    
    MixerConf structure:
    MixerConf
        protocol (string)
        inputsliders {dictionary} containing cnt keys, where each key:
            key : InputControl (object)
        outputsliders {dictionary} containing cnt keys, where each key:
            key : OutputControl (object)
    @author: mac
    '''
    def __init__(self, mixerconf_file, mixername, mixermodel, mixeraddress):
        #
        # dictionary of input sliders, index format: [Chnn]
        # each entry is a InputControl object
        self.inputsliders = {}

        # dictionary of output sliders, index format: [Chnn]
        # each entry is a OutputControl object
        self.outputsliders = {}

        # dictionary of mutestyle for the mixer
        # mutestyle referes to how the mixer indicates the channel is muted
        # for example, the Yamaha 01V indicates a channel is un-muted with an illuminated light
        # other mixer indicate a muted channel with an illuminated light
        # mutestyle['mutestyle'] will be the string 'illuminated' or 'non-illumnated'
        #                        as read from <mixerdefs>.xml for each particular mixer
        # for mutestyle['illuminated'], mutestyle['mute'] will be 0, mutestyle['unmute'] will be 1
        # for mutestyle['non-illuminated'], mutestyle['mute'] will be 1, mutestyle['unmute'] will be 0
        self.mutestyle = {}

        '''mxrstrips is a dictionary of controls for a type of strip.
        mxrstrips will have a key for each strip type (input, output, auuxin, etc.)
        each strip type wil have a dictionary of it's associated control objects.
        Controls objects are based on the protocol of the mixer. (See MixerControl.py)'''
        self.mxrstrips = {}

        '''mxrconsole is a list of all the strips on the mixer.
        This is used for the layout on the GUI and to work on a sigle strip
        or interate through all strips on the mixer.
        Each element of the list will have a dictionary with the strip name and strip type'''
        self.mxrconsole = []

        self.fadercontrol = None
        self.scribblecontrol = None
        self.mutecontrol = None
        self.controls = {}

        mixerdefs = ET.parse(mixerconf_file)
        mixers = mixerdefs.getroot()
        #print('mixers: ' + str(mixers))
        for mixer in mixers:
            print(mixer.attrib)
            mxattribs = mixer.attrib
            if 'model' in mxattribs.keys():
                if mxattribs['model'] == mixermodel and mxattribs['mfr'] == mixername:
                    #print('found')
                    break
        self.protocol = mixer.find('protocol').text
        #print('protocol: ' + self.protocol)
        self.IP = ''
        self.PORT = 0
        self.MIDICHAN = 0
        if self.protocol == 'osc':
            self.IP, port = mixeraddress.split(',')
            self.PORT = int(port)
        elif self.protocol == 'midi':
            self.MIDICHAN = int(mixeraddress)
        self.mutestyle['mutestyle'] = mixer.find('mutestyle').text
        if self.mutestyle['mutestyle'] == 'illuminated':
            self.mutestyle['mute'] = 0
            self.mutestyle['unmute'] = 1
        else:
            self.mutestyle['mute'] = 1
            self.mutestyle['unmute'] = 0
        strips = mixer.findall('strip')
        stripcontrols = []
        for strip in strips:
            stripattribs = strip.attrib
            #print(stripattribs)
            if stripattribs['type'] == 'input':
                self.mxrstrips['input'] ={}
                try:
                    fader = strip.find('fader')
                    faderattribs = fader.attrib
                    stripcontrols.append('fader')
                    fadercontrol = ControlFactory.create_control('fader', self.protocol)
                    commandstring = faderattribs['cmd']
                    if self.protocol == 'midi':
                        controlchange, changenumbase, val = faderattribs['cmd'].split(',')
                        commandstring = '{0},{1},{2}'.\
                                            format(controlchange.replace('#', '{:1x}'.format(self.MIDICHAN)),\
                                            changenumbase, val)
                    fadercontrol.fill(faderattribs['cmdtyp'], commandstring, faderattribs['range'])
                    self.mxrstrips[stripattribs['type']].update({'fader':fadercontrol})
                except:
                    pass
                try:
                    mute = strip.find('mute')
                    muteattribs = mute.attrib
                    stripcontrols.append('mute')
                    mutecontrol = ControlFactory.create_control('mute', self.protocol)
                    mutecontrol.fill(muteattribs['cmdtyp'], muteattribs['cmd'], None)
                    self.mxrstrips[stripattribs['type']].update({'mute' : mutecontrol})
                except:
                    pass
                try:
                    scribble = strip.find('scribble')
                    scribbleattribs = scribble.attrib
                    stripcontrols.append('scribble')
                    scribblecontrol = ControlFactory.create_control('scribble', self.protocol)
                    scribblecontrol.fill(scribbleattribs['cmdtyp'], scribbleattribs['cmd'], '')
                    self.mxrstrips[stripattribs['type']].update({'scribble' : scribblecontrol})
                except:
                    pass
                print(stripattribs['cnt'])
                self.input_count = int(stripattribs['cnt'])
                #print(self.input_count)
                for x in  range(1, self.input_count + 1):
                    sldr = InputControl(x,'In' + '{0:02}'.format(x), faderattribs['cmd'], muteattribs['cmd'], scribbleattribs['cmd'])
                    self.inputsliders['Ch' + '{0:02}'.format(x)] = sldr
                    self.mxrconsole.append(
                        {'name': stripattribs['name'] + '{0:02}'.format(x), 'type': stripattribs['type'],
                         'channum': x})
            elif stripattribs['type'] == 'output':
                self.mxrstrips['output'] ={}
                #print(stripattribs['cnt'])
                self.output_count = int(stripattribs['cnt'])
                #print(self.output_count)
                for x in  range(1, self.output_count + 1):
                    sldr = OutputControl(x,'Out' + '{0:02}'.format(x))
                    self.outputsliders['Ch' + '{0:02}'.format(x)] = sldr
            elif stripattribs['type'] == 'auxin':
                self.mxrstrips['auxin'] = {}
                self.aux_count = int(stripattribs['cnt'])
                try:
                    fader = strip.find('fader')
                    faderattribs = fader.attrib
                    fadercontrol = ControlFactory.create_control('fader', self.protocol)
                    fadercontrol.fill(faderattribs['cmdtyp'], faderattribs['cmd'], faderattribs['range'])
                    self.mxrstrips[stripattribs['type']].update({'fader':fadercontrol})
                except:
                    pass
                try:
                    mute = strip.find('mute')
                    muteattribs = mute.attrib
                    mutecontrol = ControlFactory.create_control('mute', self.protocol)
                    mutecontrol.fill(muteattribs['cmdtyp'], muteattribs['cmd'], None)
                    self.mxrstrips[stripattribs['type']].update({'mute' : mutecontrol})
                except:
                    pass
                try:
                    scribble = strip.find('scribble')
                    scribbleattribs = scribble.attrib
                    scribblecontrol = ControlFactory.create_control('scribble', self.protocol)
                    scribblecontrol.fill(scribbleattribs['cmdtyp'], scribbleattribs['cmd'], '')
                    self.mxrstrips[stripattribs['type']].update({'scribble' : scribblecontrol})
                except:
                    pass
                for x in range(1, self.aux_count + 1):
                    self.mxrconsole.append(
                        {'name': stripattribs['name'] + '{0:02}'.format(x), 'type': stripattribs['type'],
                         'channum': x})
            elif stripattribs['type'] == 'bus':
                self.mxrstrips['bus'] = {}
                self.bus_count = int(stripattribs['cnt'])
                try:
                    fader = strip.find('fader')
                    faderattribs = fader.attrib
                    fadercontrol = ControlFactory.create_control('fader', self.protocol)
                    fadercontrol.fill(faderattribs['cmdtyp'], faderattribs['cmd'], faderattribs['range'])
                    self.mxrstrips[stripattribs['type']].update({'fader':fadercontrol})
                except:
                    pass
                try:
                    mute = strip.find('mute')
                    muteattribs = mute.attrib
                    mutecontrol = ControlFactory.create_control('mute', self.protocol)
                    mutecontrol.fill(muteattribs['cmdtyp'], muteattribs['cmd'], None)
                    self.mxrstrips[stripattribs['type']].update({'mute' : mutecontrol})
                except:
                    pass
                try:
                    scribble = strip.find('scribble')
                    scribbleattribs = scribble.attrib
                    scribblecontrol = ControlFactory.create_control('scribble', self.protocol)
                    scribblecontrol.fill(scribbleattribs['cmdtyp'], scribbleattribs['cmd'], '')
                    self.mxrstrips[stripattribs['type']].update({'scribble' : scribblecontrol})
                except:
                    pass
                for x in range(1, self.bus_count + 1):
                    self.mxrconsole.append(
                        {'name': stripattribs['name'] + '{0:02}'.format(x), 'type': stripattribs['type'],
                         'channum': x})
            elif stripattribs['type'] == 'main':
                self.mxrstrips['main'] = {}
                self.main_count = int(stripattribs['cnt'])
                try:
                    fader = strip.find('fader')
                    faderattribs = fader.attrib
                    fadercontrol = ControlFactory.create_control('fader', self.protocol)
                    fadercontrol.fill(faderattribs['cmdtyp'], faderattribs['cmd'], faderattribs['range'])
                    self.mxrstrips[stripattribs['type']].update({'fader':fadercontrol})
                except:
                    pass
                try:
                    mute = strip.find('mute')
                    muteattribs = mute.attrib
                    mutecontrol = ControlFactory.create_control('mute', self.protocol)
                    mutecontrol.fill(muteattribs['cmdtyp'], muteattribs['cmd'], None)
                    self.mxrstrips[stripattribs['type']].update({'mute' : mutecontrol})
                except:
                    pass
                try:
                    scribble = strip.find('scribble')
                    scribbleattribs = scribble.attrib
                    scribblecontrol = ControlFactory.create_control('scribble', self.protocol)
                    scribblecontrol.fill(scribbleattribs['cmdtyp'], scribbleattribs['cmd'], '')
                    self.mxrstrips[stripattribs['type']].update({'scribble' : scribblecontrol})
                except:
                    pass
                for x in range(1, self.main_count + 1):
                    self.mxrconsole.append(
                        {'name': stripattribs['name'] + '{0:02}'.format(x), 'type': stripattribs['type'],
                         'channum': x})

        pass
             # if stripcontrols is not None:
             #     idx = 0
             #     for control in stripcontrols:
             #         self.mxrstrips.append(ControlFactory.create_control(control, self.protocol))
                     #self.mxrstrips[idx].fill(stripattribs['type'], )


        #print(self.inputsliders)