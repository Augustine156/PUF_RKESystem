When doing the Machine Learning, you should the follwing code at certain order:

1. SignalGeneration.ipynb
2. SignalPreprocessing.ipynb
3. CNN.ipynb
4. modeltransform.ipynb

First, create signal expanding our dataset.
Second, do the signal preprocessing.
Next, use the data to train CNN model.
Finally, transform the model.h5 to model.tflite. In this way, the model can be used on Raspberry Pi.
