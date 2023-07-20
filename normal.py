import numpy as np
import scipy.signal as signal

# .complexファイルのパス
file_path = "/Users/moomin/Downloads/test/complex/HackRF-2_4GHz.complex16s"

# .complexファイルの読み込み
data = np.fromfile(file_path, dtype=np.complex64)
print("data1 value:", data)

# 無効な値を除外
data = data[np.isfinite(data)]
print("data2 value:", data)
print("data length:", len(data))

is_real = np.isreal(data)  # データの要素が実数かどうかを判定
is_complex = np.iscomplex(data)  # データの要素が複素数かどうかを判定

print("Real data:", data[is_real])  # 実数データのみ表示
print("Complex data:", data[is_complex])  # 複素数データのみ表示

# データのスケーリング（例: ノーマライズ）
max_value = np.max(np.abs(data))
print("Max value:", max_value)

if max_value == 0:
    normalized_data = data  # データの最大値が0の場合はそのまま使用
else:
    normalized_data = data / max_value

# サンプリングレートの設定
sampling_rate = 1000000  # 1M (1MHz)

# バンドパスフィルタを適用
low_freq = 2400e6 - 0.75e6  # フィルタの下限周波数（Hz）= 2.4GHz - 0.75MHz
high_freq = 2400e6 + 0.75e6  # フィルタの上限周波数（Hz）= 2.4GHz + 0.75MHz

# 正規化周波数の計算
low_normalized = low_freq / sampling_rate
high_normalized = high_freq / sampling_rate

print("low_normalized:", low_normalized)
print("high_normalized:", high_normalized)

# バンドパスフィルタの設計
nyquist_freq = sampling_rate / 2
low_normalized = low_normalized / nyquist_freq
high_normalized = high_normalized / nyquist_freq
# バンドパスフィルタの設計
order = 2  # フィルタの次数を指定

b, a = signal.butter(order, [low_normalized, high_normalized], btype='band')


# フィルタ適用
filtered_data = signal.lfilter(b, a, normalized_data)
print("filtered_data:", filtered_data)

# デモジュレータを適用
carrier_freq = 2400e6  # キャリア周波数（Hz）= 2.4GHz
t = np.arange(len(filtered_data)) / sampling_rate
carrier_signal = np.exp(1j * 2 * np.pi * carrier_freq * t)
demodulated_data = filtered_data * np.conj(carrier_signal)

# デモジュレータ後の信号をスケーリング
demodulated_data_max = np.max(np.abs(demodulated_data))
demodulated_data_normalized = demodulated_data / demodulated_data_max

# RMS正規化を適用
rms_value = np.sqrt(np.mean(demodulated_data_normalized**2))
preprocessed_data = demodulated_data_normalized / rms_value

# 前処理後のデータを使用して何かしらの処理を行う...
# 例: スペクトル解析、フィルタリング、周波数解析など

# 前処理後のデータを別のファイルに保存する場合
output_file_path = "/Users/moomin/Downloads/test/complex/processed_data.npy"
np.save(output_file_path, preprocessed_data)

# 読み込んだデータを表示してみる
loaded_data = np.load(output_file_path)
print("Loaded data:", loaded_data)
