import os
import numpy as np
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data", "raw_landmarks")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
MODELS_DIR = os.path.join(ROOT_DIR, "models")

os.makedirs(PROCESSED_DIR, exist_ok=True)

X = []
y = []

# Load labels from labels.json
with open(os.path.join(MODELS_DIR, "labels.json"), "r") as f:
    gestures_dict = json.load(f)

# gestures_dict will have string keys "0", "1" etc.
label_map = {word: int(idx) for idx, word in gestures_dict.items()}

for label in label_map.keys():
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

np.save(os.path.join(PROCESSED_DIR, "X.npy"), X)
np.save(os.path.join(PROCESSED_DIR, "y.npy"), y)

print(f"Saved successfully to {PROCESSED_DIR}!")
print("Mapped labels:")
for k, v in label_map.items():
    print(f"{v}: {k}")
