### PROGRAM SETUP
import os
os.environ['KERAS_BACKEND'] = 'torch'
# Define backend

import time # for timers
import numpy as np
import matplotlib.pyplot as plt
import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)

plot = True                         # Set to False to skip all figures
keras.utils.set_random_seed(42)     # Random seed for training shuffling, allowing for results to be reproduced

status_updates = [
    "Initializing...",
    "Loading images...",
    "Splitting data (total: {count} samples)...",
    "Normalizing values...",
    "Building CNN model...",
    "Starting training...",
    "Training finished. Evaluating on test set...",
    "Generating result figures...",
    "Done :D"
]

print("") # Spacing :D
### LOADING DATA
print(status_updates[0]) # Initializing
image_size_x, image_size_y = 28, 28
num_classes = 10
data_path = 'data/'

def load_dataset(directory_path):
    x_trainval = np.load(os.path.join(directory_path, 'train_images.npy'))
    y_trainval = np.load(os.path.join(directory_path, 'train_labels.npy'))
    x_test = np.load(os.path.join(directory_path, 'test_images.npy'))
    y_test = np.load(os.path.join(directory_path, 'test_labels.npy'))
    return x_trainval, y_trainval, x_test, y_test

print(status_updates[1]) # Loading images
X_trainval, y_trainval, x_test, y_test = load_dataset(data_path)

print("Train+val images:", X_trainval.shape, X_trainval.dtype)
print("Train+val labels:", y_trainval.shape, y_trainval.dtype)
print("Test images     :", x_test.shape, x_test.dtype)
print("Test labels     :", y_test.shape, y_test.dtype)

print("") # Spacing :D
### SPLITTING DATA
print(status_updates[2].format(count = len(X_trainval))) # Splitting data (total)
x_train, x_val, y_train, y_val = train_test_split(
    X_trainval, y_trainval,
    test_size = 0.1,        # 10% of the 60,000 images are used for validation, the other 54,000 are for training
    stratify = y_trainval,
    random_state = 42       # Random seed
)

print("Training samples  :", len(x_train))      # Training set, to adjust weights
print("Validation samples:", len(x_val))        # Validation set, to monitor generalization and choose design options
print("Test samples      :", len(x_test))       # Test set, to estimate how the model performs at the end

print("") # Spacing :D
### PREPROCESSING
print(status_updates[3]) # Normalizing values

def prepare(images):
    images = images.astype('float32') / 255.0   # Normalize to values between 0.0 and 1.0
    return np.expand_dims(images, axis = -1)    # Convolution layers expect height x width x channels.
    # Our images are grayscale, to there is only one channel.

x_train = prepare(x_train)
x_val = prepare(x_val)
x_test = prepare(x_test)

print("Shape of x_train:", x_train.shape)
print("Value range     :", x_train.min(), "to", x_train.max())

print("") # Spacing :D
### BUILDING CNN
print(status_updates[4]) # Building CNN model

