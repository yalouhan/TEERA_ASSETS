import json

def load_json(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)

def get_keycode(key):
    keycodes = {
        'Space': 32, 'Backspace': 8, 'Enter': 13, 'Tab': 9,
        'Escape': 27, 'Delete': 127, 'Shift': 16
    }
    return keycodes.get(key, ord(key) if len(key) == 1 else None)

def pre_process(keystroke_dynamic):
    dynamic_features = []
    for sequence in keystroke_dynamic:
        last_press_time = {}
        last_release_time = None
        sequence_features = []

        for event in sequence['data']:
            feature = [None, None, None, None]  # Initialize feature vector with Nones
            keycode = get_keycode(event['key'])
            event_type = event['type']
            timestamp = event['time']

            if keycode is not None:
                feature.append(keycode)  # Append keycode to feature vector

                if event_type == 'keydown':
                    if last_press_time:
                        # Press Latency (PL)
                        PL = timestamp - max(last_press_time.values())
                        feature[2] = PL
                    last_press_time[event['key']] = timestamp

                elif event_type == 'keyup':
                    if event['key'] in last_press_time:
                        # Hold Latency (HL)
                        HL = timestamp - last_press_time[event['key']]
                        feature[0] = HL

                        if last_release_time:
                            # Release Latency (RL)
                            RL = timestamp - last_release_time
                            feature[3] = RL

                        last_release_time = timestamp
                        del last_press_time[event['key']]

            if last_release_time and last_press_time:
                # Inter-key Latency (IL)
                IL = min(last_press_time.values()) - last_release_time
                feature[1] = IL

            if None not in feature:  # Only add complete feature vectors
                sequence_features.append(feature)

        dynamic_features.append(sequence_features)

    return dynamic_features

if __name__ == "__main__":
    keystroke_dynamic = load_json('data_process/datas/haoyu wang_key_events_sessions.json')
    feature_sequence = pre_process(keystroke_dynamic)

    with open('Template_sequences.txt', 'w') as file:
        for sequence in feature_sequence:
            for features in sequence:
                file.write(f'{features}\n')
                print(f'{features}')
            file.write('\n')
