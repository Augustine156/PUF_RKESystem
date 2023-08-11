import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense

# データの読み込み
preprocessed_file_path = "preprocessed_data_fft.npy"
data = np.load(preprocessed_file_path)

# クラスラベルの作成
y = np.array([0, 1, 2, 0, 1, 2, ...])  # データポイントに対応するクラスラベルを指定

# データの入力と出力に分割
X = data  # 入力データ (FFT結果)

# データの正規化
X_normalized = (X - X.min()) / (X.max() - X.min())

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

# 以下、以前のコードと同じ処理


# CNNモデルの構築
model = Sequential([
    Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(X_train.shape[1], 1)),
    MaxPooling1D(pool_size=2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(num_classes, activation='softmax')
])

# モデルのコンパイル
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# モデルの訓練
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# モデルの評価
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")

