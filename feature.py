import numpy as np
import scipy.signal as signal
from scipy.fft import fft

# 前処理後のデータの読み込み
file_path = "/Users/moomin/Downloads/test/complex/processed_data.npy"
loaded_data = np.load(file_path)
print(loaded_data)

# プリアンブルの長さ（例：1000サンプル）
preamble_length = 1000

# プリアンブルを取得
preamble = loaded_data[:preamble_length]

# フーリエ変換を適用して周波数スペクトルを得る
frequency_spectrum = np.abs(fft(preamble))

# 特徴1: ピーク周波数を抽出
peak_frequency = np.argmax(frequency_spectrum)

# 特徴2: ピーク周波数と期待される周波数とのオフセットを計算
expected_frequency = 2400e6  # 期待される周波数（例：2.4GHz）
frequency_offset = peak_frequency - expected_frequency

# 特徴3: SNRを計算
signal_power = np.sum(np.abs(preamble) ** 2)  # プリアンブルの信号のパワー
noise_power = np.sum(np.abs(loaded_data[preamble_length:]) ** 2)  # ノイズのパワー（プリアンブル以降のデータ）

if noise_power == 0:
    SNR = float('inf')  # ノイズが0の場合はSNRを無限大として扱う
else:
    SNR = 10 * np.log10(signal_power / (noise_power + 1e-9))  # ノイズのパワーに微小な値を足して0除算を回避



# 特徴4: プリアンブルの統計的特徴
mean_value = np.mean(preamble)
variance = np.var(preamble)
max_value = np.max(preamble)
min_value = np.min(preamble)

# 得られた特徴量をまとめる
features = {
    "peak_frequency": peak_frequency,
    "frequency_offset": frequency_offset,
    "SNR": SNR,
    "mean_value": mean_value,
    "variance": variance,
    "max_value": max_value,
    "min_value": min_value
}

# 機械学習モデルに特徴量を与えて解析を行う...
