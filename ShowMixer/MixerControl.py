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

class ControlFactory:
    class slider:
        pass
    class mute:
        def SetMuteState(self, muteButton, muteState):
            osc_add='/ch/' + muteButton + '/mix/on'
            #print(osc_add)
            msg = osc_message_builder.OscMessageBuilder(address=osc_add)
            msg.add_arg(muteState)
            msg = msg.build()
            client.send(msg)

    class scribble:
        pass
    @staticmethod
    def create_control(control_type):
        if control_type=="slider":
            return ControlFactory.slider()
        elif control_type=="mute":
            return ControlFactory.mute()
        elif control_type=="scribble":
            return ControlFactory.scribble()


class MixerControl:
    '''
    
    Created on Nov 16, 2014
    
    @author: mac
    '''
    def SetMuteState(self, muteButton, state):
        pass

#The_Show = Show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.53.40", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=10023, help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.UDPClient(args.ip, args.port)
    mutebtn = ControlFactory.create_control("mute")
    for cnum in range(1,10):
        print("{0:02}".format(cnum))
        mutebtn.SetMuteState("{0:02}".format(cnum),1) #msg.add_arg(The_Show.mixer.mutestyle['unmute'])
        sleep(1)
        mutebtn.SetMuteState("{0:02}".format(cnum),0) #msg.add_arg(The_Show.mixer.mutestyle['unmute'])
