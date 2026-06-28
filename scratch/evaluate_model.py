import sys
import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

# Load Data
print("Loading data...")
X = np.load(os.path.join(ROOT_DIR, "data", "processed", "X.npy"))
y = np.load(os.path.join(ROOT_DIR, "data", "processed", "y.npy"))

# Load Labels
with open(os.path.join(ROOT_DIR, "models", "labels.json"), "r") as f:
    gestures_dict = json.load(f)
labels = [gestures_dict[str(i)] for i in range(len(gestures_dict))]

# Split data (using the same logic as training but with a fixed seed for evaluation)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load Model
print("Loading model...")
model = tf.keras.models.load_model(os.path.join(ROOT_DIR, "models", "gesture_classifier.h5"))

# Evaluate
print("Evaluating model...")
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest Accuracy: {accuracy*100:.2f}%")
print(f"Test Loss: {loss:.4f}\n")

# Predict
y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)

# Classification Report
report = classification_report(y_test, y_pred, target_names=labels)
print("Classification Report:")
print(report)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Gesture Recognition Confusion Matrix')
plt.ylabel('Actual Gesture')
plt.xlabel('Predicted Gesture')
plt.xticks(rotation=45)
plt.tight_layout()

# Save
cm_path = os.path.join(ROOT_DIR, "models", "confusion_matrix.png")
plt.savefig(cm_path, dpi=300, bbox_inches='tight')
print(f"Saved confusion matrix to {cm_path}")
