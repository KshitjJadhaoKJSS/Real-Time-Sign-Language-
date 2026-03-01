import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


model_path = os.path.join(ROOT_DIR, "models", "gesture_classifier.h5")
model = tf.keras.models.load_model(model_path)


X_test = np.load(os.path.join(ROOT_DIR, "data", "X_test.npy"))
y_test = np.load(os.path.join(ROOT_DIR, "data", "y_test.npy"))


y_pred_probs = model.predict(X_test)
y_pred = np.argmax(y_pred_probs, axis=1)


accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted")
recall = recall_score(y_test, y_pred, average="weighted")
f1 = f1_score(y_test, y_pred, average="weighted")


print("\n===== MODEL PERFORMANCE =====")
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)


print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
