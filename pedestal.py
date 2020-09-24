import sys
import argparse
import json

import larpix
import larpix.io

import base
import base_warm

def main(controller_config=None, periodic_trigger_cycles=1281, runtime=60, channels=[0], chip_key='1-1-23', *args, **kwargs):
    # create controller
    c = base_warm.main(controller_config_file=controller_config, logger=True)

    # set args
    chip_keys = [chip_key]
    if chip_key is None:
        chip_keys = list(c.chips.keys())

    # set configuration
    c.io.double_send_packets = True
    for chip_key, chip in [(chip_key, chip) for (chip_key, chip) in c.chips.items() if chip_key in chip_keys]:
        chip.config.periodic_trigger_mask = [1]*64
        chip.config.channel_mask = [1]*64
        for channel in channels:
            chip.config.periodic_trigger_mask[channel] = 0
            chip.config.channel_mask[channel] = 0
        chip.config.periodic_trigger_cycles = periodic_trigger_cycles
        chip.config.enable_periodic_trigger = 1
        chip.config.enable_rolling_periodic_trigger = 1
        chip.config.enable_periodic_reset = 1
        #chip.config.enable_rolling_periodic_reset = 1 # non-default
        chip.config.enable_rolling_periodic_reset = 0
        chip.config.enable_hit_veto = 0
        #chip.config.periodic_reset_cycles = 1 # non-default
        chip.config.periodic_reset_cycles = 4096
        
        # write configuration
        registers = list(range(155,163)) # periodic trigger mask
        c.write_configuration(chip_key, registers)
        c.write_configuration(chip_key, registers)
        registers = list(range(131,139)) # channel mask
        c.write_configuration(chip_key, registers)
        c.write_configuration(chip_key, registers)
        registers = list(range(166,170)) # periodic trigger cycles
        c.write_configuration(chip_key, registers)
        c.write_configuration(chip_key, registers)
        registers = [128] # periodic trigger, reset, rolling trigger, hit veto
        c.write_configuration(chip_key, registers)
        c.write_configuration(chip_key, registers)
        c.write_configuration(chip_key, 'enable_rolling_periodic_reset')
        c.write_configuration(chip_key, 'enable_rolling_periodic_reset')
        c.write_configuration(chip_key, 'periodic_reset_cycles')
        c.write_configuration(chip_key, 'periodic_reset_cycles')

    for chip_key in c.chips:
        ok, diff = c.verify_configuration(chip_key)
        if not ok:
            print('config error',diff)
    c.io.double_send_packets = True    

    print('start pedestal run')
    base.flush_data(c, rate_limit=(1+1/(periodic_trigger_cycles*1e-7)*len(c.chips)))
    c.logger.enable()
    c.run(runtime,'collect data')
    c.logger.flush()
    print('packets read',len(c.reads[-1]))
    c.logger.disable()

    return c

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controller_config', default=None, type=str)
    parser.add_argument('--periodic_trigger_cycles', default=1281, type=int)
    parser.add_argument('--runtime', default=60, type=float)
    parser.add_argument('--channels', default=range(64), type=json.loads)
    parser.add_argument('--chip_key', default=None, type=str)    
    args = parser.parse_args()
    c = main(**vars(args))
