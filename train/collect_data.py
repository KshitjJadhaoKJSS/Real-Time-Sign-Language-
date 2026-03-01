import sys
import os
import cv2
import numpy as np
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.hand_tracking import HandTracker

DATA_DIR = "../data/raw_landmarks"

GESTURES = {
    0: "मला",
    1: "अन्न",
    2: "पाणी",
    3: "हवे",
    4: "आहे",
    5: "धन्यवाद",
    6: "नमस्कार",
    7: "मदत",
    8: "द्या",
    9: "कृपया"
}

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

        landmarks = tracker.get_landmarks(frame)

        if landmarks is not None:
            filename = f"{word}_{collected}.npy"
            filepath = os.path.join(DATA_DIR, word, filename)
            np.save(filepath, landmarks)
            collected += 1

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
