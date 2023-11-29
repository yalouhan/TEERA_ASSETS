from joblib import load
import numpy as np
from hmmlearn import hmm

model = load('hmm_model_fixed.joblib')

false_accepts = 0
total_cases = 0
false_rejections = 0

def calculate_threshold(model, data):
    log_likelihoods = []
    for sequence in data:
        # sequence = np.concatenate([np.array(x) for x in sequence])
        log_likelihood = model.score(sequence)
        log_likelihoods.append(log_likelihood)
    return np.mean(log_likelihoods)

def load_data(file_name):
    data = []
    with open(file_name, 'r') as file:
        sequences = []
        for line in file:
            if line.strip():
                parts = line.strip().split(',')
                features = [float(i.strip()) for i in parts if i.strip()]
                sequences.append(features)
            else:
                data.append(sequences)
                sequences = []

    return data

test_data = load_data('TEST_sequences.txt')
clear_test_data = []
for data_seg in test_data:
    clear_test_data_seg = [[float(i) for i in features] for features in data_seg[:-1]]
    clear_test_data.append(clear_test_data_seg)

legal_data = load_data('legal_sequences.txt')
clear_legal_data = []
for data_seg in legal_data:
    clear_legal_data_seg = [[float(i) for i in features] for features in data_seg[:-1]]
    clear_legal_data.append(clear_legal_data_seg)

data = load_data('Template_sequences.txt')
clear_data = []
for data_seg in test_data:
    clear_data_seg = [[float(i) for i in features] for features in data_seg[:-1]]
    clear_data.append(clear_data_seg)
threshold = calculate_threshold(model, clear_data)
print(f'{threshold}')

# print(f'{len(lengths)}, {len(clear_data)}')
# print(f'{clear_data}')
clear_test_data_np = [np.array(segment) for segment in clear_test_data]

for segment in clear_test_data_np:
    # combined_sequence = np.concatenate(segment)
    log_likelihood_acc = model.score(segment)
    print(f'{log_likelihood_acc}')
    if log_likelihood_acc >= threshold:
        false_accepts += 1
    total_cases += 1
print(f'\n')

clear_legal_data_np = [np.array(segment) for segment in clear_legal_data]
# print(f'{len(clear_legal_data_np)}')
for segment in clear_legal_data_np:
    # combined_sequence = np.concatenate(segment)
    log_likelihood_rej = model.score(segment)
    print(f'{log_likelihood_rej}')
    if log_likelihood_rej <= threshold:
        false_rejections += 1
    total_cases += 1
print(f'\n')

far = false_accepts / total_cases
frr = false_rejections / total_cases
print(f"FAR: {far*100}%\nFRR: {frr*100}%\n")
