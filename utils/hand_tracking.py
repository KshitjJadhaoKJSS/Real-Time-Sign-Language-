import mediapipe as mp
import cv2
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.last_results = None

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.last_results = self.hands.process(rgb)
        
        if self.last_results.multi_hand_landmarks:
            landmarks = self.last_results.multi_hand_landmarks[0].landmark
            return self._normalize_landmarks(landmarks)
        return None

    def get_landmarks(self, frame):
        return self.process_frame(frame)

    def draw_landmarks(self, frame):
        if self.last_results and self.last_results.multi_hand_landmarks:
            for hand_landmarks in self.last_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    def _normalize_landmarks(self, landmarks):
        # Extract wrist coordinates
        wrist_x = landmarks[0].x
        wrist_y = landmarks[0].y
        wrist_z = landmarks[0].z

        # Calculate relative coordinates
        rel_landmarks = []
        for lm in landmarks:
            rel_landmarks.append([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
            
        rel_landmarks = np.array(rel_landmarks)
        
        # Calculate maximum Euclidean distance to normalize scale
        max_dist = np.max(np.linalg.norm(rel_landmarks, axis=1))
        
        if max_dist > 0:
            rel_landmarks = rel_landmarks / max_dist
            
        return rel_landmarks.flatten()
