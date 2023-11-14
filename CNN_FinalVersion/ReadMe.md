# Machine Learning Model Training

In our machine learning model training, based on the results of our research paper, we utilized a Conv1D CNN for training. If you want to train your own model using the following code, please execute the .ipynb files in the specified order:

## 1. SignalGeneration.ipynb
- Create signals to expand the dataset.
- When conducting machine learning training, it's crucial to have a substantial and diverse set of LoRa transceivers to transmit signals. This provides enough varied training data when collected using HackRF One. To compensate for insufficient data, this notebook attempts to simulate LoRa-like signals with digital signals (.wav files) that have similarities and variations, aiming to enhance model accuracy during training. Adjusting different parameter values in this notebook will affect the waveform of the signals (verifiable using Universal Radio Hacker).

## 2. SignalPreprocessing.ipynb
- Preprocess the generated signals.
- Before training a machine learning model, it is crucial to preprocess all training data to ensure no errors occur during training. The signal's sampling rate is standardized to two million samples per second, with a time length of 300 milliseconds. Therefore, the `librosa.load()` function converts each digital signal into a matrix of size 1x600,000 during machine learning training. Firstly, stereo .wav files are converted to mono to avoid data conversion errors. Secondly, if the data points in a .wav file are less than 600,000, the missing points are padded with "0" at the end.

## 3. CNN.ipynb
- Train a Convolutional Neural Network (CNN) model using the preprocessed data.
- In this code, a Convolutional Neural Network (CNN) model is trained. The following is a brief introduction to the cells in the .ipynb file:
  1. Due to the insufficient amount of data in our research, we aim to simplify the hyperparameter count to avoid overfitting.
  2. The data is divided into two classes: signals from legitimate users are classified as True Signals, represented by "1", and other signals are False Signals, represented by "2".
  3. All .wav files are read using `librosa.load()` and stored in matrices.
  4. The architecture of the CNN model is based on the research paper with modifications due to data and hardware limitations.
  5. The .ipynb file outputs an .h5 model and other .csv files that record the changes in numerical values during training and the settings of various parameters.

## 4. Modeltransform.ipynb
- Transform the trained model to a format compatible with deployment on a Raspberry Pi.
- Since a Raspberry Pi is used to simulate a physical car and the .h5 model produced by TensorFlow is too large for the Raspberry Pi's hardware, this notebook converts the .h5 file to the .tensorflowlite format for execution.
