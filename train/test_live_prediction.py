import sys
import os
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont
import time
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.hand_tracking import HandTracker
from utils.sentence_builder import SentenceBuilder
from utils.motion_detector import MotionDetector
from utils.tts import MarathiTTS

font_path = os.path.join(ROOT_DIR, "fonts", "NotoSansDevanagari-Regular.ttf")
font = ImageFont.truetype(font_path, 48)

model = tf.keras.models.load_model(
    os.path.join(ROOT_DIR, "models", "gesture_classifier.h5")
)

with open(os.path.join(ROOT_DIR, "models", "labels.json"), "r") as f:
    gestures_dict = json.load(f)
# Reconstruct sorted list by integer key to ensure consistent ordering
labels = [gestures_dict[str(i)] for i in range(len(gestures_dict))]

tracker = HandTracker()
sentence = SentenceBuilder()
motion = MotionDetector()
tts = MarathiTTS()

cap = cv2.VideoCapture(0)

locked = False
cooldown_time = 1.5
last_time = 0
CONF_THRESH = 0.80

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    landmarks = tracker.get_landmarks(frame)

    if landmarks is not None:
        tracker.draw_landmarks(frame)
        landmarks = landmarks.reshape(1, -1)
        preds = model.predict(landmarks, verbose=0)[0]
        conf = np.max(preds)
        word = labels[np.argmax(preds)]

        static = motion.is_static(landmarks)

        if static and conf > CONF_THRESH and not locked:
            sentence.add(word)
            last_time = time.time()
            locked = True

        if locked and (time.time() - last_time) > cooldown_time:
            locked = False

    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)

    draw.text((30, 20), sentence.get_sentence(), font=font, fill=(0, 255, 0))

    frame = np.array(img)
    cv2.imshow("Marathi Sign Language System", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    if key == ord("r"):
        tts.speak(sentence.get_sentence())
        sentence.reset()

cap.release()
cv2.destroyAllWindows()
