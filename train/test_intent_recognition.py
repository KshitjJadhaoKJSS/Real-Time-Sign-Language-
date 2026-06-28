"""
Test intent-based recognition with live camera
हेतू-आधारित ओळख चाचणी
"""
import cv2
import numpy as np
import json
import sys
import os
import time
from tensorflow.keras.models import load_model

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.hand_tracking import HandTracker
from utils.motion_detector import MotionDetector
from utils.state_machine import StateMachine
from utils.intent_mapper import IntentPatternMatcher
from utils.context_manager import ContextManager
from utils.tts import MarathiTTS

class IntentBasedRecognizer:
    """Intent-based MSL recognizer"""
    
    def __init__(self):
        """Initialize recognizer"""
        print("Loading model...")
        self.model = load_model('models/gesture_classifier.h5')
        
        print("Loading labels...")
        with open('models/labels.json', 'r') as f:
            gestures_dict = json.load(f)
        self.labels = [gestures_dict[str(i)] for i in range(len(gestures_dict))]
        
        print("Initializing components...")
        self.hand_tracker = HandTracker()
        self.motion_detector = MotionDetector()
        self.state_machine = StateMachine()
        self.intent_matcher = IntentPatternMatcher()
        self.context_manager = ContextManager()
        self.tts = MarathiTTS()
        
        # Gesture sequence
        self.gesture_sequence = []
        self.sequence_start_time = time.time()
        self.intent_timeout = 5.0
        
        # Output
        self.last_output = ""
        
        print("✓ Ready!")
    
    def predict_gesture(self, landmarks):
        """Predict gesture from landmarks"""
        landmarks = np.array(landmarks).reshape(1, -1)
        
        # Normalize
        mean = landmarks.mean()
        std = landmarks.std()
        if std > 0:
            landmarks = (landmarks - mean) / std
        
        # Predict
        prediction = self.model.predict(landmarks, verbose=0)
        class_idx = np.argmax(prediction)
        confidence = prediction[0][class_idx]
        
        if confidence > 0.8:
            gesture = self.labels[class_idx]
            return gesture, confidence
        
        return None, confidence
    
    def add_to_sequence(self, gesture: str):
        """Add gesture to sequence and try to match intent"""
        # Reset if timeout
        if time.time() - self.sequence_start_time > self.intent_timeout:
            self.gesture_sequence = []
        
        # Add gesture
        if not self.gesture_sequence or gesture != self.gesture_sequence[-1]:
            self.gesture_sequence.append(gesture)
            self.sequence_start_time = time.time()
            
            # Limit sequence length
            if len(self.gesture_sequence) > 5:
                self.gesture_sequence.pop(0)
            
            # Auto-detect context
            detected_ctx = self.context_manager.detect_from_gesture(gesture)
            if detected_ctx != self.context_manager.get_context():
                self.context_manager.set_context(detected_ctx)
            
            # Try to match intent
            self.match_intent()
    
    def match_intent(self):
        """Try to match current sequence to intent"""
        if not self.gesture_sequence:
            return
        
        context = self.context_manager.get_context()
        result = self.intent_matcher.match_intent(self.gesture_sequence, context)
        
        if result:
            intent_name, marathi_output, description = result
            self.last_output = marathi_output
            
            print(f"\n✓ Intent Matched!")
            print(f"  Sequence: {' → '.join(self.gesture_sequence)}")
            print(f"  Intent: {intent_name}")
            print(f"  Output: {marathi_output}")
            print(f"  Context: {self.context_manager.get_display_name()}")
            
            # Clear sequence
            self.gesture_sequence = []
            self.context_manager.refresh()
    
    def run(self):
        """Run intent recognition"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
        print("\n" + "="*60)
        print("हेतू-आधारित MSL ओळख सुरू")
        print("INTENT-BASED MSL RECOGNITION STARTED")
        print("="*60)
        print("\nControls:")
        print("  C - Change Context")
        print("  S - Speak Output")
        print("  R - Reset Sequence")
        print("  Q - Quit")
        print("="*60 + "\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Process frame
            landmarks = self.hand_tracker.process_frame(frame)
            
            if landmarks:
                # Draw hand
                self.hand_tracker.draw_landmarks(frame)
                
                # Detect motion
                is_static = self.motion_detector.is_static(landmarks)
                
                # Update state machine
                prediction = self.state_machine.update(is_static)
                
                # If prediction should be made
                if prediction:
                    gesture, conf = self.predict_gesture(landmarks)
                    
                    if gesture:
                        self.add_to_sequence(gesture)
                        
                        # Draw gesture
                        cv2.putText(frame, f"{gesture} ({conf:.2f})", 
                                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                   0.8, (0, 255, 0), 2)
            
            # Draw UI
            self.draw_ui(frame)
            
            cv2.imshow('Intent-Based MSL Recognition', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.change_context()
            elif key == ord('s'):
                if self.last_output:
                    print(f"\nSpeaking: {self.last_output}")
                    self.tts.speak(self.last_output)
            elif key == ord('r'):
                self.gesture_sequence = []
                print("Sequence reset")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def draw_ui(self, frame):
        """Draw user interface"""
        h, w, _ = frame.shape
        
        # Top panel
        cv2.rectangle(frame, (0, 0), (w, 80), (0, 0, 0), -1)
        cv2.putText(frame, "Intent-Based MSL Recognition", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        context_text = f"Context: {self.context_manager.get_display_name()}"
        cv2.putText(frame, context_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Middle panel - Sequence
        cv2.rectangle(frame, (0, 80), (w, 150), (40, 40, 40), -1)
        
        if self.gesture_sequence:
            seq_text = "Sequence: " + " -> ".join(self.gesture_sequence)
            cv2.putText(frame, seq_text, (10, 115), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        else:
            cv2.putText(frame, "Make gestures...", (10, 115), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        # Bottom panel - Output
        cv2.rectangle(frame, (0, h-100), (w, h), (0, 0, 0), -1)
        
        if self.last_output:
            cv2.putText(frame, "Output:", (10, h-70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
            cv2.putText(frame, self.last_output, (10, h-35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Controls
        cv2.putText(frame, "[C]Context [S]Speak [R]Reset [Q]Quit", 
                   (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def change_context(self):
        """Show context menu"""
        print("\n" + "="*50)
        print("Select Context:")
        print("="*50)
        
        contexts = list(ContextManager.CONTEXTS.items())
        for i, (key, name) in enumerate(contexts, 1):
            print(f"  {i}. {name} ({key})")
        
        try:
            choice = int(input("\nChoice (1-{}): ".format(len(contexts))))
            if 1 <= choice <= len(contexts):
                selected = contexts[choice-1][0]
                self.context_manager.set_context(selected, manual=True)
        except:
            print("Invalid input")

if __name__ == "__main__":
    try:
        recognizer = IntentBasedRecognizer()
        recognizer.run()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()