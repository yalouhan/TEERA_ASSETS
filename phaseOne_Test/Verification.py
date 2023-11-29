from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
from scipy.interpolate import interp1d
from scipy.signal import butter, sosfiltfilt
from tslearn.metrics import dtw
from scipy.fft import fft
from joblib import load
import numpy as np
from hmmlearn import hmm

seq_length = 4000 + 1

def bandpass_filter(data, fs, bands, order=4):
    sos = np.concatenate([butter(order, band, 'bandpass', fs=fs, output='sos') for band in bands])
    filtered_data = sosfiltfilt(sos, data)
    
    return filtered_data

def load_data(file_name):
    sequences = []
    labels = []
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            sequence = [i for i in parts]
            sequences.append(sequence[:-1])
            labels.append(sequence[-1])

    return sequences, labels

def load_template(file_name):
    with open(file_name, 'r') as file:
        line = file.readline().strip()
        template = [float(i) for i in line.split(',')[:-1]]

    return template

def feature_Ectracting(seqs, tem):
    features = []
    for seq in seqs:
        dtw_d = dtw(seq, tem)
        mean_val = np.mean(seq)
        std_dev = np.std(seq)
        energy = np.sum(np.square(seq))
        spectral_energy = np.sum(np.square(np.abs(fft(seq))))
        zero_crossing = np.sum(np.diff(np.diff(np.sign(seq))!= 0))
        f_vector = [dtw_d, mean_val, std_dev, energy, spectral_energy, zero_crossing]
        features.append(f_vector)
    
    return features

sequences, labels = load_data('data_file_HYL_new.txt')
filtered_sequences = [seq for seq, label in zip(sequences, labels) if label != "False"]

fs = 8000
bands = [(4, 150), (245, 410)]
f_seqs = []
for seq in sequences:
    f_seq = bandpass_filter([float(i) for i in seq], fs, bands)
    f_seqs.append(f_seq)

frames = []
sub_seq_length = 4000
for seq in f_seqs:
    if len(seq) >= sub_seq_length:
        for i in range(0, len(seq), sub_seq_length):
            sub_seq = seq[i:i + sub_seq_length]
            if len(sub_seq) == sub_seq_length:
                frames.append(sub_seq)

s_seqs = frames
print(f'{s_seqs}')
# s_seqs = [[float(i) for i in seq[(-2*seq_length):(-seq_length)]] for seq in f_seqs]

c_sequences = to_time_series_dataset(s_seqs)
new_sequences = TimeSeriesScalerMeanVariance().fit_transform(s_seqs)

template = load_template('template_wave.txt')
# print(f'{template}')

new_features = feature_Ectracting(new_sequences, template)
new_features = np.array(new_features)

model = load('hmm_model.joblib')
predicted_states = model.predict(new_features)
for status, label in zip(predicted_states, labels):
    print(f'{status}, {label}')