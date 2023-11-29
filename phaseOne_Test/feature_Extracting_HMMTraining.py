from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
from scipy.interpolate import interp1d
from scipy.signal import butter, sosfiltfilt
from tslearn.metrics import dtw
from scipy.fft import fft
from joblib import dump
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

def interpolate_sequence(seq, target_length):
    original_indices = np.linspace(0, 1, len(seq))
    new_indices = np.linspace(0, 1, target_length)
    interpolator = interp1d(original_indices, seq, kind='linear')
    new_seq = interpolator(new_indices)
    return new_seq

sequences, labels = load_data('data_file_HYL.txt')
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
# s_seqs = [[float(i) for i in seq[-seq_length:-1]] for seq in f_seqs]

c_sequences = to_time_series_dataset(s_seqs)
c_sequences = TimeSeriesScalerMeanVariance().fit_transform(s_seqs)

template = load_template('template_wave.txt')
# print(f'{template}')

features = feature_Ectracting(c_sequences, template)

features = np.array(features)


model = hmm.GaussianHMM(n_components=3, n_iter=500)
model.fit(features)
p = model.predict_proba(features)
dump(model, 'hmm_model.joblib')
print(f'Training Finished!, {p}')