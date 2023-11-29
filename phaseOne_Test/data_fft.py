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
fft_result = np.fft.fft(sequences[15])
frequencies = np.fft.fftfreq(len(sequences[15]), 1/sampling_rate)

half_length = len(fft_result) // 2

positive_frequencies = frequencies[:half_length]
positive_fft_result = fft_result[:half_length]

plt.plot(positive_frequencies, np.abs(positive_fft_result))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Frequency Spectrum')
plt.show()