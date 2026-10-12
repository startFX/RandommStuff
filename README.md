# RandommStuff
A public repository where I put some of my stuff, like coding projects, tests and more.

All Python code in this repository uses Python 3.14.8. You need to use this version, as projects like the MNIST CNN only work with that version of Python.

# Information
## Python Clicker Game
A clicker game with a translatable JSON file, save files and more. Created to experiment with file writing and reading.

## MNIST Handwritten Digits CNN
A Convolutional Neural Network (CNN) that takes images of handwritten numbers and guesses the digit showed in the image, made using Keras and sklearn.

Dataset is from https://www.kaggle.com/datasets/hichamachahboun/mnist-handwritten-digits.

This file requires the following to run:

- Python 3.10 - 3.14
- `keras`
- `scikit-learn`
- `numpy`
- `matplotlib`

All of the above can be installed using `pip install`. However, the file also requires PyTorch to run, which is a little more complicated to install. See https://pytorch.org/get-started/locally/ for installation instructions.

# Individual files
## simple_b64.py
A module that simplifies Base64 encoding with providing two functions, one that encodes a str in Base64 and returns it as a str, another that decodes a str from Base64 and returns it as a str.

## testing.py
Random stuff for testing.
