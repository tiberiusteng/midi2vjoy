import argparse
import json
import sys
import threading
import time
import platform

import mido
from loguru import logger

is_windows_platform = False
vjoy_device = None
if platform.system().lower() == 'windows':
    import pyvjoy
    vjoy_device = pyvjoy.VJoyDevice(1)
    is_windows_platform = True


def search_button(ctr, mapping):
    try:
        return [element for element in mapping if element['control'] == ctr][0]
    except IndexError:
        return None


def resolve_midi_name(midi_name_start_with, possible_names):
    midi_name = None
    for input_name in possible_names:
        if input_name.startswith(midi_name_start_with):
            midi_name = input_name
            break
    return midi_name


def simulate_vjoy_btn_change(btn_number, is_pushed):
    if is_windows_platform and vjoy_device:
        vjoy_device.set_button(btn_number, is_pushed)
    logger.debug(f"vJoy button {btn_number} will be set to {is_pushed}")


def simulate_vjoy_push_btn(btn_number, activation_duration):
    delay = .100
    if activation_duration:
        delay = activation_duration
    simulate_vjoy_btn_change(btn_number, True)
    time.sleep(delay)
    simulate_vjoy_btn_change(btn_number, False)
    time.sleep(delay)


def simulate_vjoy_slide(axis, value):
    logger.debug(f"vJoy axis {axis} ({getattr(pyvjoy, 'HID_USAGE_' + axis)}) will be set to {value}: {0x8000 * value / 128}")
    if is_windows_platform and vjoy_device:
        vjoy_device.set_axis(getattr(pyvjoy, "HID_USAGE_" + axis), int(0x8000 * value / 128))


class Midi2vJoy(threading.Thread):
    def __init__(self, config_filename):
        super().__init__()
        self.config_filename = config_filename
        self.inport = None
        self.outport = None
        self.mapping = None

    def run(self):
        with open(self.config_filename, "r") as f:
            config = json.load(f)
            self.mapping = config['mapping']
        logger.debug(config)

        input_midi_name = resolve_midi_name(config['input'], mido.get_input_names())
        output_midi_name = resolve_midi_name(config['output'], mido.get_output_names())

        logger.debug(f"Selected INPUT : {input_midi_name}")
        logger.debug(f"Selected OUTPUT : {output_midi_name}")

        self.inport = mido.open_input(name=input_midi_name, callback=self.callback_midi_message)
        self.outport = mido.open_output(name=output_midi_name)

        self.load_initial_values()

        while True:
            time.sleep(1)

    def callback_midi_message(self, msg):
        logger.debug(msg)
        if type(msg) is mido.Message:
            btn = search_button(msg.control, self.mapping)
            if btn:
                logger.debug(btn)
                if btn['type'] == 'pad' or btn['type'] == 'push':
                    simulate_vjoy_btn_change(btn['vjoy-btn'], msg.value > 64)
                elif btn['type'] == 'rotary':
                    activation_duration=btn['activation-duration'] if 'activation-duration' in btn else None
                    if msg.value > 0:
                        simulate_vjoy_push_btn(btn['vjoy-btn-inc'], activation_duration)
                    else:
                        simulate_vjoy_push_btn(btn['vjoy-btn-dec'], activation_duration)
                    msg.value = 0
                    self.outport.send(msg)
                elif btn['type'] == 'slider' or btn['type'] == 'axis':
                    simulate_vjoy_slide(btn['axis-name'], msg.value)

    def load_initial_values(self):
        for m in self.mapping:
            initial_value = 0
            if 'initial-value' in m and 'channel' in m:
                initial_value = m.pop('initial-value')
            
            msg = mido.Message(type='control_change', channel=m['channel'],
                                control=m['control'], value=initial_value)
            self.outport.send(msg)

            if m['type'] == 'slider' or m['type'] == 'axis':
                simulate_vjoy_slide(m['axis-name'], initial_value)

        logger.debug('Initial values are loaded successfully')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', help='mapping.json', required=True)
    return parser.parse_args(args)


def main(args):
    args_parsed = parse_args(args)
    m = Midi2vJoy(args_parsed.config)
    m.start()


if __name__ == "__main__":
    main(sys.argv[1:])
