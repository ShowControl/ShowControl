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

#from ShowMixer import Show

supported_protocols = ['osc','midi']
supported_controls = ['fader','mute','scribble']

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
            pass

    class midifader:
        pass

    class oscmute:
        def __init__(self):
            self.ctyp = ''
            self.cmdstr = ''
            self.crng = []

        def fill(self, ctyp, cmdstr, crng):
            self.cmdstr = cmdstr
            self.crng = crng
            self.ctyp = ctyp

        def Set(self, muteButton, muteState):
            osc_add='/ch/' + muteButton + '/mix/on'
            #print(osc_add)
            msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            msg.add_arg(muteState)
            msg = msg.build()
            #client.send(msg)

    class midimute:
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

        def Set(self):
            """Handle osc output to scribble control"""
            # osc_add = '/ch/' + '{0:02}'.format(cnum) + '/config/name'
            # msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            # tmpstr = char.attrib['actor'][:5]
            # # print('Temp String: ' + tmpstr)
            # msg.add_arg(char.attrib['actor'][:5])
            # msg = msg.build()
            # # client.send(msg)
            # self.mxr_sndrthread.queue_msg(msg, MXR_IP, MXR_PORT)
            # thislbl = self.findChild(QtWidgets.QLabel, name='scr' + '{0:02}'.format(cnum))
            # thislbl.setText(tmpstr)

    class midiscribble:
        def Set(self):
            pass

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
