import numpy as np

class MotionDetector:
    def __init__(self, threshold=0.035, min_static_frames=5):
        self.prev_landmarks = None
        self.threshold = threshold
        self.min_static_frames = min_static_frames
        self.static_count = 0

    def is_static(self, landmarks):
        if self.prev_landmarks is None:
            self.prev_landmarks = landmarks
            return False

        diff = np.mean(np.abs(landmarks - self.prev_landmarks))
        self.prev_landmarks = landmarks

        if diff < self.threshold:
            self.static_count += 1
        else:
            self.static_count = 0

        return self.static_count >= self.min_static_frames

    def reset(self):
        self.static_count = 0
