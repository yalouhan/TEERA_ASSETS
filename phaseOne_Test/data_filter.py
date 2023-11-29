from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import numpy as np

def load_data(file_name):
    sequences = []
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            sequence = [float(i) for i in parts[:-1]]
            sequences.append(sequence)
    return sequences

sequences = load_data('data_file_HYL.txt')

sampling_rate = 8000

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

# 设置滤波器参数
fs = 8000  # 采样率
lowcut_1 = 0
highcut_1 = 150
lowcut_2 = 245
highcut_2 = 410

# 应用滤波器
filtered_data_1 = bandpass_filter(sequences[1], lowcut_1, highcut_1, fs)
filtered_data_2 = bandpass_filter(sequences[1], lowcut_2, highcut_2, fs)

# 可视化滤波后的结果
plt.plot(filtered_data_1)
plt.plot(filtered_data_2)
plt.title('Bandpass Filtered Data')
plt.xlabel('Sample Number')
plt.ylabel('Amplitude')
plt.show()
