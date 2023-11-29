import matplotlib.pyplot as plt
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
import numpy as np
from scipy.signal import butter, sosfiltfilt
import wave


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

sequences, labels = load_data('data_file_HYL.txt')

fs = 8000
bands = [(4, 150), (245, 410)]
f_seqs = []
for seq in sequences:
    f_seq = bandpass_filter([float(i) for i in seq], fs, bands)
    f_seqs.append(f_seq)

clear_sequences = [[float(i) for i in seq[-seq_length:-1]] for seq in f_seqs]
c_sequences = to_time_series_dataset(clear_sequences)

c_sequences = TimeSeriesScalerMeanVariance().fit_transform(c_sequences)

n_clusters = 2
dtw_km = TimeSeriesKMeans(n_clusters=n_clusters, verbose=True, metric="dtw", random_state=0)
y_pred = dtw_km.fit_predict(c_sequences)

with open ('template_wave.txt', 'a') as file:
    for num in dtw_km.cluster_centers_[1].ravel():
        file.write(f"{num},")

true_counts = [0] * n_clusters
for label, cluster_id in zip(labels, y_pred):
    if label == 'True':
        true_counts[cluster_id] += 1

plt.figure()
for yi in range(n_clusters):
    plt.subplot(2, 1, 1 + yi)
    for xx in c_sequences[y_pred == yi]:
        plt.plot(xx.ravel(), "k-", alpha=.2)
    plt.plot(dtw_km.cluster_centers_[yi].ravel(), "r-")
    plt.xlim(0, len(c_sequences[0]))
    plt.ylim(-4, 4)
    plt.title(f"Cluster {yi + 1} (True count: {true_counts[yi]})")

plt.tight_layout()
plt.show()



# def save_to_wave(file_name, audio, fs):
#     with wave.open(file_name, 'w') as wf:
#         wf.setnchannels(1)  # 单声道
#         wf.setsampwidth(4)  # 32位采样
#         wf.setframerate(fs)
#         wf.writeframes(audio.tobytes())

# save_to_wave('output_audio.wav', np.array(sequences[15], dtype=np.float32), fs)

# plt.plot(f_seqs[15])
# plt.title('Bandpass Filtered Data')
# plt.xlabel('Sample Number')
# plt.ylabel('Amplitude')
# plt.show()

