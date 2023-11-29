import matplotlib.pyplot as plt
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset
import numpy as np

seq_length = 4000 + 1

def load_data(file_name):
    sequences = []
    labels = []  # 用于存储布尔值
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            sequence = [i for i in parts]
            if len(sequence) >= seq_length:
                sequences.append(sequence[(-seq_length):])
                labels.append(sequence[-1])  # 获取布尔值
            else:
                sequences.append(sequence)
                labels.append(sequence[-1])  # 获取布尔值
    return sequences, labels

sequences, labels = load_data('data_file_HYL.txt')
clear_sequences = [[float(i) for i in seq[:-1]] for seq in sequences]
c_sequences = to_time_series_dataset(clear_sequences)

c_sequences = TimeSeriesScalerMeanVariance().fit_transform(c_sequences)

n_clusters = 2
dtw_km = TimeSeriesKMeans(n_clusters=n_clusters, verbose=True, metric="dtw", random_state=0)
y_pred = dtw_km.fit_predict(c_sequences)

# 统计每个聚类中True的数量
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
