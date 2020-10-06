'''
Loads specified configuration file and collects data until killed (cleanly exits)

Usage:
  python3 -i start_run.py --config_name <config file/dir> --controller_config <controller config file>

'''
import larpix
import larpix.io
import larpix.logger

import base
import load_config

import argparse
import json
from collections import defaultdict
import time

_default_config_name=None
_default_controller_config=None
_default_runtime=30*60 # 30-min run files

def main(config_name=_default_config_name, controller_config=_default_controller_config, runtime=_default_runtime):
    print('START RUN')
    # create controller
    c = None
    if config_name is None:
        c = base.main(controller_config)
    else:
        if controller_config is None:
            c = load_config.main(config_name, logger=True)
        else:
            c = load_config.main(config_name, controller_config, logger=True)

    c.start_listening()
    while True:
        start_time = time.time()
        c.logger = larpix.logger.HDF5Logger()
        print('new run file at ',c.logger.filename)
        c.logger.enable()
        while True:
            try:
                c.read()
                c.reads = []
                if time.time() > start_time + runtime: break
            except:
                c.logger.flush()
                raise
        c.logger.flush()

    print('END RUN')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_name', default=_default_config_name, type=str, help='''Directory or filename to load chip configurations from''')
    parser.add_argument('--controller_config', default=_default_controller_config, type=str, help='''Hydra network configuration file''')
    parser.add_argument('--runtime', default=_default_runtime, type=float, help='''Time duration before flushing remaining data to disk and initiating a new run (in seconds) (default=%(default)s)''')
    args = parser.parse_args()
    c = main(**vars(args))