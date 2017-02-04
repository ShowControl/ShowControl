#!/usr/bin/env python3
'''

Created on Nov 16, 2014

@author: mac
'''

import os, sys, inspect
import types
import argparse
import socket
from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client
from rtmidi.midiconstants import CONTROL_CHANGE
#from ShowMixer import Show

supported_protocols = ['osc','midi']
supported_controls = ['fader','mute','scribble']

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class ControlFactory:
    class oscfader:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng, anom):
            self.cmdstr = cmdstr
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, cnum, value):
            osc_address = self.cmdstr.replace('#', '{0:02}'.format(cnum))
            msg = osc_message_builder.OscMessageBuilder(address=osc_address)
            msg.add_arg(translate(value, 0, 1024, 0.0, 1.0))
            msg = msg.build()
            return msg

    class midifader:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []
            self.anoms = None
            self.rangehigh = 0
            self.rangelow = 0

        def fill(self, ctyp, cmdstr, crng, anoms):
            self.cmdstr = cmdstr
            self.controlchange, self.changenumbase, self.waste = cmdstr.split(',')
            self.crng = crng
            self.rangelow, self.rangehigh = crng.split(',')
            self.ctyp = ctyp
            try:
                self.anoms = dict(item.split("=") for item in anoms.split(":"))
            except:
                pass

        def anomaly(self, chan):
            """Had to add this method to handle various things like gaps or offsets
            the change number sequence for certain mixers (i.e. Yamaha 01V)
            anoms is a dictionary of these anomalies from the mixer def file
            currently supported anoms keys: offset, gap"""
            i_ctlnum = int(self.changenumbase, 16) + int(chan)
            if self.anoms != None:
                # Handle offsets
                if 'offset' in self.anoms:
                    i_ctlnum += int(self.anoms['offset'])
                # Handles gap
                if 'gap' in self.anoms:
                    if i_ctlnum >= int(self.anoms['gap']):
                        i_ctlnum +=1
            return i_ctlnum
            # if 'offset' in self.anoms:
            #     adjusted = int(chan) + int(self.anoms['offset'])
            # else:
            #     adjusted = int(chan)
            # if 'gap' in self.anoms:
            #     if int(int(self.anoms['gap'])) == adjusted:
            #         adjusted = None
            # return adjusted

        def Set(self, mixerchan, value):
            # handle anomalies
            cnum = self.anomaly(mixerchan)
            # convert to hex string
            ctlnum = '{:02x}'.format(cnum)
            # # handle anomalies
            # if self.anoms != None:
            #     cnum = self.anomaly(mixerchan)
            #     if cnum == None:
            #         return None
            # else:
            #     cnum = mixerchan
            # ctlnum = '{:02x}'.format(int(self.changenumbase, 16) + cnum)
            f_val = translate(value, 0, 1024, int(self.rangelow), int(self.rangehigh))
            val = '{:02x}'.format(int(f_val))
            msg = '{0},{1},{2}'.format(self.controlchange,ctlnum,val)
            return msg

    class oscmute:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng, anoms):
            self.cmdstr = cmdstr
            self.ctyp = ctyp

        def Set(self, cnum, muteState):
            osc_address = self.cmdstr.replace('#', '{0:02}'.format(cnum))
            msg = osc_message_builder.OscMessageBuilder(address=osc_address)
            msg.add_arg(muteState)
            msg = msg.build()
            return msg

    class midimute:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.controlchange = ''
            self.changenumbase = ''
            self.crng = []
            self.anoms = None

        def fill(self, ctyp, cmdstr, crng, anoms):
            self.cmdstr = cmdstr
            self.controlchange, self.changenumbase, self.waste = cmdstr.split(',')
            self.ctyp = ctyp
            self.rl, self.rh = crng.split(',')
            try:
                self.anoms = dict(item.split("=") for item in anoms.split(":"))
            except:
                pass

        def anomaly(self, chan):
            """Had to add this method to handle various things like gaps or offsets
            the change number sequence for certain mixers (i.e. Yamaha 01V)
            anoms is a dictionary of these anomalies from the mixer def file
            currently supported anoms keys: offset, gap"""
            i_ctlnum = int(self.changenumbase, 16) + int(chan)
            if self.anoms != None:
                # Handle offsets
                if 'offset' in self.anoms:
                    i_ctlnum += int(self.anoms['offset'])
                # Handles gap
                if 'gap' in self.anoms:
                    if i_ctlnum >= int(self.anoms['gap']):
                        i_ctlnum +=1
            return i_ctlnum

        def Set(self, mixerchan, value):
            # handle anomalies
            cnum = self.anomaly(mixerchan)
            # convert to hex string
            ctlnum = '{:02x}'.format(cnum)
            #
            if value == 0:
                val = '{:02x}'.format(int(self.rh))
            elif value == 1:
                val = '{:02x}'.format(int(self.rl))
            else:
                val = '00'
            msg = '{0},{1},{2}'.format(self.controlchange,ctlnum,val)
            return msg

    class oscscribble:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng, anoms):
            self.cmdstr = cmdstr
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, cnum, scrbltxt):
            """Handle osc output to scribble control"""
            osc_address = self.cmdstr.replace('#', '{0:02}'.format(cnum))
            msg = osc_message_builder.OscMessageBuilder(address=osc_address)
            # tmpstr = scrbltxt[:5]
            msg.add_arg(scrbltxt[:5])
            msg = msg.build()
            return msg

    class midiscribble:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng, anoms):
            self.cmdstr = cmdstr
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, cnum, value):
            return None

    @staticmethod
    def create_control(control_type, mixer_protocol):
        if mixer_protocol in supported_protocols:
            return eval('ControlFactory.{}{}()'.format(mixer_protocol, control_type))
        else:
            return None

if __name__ == "__main__":
    """If main, run test code below"""
    for control in supported_controls:
        for protocol in supported_protocols:
            control_object = ControlFactory.create_control(control, protocol)
            print(type(control_object))
            control_object = None
    testmidifader = ControlFactory.create_control('fader', 'midi')
    testmidifader.fill('input', 'B#,1C,XX', '0,127')
    msg = testmidifader.Set(2,0)
    # msg is a comma separated string
    # so the following could be used to get it to a list of ints:
    # x = list(map(int,msg.split(',')))
    pass