#!/usr/bin/env python3
import logging

# the following sets up the root logger so all subsequent calls get a reference to this one
from ShowControl.utils.ShowControlConfig import LOG_DIR
logging.basicConfig(level=logging.DEBUG,
                   filename=LOG_DIR + '/CueEngine.log', filemode='w',
                   format='%(name)s %(levelname)s %(message)s')


from CueEngine.main import main


logging.info('in cue-engine.py before call to main()')
main()

logging.info('in cue-engine.py after call to main()')
