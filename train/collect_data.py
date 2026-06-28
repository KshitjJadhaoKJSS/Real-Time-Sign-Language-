import sys
import os
import cv2
import numpy as np
import time
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.hand_tracking import HandTracker

DATA_DIR = os.path.join(ROOT_DIR, "data", "raw_landmarks")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

GESTURES = {
    0: "g_one",
    1: "g_two",
    2: "g_buy",
    3: "g_price",
    4: "g_ticket",
    5: "g_mobile",
    6: "g_pune",
    7: "g_mumbai",
    8: "g_when",
    9: "g_water",
    10: "g_help",
    11: "undo"
}

# Save the labels mapping to act as a single source of truth
with open(os.path.join(MODELS_DIR, "labels.json"), "w") as f:
    json.dump(GESTURES, f, indent=4)

SAMPLES_PER_GESTURE = 150

os.makedirs(DATA_DIR, exist_ok=True)

for g in GESTURES.values():
    os.makedirs(os.path.join(DATA_DIR, g), exist_ok=True)

cap = cv2.VideoCapture(0)
tracker = HandTracker()

print("Press ENTER to start each gesture collection")
print("Press Q anytime to skip gesture")

for label, word in GESTURES.items():

    input(f"\nPrepare gesture for '{word}' and press ENTER...")

    collected = 0

    while collected < SAMPLES_PER_GESTURE:

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1) # Mirror display
        landmarks = tracker.get_landmarks(frame)

        if landmarks is not None:
            filename = f"{word}_{collected}.npy"
            filepath = os.path.join(DATA_DIR, word, filename)
            np.save(filepath, landmarks)
            collected += 1
            # Draw landmarks for visual feedback
            tracker.draw_landmarks(frame)

        cv2.putText(
            frame,
            f"{word} {collected}/{SAMPLES_PER_GESTURE}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Collecting Data", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    print(f"Collected {collected} samples for {word}")

cap.release()
cv2.destroyAllWindows()

print("Data collection completed")
