#!/usr/bin/env python3
__author__ = 'mac'

import os, sys, inspect, subprocess, time

bla = subprocess.Popen(['python3', '/home/mac/PycharmProjs/linux-show-player/linux-show-player', '-f', '/home/mac/Shows/Pauline/sfx.lsp'])
# /home/mac/PycharmProjs/linux-show-player/linux-show-player
while True:
    inkey = input('> ')
    if inkey == 'q':
        bla.terminate()
        exit()
    time.sleep(100)