model = keras.models.Sequential([
    keras.layers.Input((image_size_x, image_size_y, 1)),
    keras.layers.Conv2D(32, (3, 3), activation = 'relu'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Conv2D(64, (3, 3), activation = 'relu'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation = 'relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(num_classes, activation = 'softmax')
])

model.summary()

### COMPILING MODEL
model.compile(optimizer = 'adam',
              loss = 'sparse_categorical_crossentropy',
              metrics = ['accuracy'])

print("") # Spacing :D
### TRAINING MODEL
print(status_updates[5]) # Starting training

start_time = time.time()
history = model.fit(x_train, y_train,                   # Training images and labels
                    batch_size = 128,                   # Weights are updated every 128 images, so 54,000/128 = 422 updates per epoch
                    epochs = 10,                        # Epochs are passes over the training set, so the network sees every training image 10 times
                    validation_data = (x_val, y_val),   # Compute loss and accuracy without changing weights
                    verbose = 1)                        # Print progress bar
end_time = time.time()
final_time = end_time - start_time
print("Training took", final_time, "seconds")           # Timer
minutes, remaining_seconds = divmod(final_time, 60)
print(f"Or {int(minutes)} minutes and {remaining_seconds:g} seconds")

print("") # Spacing :D
### EVALUATING MODEL
print(status_updates[6]) # Training finished, evaluating
test_loss, test_acc = model.evaluate(x_test, y_test, verbose = 0)   # Run network on test images and return loss
print(f"Test loss    : {test_loss:.4f}")
print(f"Test accuracy: {test_acc:.4f}")

y_prob = model.predict(x_test, verbose = 0)
y_pred = np.argmax(y_prob, axis = 1)

print("Accuracy score:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, digits = 4))

### VISUALISING RESULTS
if plot:
    print("")  # Spacing :D
    print(status_updates[7]) # Generating result figures

    def plot_learning_curves(history):
        epochs = range(1, len(history.history['loss']) + 1)
        plt.figure(figsize = (10, 4))
        plt.subplot(1, 2, 1)
        plt.plot(epochs, history.history['loss'], 'k-o', label = 'training')
        plt.plot(epochs, history.history['val_loss'], 'k--s', label = 'validation')
        plt.xlabel('Epoch'); plt.ylabel('Loss'); plt.legend()
        plt.subplot(1, 2, 2)
        plt.plot(epochs, history.history['accuracy'], 'k-o', label = 'training')
        plt.plot(epochs, history.history['val_accuracy'], 'k--s', label = 'validation')
        plt.xlabel('Epoch'); plt.ylabel('Accuracy'); plt.legend()
        plt.suptitle("Learning curves")
        plt.tight_layout()
        plt.show()

    def plot_grid_results(x_test, y_test, y_pred, rows = 6, cols = 5):
        num_images = rows * cols
        indices = np.random.choice(len(x_test), num_images, replace = False)
        plt.figure(figsize = (10, 12))
        for i, idx in enumerate(indices):
            plt.subplot(rows, cols, i + 1)
            plt.imshow(x_test[idx].reshape(28, 28), cmap = 'gray_r', vmin = 0, vmax = 1)
            t, p = y_test[idx], y_pred[idx]
            plt.title(f"T: {t} P: {p}" + ("" if t == p else "  X"),
                      fontsize = 9, fontweight = "normal" if t == p else "bold")
            plt.axis('off')
        plt.suptitle("Random test results (T = True, P = predicted)", fontsize = 14)
        plt.tight_layout()
        plt.show()

    def plot_errors(x_test, y_test, y_pred, rows = 3, cols = 5):
        num_to_show = rows * cols
        error_indices = np.where(y_pred != y_test) [0]
        if len(error_indices) == 0:
            print("Status: no errors found in the test set!")
            return
        selected = error_indices[:min(len(error_indices), num_to_show)]
        plt.figure(figsize = (10, 6))
        for i, idx in enumerate(selected):
            plt.subplot(rows, cols, i + 1)
            plt.imshow(x_test[idx].reshape(28, 28), cmap = 'gray_r', vmin = 0, vmax = 1)
            plt.title(f"True:{y_test[idx]} Pred:{y_pred[idx]}", fontsize = 9)
            plt.axis('off')
        plt.suptitle("Misclassified test images", fontsize = 14)
        plt.tight_layout()
        plt.show()

    def plot_confusion_matrix(x_test, y_pred):
        cm = confusion_matrix(x_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix = cm,
                                      display_labels = range(num_classes))
        fig, ax = plt.subplots(figsize = (8, 8))
        disp.plot(ax = ax, cmap = 'Greys', values_format = 'd')
        plt.title("Confusion matrix: predicted vs actual digit")
        plt.show()

    plot_learning_curves(history)
    plot_grid_results(x_test, y_test, y_pred)
    plot_errors(x_test, y_test, y_pred)
    plot_confusion_matrix(y_test, y_pred)

print(status_updates[8]) # Done
