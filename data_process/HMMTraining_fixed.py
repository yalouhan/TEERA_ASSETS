from joblib import dump
import numpy as np
from hmmlearn import hmm

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

data = load_data('Template_sequences.txt')
lengths = []
clear_data = []
for data_seg in data:
    clear_data_seg = [[float(i) for i in features] for features in data_seg[:-1]]
    lengths.append(len(clear_data_seg))
    clear_data.append(clear_data_seg)
# combined_sequence = np.concatenate(clear_data)
# print(f'{len(lengths)}, {len(clear_data)}')
# print(f'{clear_data}')

clear_data_np = [np.array(segment) for segment in clear_data]
model = hmm.GaussianHMM(n_components=4, covariance_type="diag")
for segement in clear_data_np:
    print(f'{segement}')
#     model.fit(segement)
# dump(model, 'hmm_model_fixed.joblib')
# print(f'Training Finished!, {model.transmat_}')

