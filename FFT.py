import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import os

# データフォルダのパス
data_folder = "/home/k2/Desktop/Key_To_Car/Signal"

# データフォルダ内の .complex ファイルを取得
data_files = [file for file in os.listdir(data_folder) if file.endswith(".complex")]

# サンプリング周波数
sampling_rate = 2.5e6  # 例: 2.5 MHz

# FFT結果を格納するリスト
fft_results = []

# データフォルダ内の .complex ファイルを処理
for file in data_files:
    # .complexファイルのパス
    file_path = os.path.join(data_folder, file)
    
    # .complexファイルの読み込み
    data = np.fromfile(file_path, dtype=np.complex64)
    
    # FFTを計算して周波数スペクトルを取得
    fft_result = fft(data)
    
    # FFT結果をリストに追加
    fft_results.append(fft_result)

# FFT結果の最大の長さを取得
max_fft_length = max(len(fft_result) for fft_result in fft_results)

# 各FFT結果の長さを最大の長さに合わせてパディング
padded_fft_results = [np.pad(fft_result, (0, max_fft_length - len(fft_result))) for fft_result in fft_results]

# 周波数軸を生成
freq_axis = np.fft.fftfreq(max_fft_length, d=1/sampling_rate)

# 周波数スペクトルの表示
plt.figure(figsize=(12, 6))
for fft_result in padded_fft_results:
    plt.plot(freq_axis, np.abs(fft_result))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('Frequency Spectrum')
plt.grid()
plt.show()

# プリプロセス後のデータを保存する場合
preprocessed_file_path = "preprocessed_data_fft.npy"
np.save(preprocessed_file_path, padded_fft_results)

