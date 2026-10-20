# RandommStuff
A public repository where I put some of my stuff, like coding projects, tests and more.

All Python code in this repository uses **Python 3.14.8**. You need to use this version - or a version between 3.10 and 3.14 - as projects like the MNIST CNN only work with that version of Python.

No code in this repository is AI-generated. However, for more complex code, **help from LLMs like Claude was used**. By that, I mean I asked it, for some projects, to teach me concepts or debug my code. **I wrote all the code myself**.

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

All modules above can be installed using `pip install`. However, the file also requires **PyTorch** to run, which is a little more complicated to install. To install it, see https://pytorch.org/get-started/locally/ for instructions.

# Individual files
## simple_b64.py
Functions to quickly encode to and decode from Base64. Uses str objects as inputs and outputs str objects directly, rather than going through byte conversion. **Use Python's built-in `help()` function for more info.**

## romaji_kana.py
A module with functions to convert text between romaji, hiragana and katakana (Japanese characters). **Use Python's built-in `help()` function for more info.**

## weight_mean.py
Utility functions for calculating weighted averages. **Use Python's built-in `help()` function for more info.**

## testing.py
Random stuff for testing.
