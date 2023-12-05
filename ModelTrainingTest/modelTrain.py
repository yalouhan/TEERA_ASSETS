import numpy as np
import pandas as pd
import json
from hmmlearn import hmm
from joblib import load
import os
import csv
import matplotlib.pyplot as plt

class Data:
    json_path = ''
    keystroke_dynamic = []
    keystroke_batch = []
    clear_data = []
    clear_data_np = []
    model = None
    features = []
    scores = []
    scores_mean = 0
    scores_median = 0
    
    def __init__(self, json_path):
        self.json_path = json_path
        self.model = hmm.GaussianHMM(n_components=8, covariance_type='diag')
    def load_json(self):
        with open (self.json_path, 'r') as file:
            key_sequences = json.load(file)

            for key_sequence in key_sequences:
                keys = []
                keystrokes = key_sequence['data']

                for keystroke in keystrokes:
                    events = {}
                    events['key'] = keystroke['key']
                    events['event'] = keystroke['type']
                    events['timestamp'] = keystroke['time']
                    keys.append(events)
                    if events['key'] == 'b':
                        break
                    else:
                        keys.append(events)

                self.keystroke_dynamic.append(keys)
    def get_keycode(key):
        special_keys = {
        'space': 32, 'Backspace': 8, 'Enter': 13, 'Tab': 9,
        'Escape': 27, 'Delete': 127, 'Shift': 16, 'CapsLock': 20,
        'Ctrl': 17, 'Alt': 18, 'Cmd': 91, 'Left': 37, 'Up': 38,
        'Right': 39, 'Down': 40, ',': 188, '.': 190, '/': 191,
        ';': 186, "'": 222, '[': 219, ']': 221, '\\': 220,
        '`': 192, '=': 187, '-': 189, 'Alt': 18, 'ArrowLeft': 37, 
        'ArrowUp': 38, 'ArrowRight': 39, 'ArrowDown': 40,
        }

        if key in special_keys:
            return special_keys[key]
        
        if len(key) == 1 and key.isprintable():
            return ord(key)
        
        return None
    def pre_process(self):
        for keystrokes in self.keystroke_dynammic:
            feature_sequence = []
            for i, keystroke in enumerate(keystrokes):
                key = keystroke['key']
                event = keystroke['event']
                if event == 'keydown':
                    HL, PL, IL, RL = self.two_gram_extracting(i, keystrokes)
                    feature = [self.get_keycode(key), HL, PL, IL, RL]
                    feature = [HL, PL, IL, RL]
                    feature_sequence.append(feature)
                else:
                    continue
            self.keystroke_batch.append(feature_sequence)
    def two_gram_extracting(i, keystroke):
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
    def data_clean(self):
        data = self.keystroke_batch
        for data_seg in data:
            clear_data_seg = [[float(i) for i in features] for features in data_seg[:-1] if features[0] != None]
            if clear_data_seg:
                self.clear_data.append(clear_data_seg)
                self.clear_data_np.append(np.array(clear_data_seg))
                # print(f'{clear_data_seg}')
        return self.clear_data, self.clear_data_np
    def scores_computing(self):
        for segment in self.clear_data_np:
            log_likelihood = self.model.score(segment)
            self.scores.append(log_likelihood)
        self.scores_mean = np.mean(self.scores)
        self.scores_median = np.median(self.scores)

class TemplateData(Data):
    threshold_mean = 0
    threshold_median = 0

    def __init__(self, json_path):
        super().__init__(json_path)
    def calc_threshold(self):
        self.threshold_mean = np.mean(self.scores) if self.scores else float('nan')
        self.threshold_median = np.median(self.scores) if self.scores else float('nan')

class TestData(Data):
    namedScores = {}

    def __init__(self, json_path):
        super().__init__(json_path)
    def score_clustering(self):
        name = self.json_path.strip().split('_')[0]
        self.namedScores[name] = [self.scores_median, self.scores_mean, self.scores]

features = {}
directory = 'data_process/datas/data_for_test'
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        file_path = os.path.join(directory, filename)
        name = filename.strip().split('_')[0]
        feature_cleaned = TestData(file_path).data_clean()
        features[name] = feature_cleaned

# with open ('harry_and_hugo.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for input_harry, input_hugo in zip (features['harry'], features['Hugo']):
#         writer.writerow(input_harry)
#         writer.writerow(input_hugo)

with open ('wendy.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for input_wendy in zip (features['wendy']):
        writer.writerow(input_wendy)


# with open ('test_scores.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for key, value in scores.items():
#         writer.writerow([key, value])

# scores_csv = []
# for key, value in scores.items():
#     csv_vals = []
#     csv_vals.append(key)
#     for score in value:
#         csv_vals.append(score)
#     scores_csv.append(csv_vals)
#     # print(f'{csv_vals}\n')
# with open ('test_with_letters_scores.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for score in scores_csv:
#         writer.writerow(score)