#!/usr/bin/env python3
__author__ = 'mac'

import sys
import logging

from PyQt5 import QtWidgets

from ShowControl.utils import styles
from ShowMixer.ShowMixer import ChanStripMainWindow

def main():
    logging.info('Mesage from main')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    chans = 32
    ui = ChanStripMainWindow()
    ui.addChanStrip()
    ui.resize(ui.max_slider_count * ui.ChanStrip_MinWidth, 800)
    ui.disptext()
    ui.initmutes()
    ui.initlevels()
    ui.setfirstcue()
    firstuuid = ui.getcurrentcueuuid()
    ui.set_scribble(firstuuid)
    ui.execute_cue_uuid(firstuuid)
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
	main()
