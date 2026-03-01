import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


X = np.load(os.path.join(ROOT_DIR, "data", "processed", "X.npy"))
y = np.load(os.path.join(ROOT_DIR, "data", "processed", "y.npy"))

model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(63,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(set(y)), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    X, y,
    epochs=50,
    batch_size=16,
    validation_split=0.2   # This creates validation data automatically
)

model.fit(X, y, epochs=50, batch_size=16)
model.save(os.path.join(ROOT_DIR, "models", "gesture_classifier.h5"))

# =========================
# ACCURACY GRAPH
# =========================
plt.figure()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(['Train', 'Validation'])
plt.show()

# =========================
# LOSS GRAPH
# =========================
plt.figure()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'])
plt.show()

