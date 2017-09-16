#!/usr/bin/env python3
__author__ = 'mac'

import sys
import logging

from PyQt5 import QtWidgets

from ShowControl.utils import styles

from CueEngine.CueEngine import CueDlg

def main():
    logging.info('Message from main')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = CueDlg()
    ui.resize(900,800)
    ui.disptext()
    ui.setfirstcue(1)  # slaves should execute cue 0 as the initialization

    ui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
	main()
