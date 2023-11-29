import numpy as np
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
from tslearn.clustering import KShape
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series_dataset

def process_line(line):
    parts = line.strip().split(',')
    sequence = [float(i) for i in parts[:-1]]
    return sequence[-4000:] if len(sequence) >= 4000 else sequence

def load_data(file_name):
    with open(file_name, 'r') as file:
        sequences = Parallel(n_jobs=-1)(delayed(process_line)(line) for line in file)
    return sequences

sequences = load_data('data_file_HYL.txt')
sequences = to_time_series_dataset(sequences)
sequences = TimeSeriesScalerMeanVariance().fit_transform(sequences)

n_clusters = 2
ks = KShape(n_clusters=n_clusters, verbose=True, random_state=0)
y_pred = ks.fit_predict(sequences)

plt.figure()
for yi in range(n_clusters):
    plt.subplot(3, 1, 1 + yi)
    for xx in sequences[y_pred == yi]:
        plt.plot(xx.ravel(), "k-", alpha=.2)
    plt.plot(ks.cluster_centers_[yi].ravel(), "r-")
    plt.xlim(0, 4000)
    plt.ylim(-4, 4)
    plt.title(f"Cluster {yi + 1}")

plt.tight_layout()
plt.show()
