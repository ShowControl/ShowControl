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

        def fill(self, ctyp, cmdstr, crng):
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

        def fill(self, ctyp, cmdstr, crng):
            self.cmdstr = cmdstr
            self.controlchange, self.changenumbase, self.waste = cmdstr.split(',')
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, mixerchan, value):
            ctlnum = '{:02x}'.format(int(self.changenumbase, 16) + mixerchan)
            val = '{:02x}'.format(value)
            msg = '{0},{1},{2}'.format(self.controlchange,ctlnum,val)
            return msg

    class oscmute:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng):
            self.cmdstr = cmdstr
            self.crng = crng
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
            self.crng = []

        def fill(self, ctyp, cmdstr, crng):
            self.cmdstr = cmdstr
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, muteButton, muteState):
            pass

    class oscscribble:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng):
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

        def fill(self, ctyp, cmdstr, crng):
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