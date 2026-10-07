# MNIST Dataset

## Introduction

The MNIST (Modified National Institute of Standards and Technology) dataset is a widely used dataset for training and testing image processing systems. It consists of 70,000 images of handwritten digits (0-9), split into a training set of 60,000 images and a test set of 10,000 images. Each image is 28x28 pixels in size.

## Description

The MNIST dataset includes:

- **Training Images:** 60,000 images of handwritten digits.
- **Training Labels:** Corresponding labels for the training images.
- **Test Images:** 10,000 images of handwritten digits.
- **Test Labels:** Corresponding labels for the test images.

Each image is grayscale and has been size-normalized and centered in a fixed-size image.

## How to Use

First, load the dataset files:

```python
import numpy as np

train_val_images = 'train_images.npy' # Train 80%, Validation 20%
train_val_labels = 'train_labels.npy' # Train 80%, Validation 20%
test_images = 'test_images.npy'
test_labels = 'test_labels.npy'

train_val_images = np.load(train_val_images)
train_val_labels = np.load(train_val_labels)
```

Split the dataset into training, validation, and test sets:

```python
# 90% of the training data for training, 10% for validation
train_images = train_val_images[:int(train_val_images.shape[0] * 0.9)]
train_labels = train_val_labels[:int(train_val_labels.shape[0] * 0.9)]

val_images = train_val_images[int(train_val_images.shape[0] * 0.9):]
val_labels = train_val_labels[int(train_val_labels.shape[0] * 0.9):]

test_images = np.load(test_images)
test_labels = np.load(test_labels)
```

Now, you can use these splits for your machine learning model training and evaluation.

## Acknowledgement

The MNIST dataset was created by Yann LeCun, Corinna Cortes, and Christopher J.C. Burges. It is widely used for benchmarking image processing systems and is publicly available for academic and research purposes. Special thanks to the creators for making this dataset available to the research community.