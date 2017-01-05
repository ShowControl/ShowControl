import queue
from time import sleep
import re

from PyQt5.QtCore import *

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
            sleep(1)
            print("in receiver thread")
            #self.rcvrsignal.emit("hi from receiver thread")
            while not self.rcvsndqueue.empty():
                msg = self.rcvsndqueue.get()
                self.sck.sendto(msg.dgram, (self.mixer_ip, self.mixer_port))
                sleep(0.1)
                data, server = self.sck.recvfrom(1024)
                data_str = data.decode('utf-8')
                data_strx = re.sub('\0|\n', '', data_str)

                addstr = re.split(',s| ', data_strx)
                self.rcvrsignal.emit('{0}'.format(addstr))
                #print('{0}'.format(addstr))

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True

    def queue_msg(self, msg):
        """..."""
        self.rcvsndqueue.put(msg)


class sender(QThread):
    """..."""
    sndrsignal = pyqtSignal(str, name='sndrsignaled') #define a custom signal called 'signal' whose name is 'signaled'

    def __init__(self, socket, mixer_ip, mixer_port):
        """..."""
        QThread.__init__(self)
        self.threadshouldstop = False
        self.sndrqueue = queue.Queue()
        self.mixer_ip = mixer_ip
        self.mixer_port = mixer_port
        self.socket = socket

    '''overloads QThread run() function'''
    def run(self):
        """..."""
        while not self.threadshouldstop:
            sleep(0.5)
            print("in sender thread")
            #self.sndrsignal.emit("hi from sender thread")
            while not self.sndrqueue.empty():
                self.socket.sendto(self.sndrqueue.get().dgram, (self.mixer_ip, self.mixer_port))

    '''called from widget.stopthread to flag thread to close'''
    def setstopflag(self):
        """..."""
        self.threadshouldstop = True

    def queue_msg(self, msg):
        """..."""
        self.sndrqueue.put(msg)

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
            #print("in command receiver thread")
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

    def queue_msg(self, msg):
        """..."""
        self.rcvsndqueue.put(msg)

