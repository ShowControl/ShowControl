#!/usr/bin/env python3
__author__ = 'mac'

import sys
import logging

from PyQt5 import QtWidgets

from ShowControl.utils import styles

from CharMap.CharMap import CharMap_MainWindow

def main():
    logging.info('Message from main')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(styles.QLiSPTheme_Dark)
    ui = CharMap_MainWindow()
    ui.resize(900,800)
    ui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
	main()
