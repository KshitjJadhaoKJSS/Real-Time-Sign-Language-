import numpy as np

class MotionDetector:
    def __init__(self, threshold=0.02):
        self.prev_landmarks = None
        self.threshold = threshold

    def is_static(self, landmarks):
        if self.prev_landmarks is None:
            self.prev_landmarks = landmarks
            return False

        diff = np.mean(np.abs(landmarks - self.prev_landmarks))
        self.prev_landmarks = landmarks

        return diff < self.threshold
