import sys
import queue
from time import sleep
import re
import threading

from PyQt5.QtCore import *

from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
import jack


class receiver(QThread):
    """..."""
    rcvrsignal = pyqtSignal(str, name='rcvrsignaled')  # define a custom signal called 'rcvrsignal' whose name is 'rcvrsignaled'
    def __init__(self, sck, mixer_ip, mixer_port):
        QThread.__init__(self)
        self.mixer_ip = mixer_ip
        self.mixer_port = mixer_port
        self.threadshouldstop = False
        self.rcvsndqueue = queue.Queue()
        self.sck = sck
    '''overloads QThread run() function'''
    def run(self):
        """..."""
        while not self.threadshouldstop:
            if not self.rcvsndqueue.empty():
                #sleep(.1)
                print("in receiver thread")
                #self.rcvrsignal.emit("hi from receiver thread")
                while not self.rcvsndqueue.empty():
                    print("in receiver thread queue handler")
                    msg = self.rcvsndqueue.get()
                    self.sck.sendto(msg.dgram, (self.mixer_ip, self.mixer_port))
                    self.msleep(100)
                    data, server = self.sck.recvfrom(1024)
                    data_str = data.decode('utf-8')
                    data_strx = re.sub('\0|\n', '', data_str)

                    addstr = re.split(',s| ', data_strx)
                    self.rcvrsignal.emit('{0}'.format(addstr))
                    #print('{0}'.format(addstr))
            else:
                self.msleep(200)

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True
    # todo-mac needs to handle ip and port arguments
    def queue_msg(self, msg, device):
        """..."""
        cmd_pack = (msg, (device.IP, device.PORT))
        self.rcvsndqueue.put(cmd_pack)

class sender(QThread):
    """..."""
    sndrsignal = pyqtSignal(str, name='sndrsignaled') #define a custom signal called 'signal' whose name is 'signaled'

    def __init__(self, socket):
        """..."""
        QThread.__init__(self)
        self.threadshouldstop = False
        self.sndrqueue = queue.Queue()
        self.socket = socket

    '''overloads QThread run() function'''
    def run(self):
        """..."""
        while not self.threadshouldstop:
            if not self.sndrqueue.empty():
                #sleep(0.1)
                print("in sender thread")
                #self.sndrsignal.emit("hi from sender thread")
                while not self.sndrqueue.empty():
                    packet =  self.sndrqueue.get()
                    msg = packet[0].dgram
                    self.socket.sendto(msg, packet[1])
                    self.msleep(10)
            else:
                self.msleep(200)

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True

    # def queue_msg(self, msg, target_ip, target_port, mixer):
    def queue_msg(self, msg, device):
        """..."""
        # cmd_pack = (msg, (target_ip, target_port))
        cmd_pack = (msg, (device.IP, device.PORT))
        self.sndrqueue.put(cmd_pack)

class cmd_receiver(QThread):
    """..."""
    cmd_rcvrsignal = pyqtSignal(bytearray, name='cmd_rcvrsignaled') #define a custom signal called 'signal' whose name is 'signaled'

    def __init__(self, sck):
        """..."""
        QThread.__init__(self)
        self.threadshouldstop = False
        self.rcvsndqueue = queue.Queue()
        self.sck = sck

    '''overloads QThread run() function'''
    def run(self):
        """..."""
        while not self.threadshouldstop:
            print("in command receiver thread")
            #self.cmd_rcvrsignal.emit("hi from command receiver thread")
            sleep(0.1)
            data, server = self.sck.recvfrom(1024)
            self.cmd_rcvrsignal.emit(bytearray(data))
            '''1/5/2017 had to change the bytes datagram to bytearray
               because there is a known bug in emit when using
               bytes the bytes get corrupted'''

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True

    def queue_msg(self, msg, device):
        """..."""
        self.rcvsndqueue.put(msg)

