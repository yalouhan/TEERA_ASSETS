import numpy as np
import pandas as pd
import json

def load_json(json_path):
    with open (json_path, 'r') as file:
        key_sequences = json.load(file)
        keystroke_dynamic = []

        for key_sequence in key_sequences:
            keys = []
            keystrokes = key_sequence['data']

            for keystroke in keystrokes:
                events = {}
                events['key'] = keystroke['key']
                events['event'] = keystroke['type']
                events['timestamp'] = keystroke['time']
                keys.append(events)

            keystroke_dynamic.append(keys)

    return keystroke_dynamic

def get_keycode(key):
    special_keys = {
        'space': 32, 'Backspace': 8, 'Enter': 13, 'Tab': 9,
        'Escape': 27, 'Delete': 127, 'Shift': 16, 'CapsLock': 20,
        'Ctrl': 17, 'Alt': 18, 'Cmd': 91, 'Left': 37, 'Up': 38,
        'Right': 39, 'Down': 40, ',': 188, '.': 190, '/': 191,
        ';': 186, "'": 222, '[': 219, ']': 221, '\\': 220,
        '`': 192, '=': 187, '-': 189
    }

    if key in special_keys:
        return special_keys[key]
    
    if len(key) == 1 and key.isprintable():
        return ord(key)
    
    return None  # For unmapped keys


def lookup_key_and_compute(i, keystroke):
    key = keystroke[i]['key'].lower()
    time = keystroke[i]['timestamp']
    release_time = 0
    next_press = 0
    next_release = 0
    next_press_key = None

    for j in range(i+1, len(keystroke)):
        if keystroke[j]['key'].lower() == key and keystroke[j]['event'] == 'keyup' and release_time == 0:
            release_time = keystroke[j]['timestamp']
        elif keystroke[j]['event'] == 'keydown' and next_press == 0 and next_press_key is None:
            next_press = keystroke[j]['timestamp']
            next_press_key = keystroke[j]['key'].lower()
        elif keystroke[j]['event'] == 'keyup' and keystroke[j]['key'].lower() == next_press_key and next_release == 0:
            next_release = keystroke[j]['timestamp']
        else:
            continue

    HL = release_time - time
    PL = next_press - time
    IL = next_press - release_time
    RL = next_release - release_time

    return HL, PL, IL, RL


def pre_process(keystroke_dynammic):
    keystroke_batch = []
    
    for keystrokes in keystroke_dynamic:
        feature_sequence = []
        for i, keystroke in enumerate(keystrokes):
            key = keystroke['key']
            event = keystroke['event']
            if event == 'keydown':
                HL, PL, IL, RL = lookup_key_and_compute(i, keystrokes)
                feature = [get_keycode(key), HL, PL, IL, RL]
                feature_sequence.append(feature)
            else:
                continue
        keystroke_batch.append(feature_sequence)

    return keystroke_batch       

if __name__ == "__main__": 
    keystroke_dynamic = load_json('data_process/datas/haoyu wang_key_events_sessions (2).json')
    feature_sequence = pre_process(keystroke_dynammic=keystroke_dynamic)

    with open ('legal_sequences.txt', 'w') as file:
        for features in feature_sequence:
            for feature in features:
                for val in feature:
                    file.write(f'{val},')
                file.write(f'\n')
                print(f'{feature}')
            print(f'\n')
            file.write(f'\n')

