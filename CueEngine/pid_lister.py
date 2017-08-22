#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess
import types
import argparse
import socket
from time import sleep
from curses.ascii import isprint
import psutil
import logging



pid_iter = psutil.process_iter()
for process in psutil.process_iter():
    print(process.pid)
    print(process.cmdline())
    # try:
    #     if 'linux-show-player' in process.cmdline()[1]:
    #         print('MuteMap pid:{}'.format(process.pid))
    #         break
    # except IndexError as e:
    #     print(e)