class AMIDIsender(QThread):
    """MIDI queued/threaded sender for ALSA interfaces"""
    amidi_sndrsignal = pyqtSignal(str, name='amidi_sndrsignaled') #define a custom signal called 'signal' whose name is 'signaled'

    def __init__(self):
        """..."""
        QThread.__init__(self)
        self.threadshouldstop = False
        self.MIDIsndrqueue = queue.Queue()
        self.midiout = None
        self.port_name = None

    '''overloads QThread run() function'''
    def run(self):
        """..."""
        while not self.threadshouldstop:
            if not self.MIDIsndrqueue.empty():
                #sleep(0.1)
                print("in sender thread")
                #self.sndrsignal.emit("hi from sender thread")
                while not self.MIDIsndrqueue.empty():
                    #self.socket.sendto(self.sndrqueue.get().dgram, (self.mixer_ip, self.mixer_port))
                    packet =  self.MIDIsndrqueue.get()
                    self.midiout.send_message(packet)
                    self.msleep(10)
            else:
                self.msleep(200)

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True

    def queue_msg(self, msg, device):
        """..."""
        cmd_pack = msg
        self.MIDIsndrqueue.put(cmd_pack)

    def setport(self, port):
        for n in range(10):  # wait up to 10 seconds for app to launch and the port be available
            try:
                self.midiout, self.port_name = open_midiport(port[0],port[1], interactive=False)
                break
            except (EOFError, KeyboardInterrupt):
                sys.exit()
            except ValueError as err:
                print('count: {} Error: {}'.format(n, err.args))
                sleep(1)

class JMIDIsender(QThread):
    """MIDI queued/threaded sender for JACK interfaces"""
    jmidi_sndrsignal = pyqtSignal(str, name='jmidi_sndrsignaled') #define a custom signal called 'signal' whose name is 'signaled'
    def __init__(self, clientname):
        """..."""
        QThread.__init__(self)
        self.threadshouldstop = False
        self.MIDIsndrqueue = queue.Queue()
        self.client = jack.Client('jmidi_{}'.format(clientname))
        self.outport = self.client.midi_outports.register("output")
        self.client.set_process_callback(self.process)
        self.client.set_xrun_callback(self.xrun)
        self.client.set_shutdown_callback(self.shutdown)
        self.client.activate()

    def print_error(self, *args):
        print(*args, file=sys.stderr)

    def xrun(self, delay):
        self.print_error("An xrun occured, increase JACK's period size?")

    def shutdown(self, status, reason):
        self.print_error('JACK shutdown!')
        self.print_error('status:', status)
        self.print_error('reason:', reason)
        # self.event.set()

    def stop_callback(self, msg=''):
        if msg:
            self.print_error(msg)
        # for port in self.client.outports:
        #     port.get_array().fill(0)
        # self.event.set()
        # raise jack.CallbackExit
            self.client.deactivate()
            self.client.close()

    def process(self, frames):
        for port in self.client.midi_outports:
            port.clear_buffer()
        offset = 0
        try:
            midievent = self.MIDIsndrqueue.get_nowait()
            print('In midi process: {0} || {1}'.format(midievent[0], midievent[1:]))
            self.client.midi_outports[midievent[0]].write_midi_event(offset, midievent[1:])
            # offset += 1
        except queue.Empty:
            pass

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.stop_callback('JACK MIDI thread closing')
        self.threadshouldstop = True

    def setport(self, port):
        '''Connect this ouput client (self.outport) to the input of another client or a physical output'''
        self.client.connect(self.outport, port)

    def queue_msg(self, msg, device):
        """Add a MIDI event to the cue
            parameters in:
            event - list [<port index>, <midi chan>, <control number on the midi device>, <value>]
                multi ports (i.e. port_index) is not implemented as of 1/26/2017
            """
        midievent = [0]
        midievent.extend(int(v,16) for v in msg.split(','))
        self.MIDIsndrqueue.put(midievent)

