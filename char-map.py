#!/usr/bin/env python3
import argparse
import logging
parser = argparse.ArgumentParser()
parser.add_argument("--log", default="INFO", choices=["INFO", "DEBUG"], help="Set log level: INFO,DEBUG")
args = parser.parse_args()
if args.log == 'INFO':
    loglev = logging.INFO
else:
    loglev = logging.DEBUG

# the following sets up the root logger so all subsequent calls get a reference to this one
from ShowControl.utils.ShowControlConfig import LOG_DIR
logging.basicConfig(level=loglev,
                  filename=LOG_DIR + '/CharMap.log', filemode='w',
                  format='%(name)s %(levelname)s %(message)s')


from CharMap.main import main

logging.info('in char-map.py before call to main()')
main()

logging.info('in char-map.py after call to main()')
