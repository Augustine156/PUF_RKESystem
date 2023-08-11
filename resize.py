import cv2
import matplotlib.pyplot as plt

# 画像の読み込み
img = cv2.imread('1.png')

# 画像のリサイズ
resized_img = cv2.resize(img, dsize=(299, 299))

# 変更後の画像を表示
plt.imshow(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))
plt.axis('off')  # 軸を表示しない
plt.show()

