from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from hmmlearn import hmm
from joblib import load
import json
import numpy as np

app = Flask(__name__)
CORS(app)
@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    if request.method == 'POST':
        json_data = request.json
        analyzer = KeyStrokeAnalyzer()

        template_data = load_template_json('backend/tem_data/haoyu wang_key_events_sessions.json')
        tem_scores = []
        for data in template_data:
            tem_features = analyzer.feature_extracting(data)
            cleaned_tem_features = analyzer.feature_cleaning(tem_features)
            # print(f'{cleaned_tem_features}')
            tem_scores.append(analyzer.score_computing(cleaned_tem_features))

        threshold = np.median(tem_scores)
            
        subject_data = analyzer.load_json(json_data)
        features = analyzer.feature_extracting(subject_data)
        cleaned_features = analyzer.feature_cleaning(features)
        score = analyzer.score_computing(cleaned_features)
        print(f'{score}')

        result = False
        if score <= (0.85 * threshold) and score >= (1.15 * threshold):
            result = True
        else:
            result = False

        return jsonify(result)
    elif request.method == 'GET':
        analyzer = KeyStrokeAnalyzer()

        template_data = load_template_json('backend/tem_data/haoyu wang_key_events_sessions.json')
        tem_scores = []
        for data in template_data:
            tem_features = analyzer.feature_extracting(data)
            cleaned_tem_features = analyzer.feature_cleaning(tem_features)
            # print(f'{cleaned_tem_features}')
            tem_scores.append(analyzer.score_computing(cleaned_tem_features))

        threshold = np.median(tem_scores)
        return jsonify(threshold)

model = load('backend/model1204.joblib')
def load_template_json(json_path):
    with open (json_path, 'r') as file:
        key_sequences = json.load(file)
        keystroke_dynamic = []

        for i, key_sequence in enumerate(key_sequences):
            keys = []
            keystrokes = key_sequence['data']

            for keystroke in keystrokes:
                events = {
                    'key' : keystroke['key'],
                    'event' : keystroke['type'],
                    'timestamp' : keystroke['time']
                }
                keys.append(events)
            keystroke_dynamic.append(keys)
    return keystroke_dynamic
class KeyStrokeAnalyzer:
    def __init__(self) -> None:
        pass
    def load_json(self, json_data):
        # print(f'{json_data}')
        keystrokes = []
        key_data = json_data['keystrokes']
        # print(f'{key_data}')
        for keys in key_data:
            events = {
                'key' : keys['key'],
                'event' : keys['type'],
                'timestamp' : keys['time']
            }
            keystrokes.append(events)
        return keystrokes
    def feature_computing(self, i, keystrokes):
        key = keystrokes[i]['key'].lower()
        time = keystrokes[i]['timestamp']
        release_time = 0
        next_press = 0
        next_release = 0
        next_press_key = None

        for j in range(i+1, len(keystrokes)):
            if keystrokes[j]['key'].lower() == key and keystrokes[j]['event'] == 'keyup' and release_time == 0:
                release_time = keystrokes[j]['timestamp']
            elif keystrokes[j]['event'] == 'keydown' and next_press == 0 and next_press_key is None:
                next_press = keystrokes[j]['timestamp']
                next_press_key = keystrokes[j]['key'].lower()
            elif keystrokes[j]['event'] == 'keyup' and keystrokes[j]['key'].lower() == next_press_key and next_release == 0:
                next_release = keystrokes[j]['timestamp']
            else:
                continue

        HL = release_time - time
        PL = next_press - time
        IL = next_press - release_time
        RL = next_release - release_time

        return HL, PL, IL, RL
    def get_keycode(self, key):
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
    def feature_extracting(self, keystrokes):
        featureVectors = []
        for i, keystroke in enumerate(keystrokes):
            key = keystroke['key']
            event = keystroke['event']
            if event == 'keydown':
                HL, PL, IL, RL = self.feature_computing(i, keystrokes)
                # feature = [self.get_keycode(key), HL, PL, IL, RL]
                feature = [HL, PL, IL, RL]
                featureVectors.append(feature)
            else:
                continue
        return featureVectors
    def feature_cleaning(self, feature_sequence):
        cleaned_features = [[float(i) for i in features] for features in feature_sequence[:-1] if features[0] != None]
        if cleaned_features:
            return cleaned_features
        else:
            return None
    def score_computing(self, cleaned_features):
        cleaned_features_np = np.array(cleaned_features)

        log_likelihood = model.score(cleaned_features_np)
        score = log_likelihood
        # mean = sum(i for i in score) / len(score)
        return score

if __name__ == '__main__' :
    app.run(debug=True)