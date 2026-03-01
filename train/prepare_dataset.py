import os
import numpy as np
from sklearn.model_selection import train_test_split

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "raw_landmarks")

X = []
y = []

labels = sorted(os.listdir(DATA_DIR))
label_map = {label: idx for idx, label in enumerate(labels)}

for label in labels:
    folder = os.path.join(DATA_DIR, label)

    if not os.path.isdir(folder):
        continue

    for file in os.listdir(folder):

        if not file.endswith(".npy"):
            continue

        path = os.path.join(folder, file)

        data = np.load(path)

        # ensure shape is correct
        if data.shape == (63,):
            X.append(data)
            y.append(label_map[label])
        else:
            print("Skipping invalid shape:", file, data.shape)

X = np.array(X, dtype=np.float32)
y = np.array(y)

print("Dataset prepared")
print("X shape:", X.shape)
print("y shape:", y.shape)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

SAVE_DIR = os.path.join(ROOT_DIR, "data")

np.save(os.path.join(SAVE_DIR, "X_train.npy"), X_train)
np.save(os.path.join(SAVE_DIR, "X_test.npy"), X_test)
np.save(os.path.join(SAVE_DIR, "y_train.npy"), y_train)
np.save(os.path.join(SAVE_DIR, "y_test.npy"), y_test)

print("\nSaved successfully!")
