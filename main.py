import sys
import os
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import time
import json
import customtkinter as ctk

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from utils.hand_tracking import HandTracker
from utils.sentence_builder import SentenceBuilder
from utils.motion_detector import MotionDetector
from utils.tts import MarathiTTS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SignLanguageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Marathi Sign Language Translator")
        self.geometry("1100x700")
        
        # Load backend
        self.model = tf.keras.models.load_model(os.path.join(ROOT_DIR, "models", "gesture_classifier.h5"))
        with open(os.path.join(ROOT_DIR, "models", "labels.json"), "r") as f:
            gestures_dict = json.load(f)
        self.labels = [gestures_dict[str(i)] for i in range(len(gestures_dict))]
        
        self.tracker = HandTracker()
        self.sentence = SentenceBuilder()
        self.motion = MotionDetector()
        self.tts = MarathiTTS()
        
        self.locked = False
        self.cooldown_time = 1.5
        self.last_time = 0
        self.CONF_THRESH = 0.80
        self.active_detection = False
        
        self.cap = cv2.VideoCapture(0)
        
        self.build_ui()
        
        # Start video loop
        self.update_video()
        
    def build_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=400) # Fixed width for right panel
        self.grid_rowconfigure(0, weight=1)
        
        # --- LEFT PANEL (Video) ---
        self.video_frame = ctk.CTkFrame(self, corner_radius=15)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # --- RIGHT PANEL (Controls & Text) ---
        self.control_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E", width=400)
        self.control_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.control_frame.grid_propagate(False) # Stop panel from expanding/moving
        
        # Context Indicator
        self.context_label = ctk.CTkLabel(self.control_frame, text="Context: Daily Routine", 
                                        font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FFAA")
        self.context_label.pack(pady=(20, 0))
        
        # Final Sentence
        self.sentence_label = ctk.CTkLabel(self.control_frame, text="Press 'Start Sentence' to begin", 
                                         font=ctk.CTkFont(family="Nirmala UI", size=36, weight="bold"), 
                                         text_color="#FFFFFF", wraplength=350, justify="center")
        self.sentence_label.pack(expand=True, fill="both", pady=10, padx=20)
        
        # Buttons
        self.btn_start = ctk.CTkButton(self.control_frame, text="Start Sentence", 
                                     fg_color="#28A745", hover_color="#218838",
                                     height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                     command=self.start_sentence)
        self.btn_start.pack(fill="x", padx=30, pady=10)
        
        self.btn_complete = ctk.CTkButton(self.control_frame, text="Sentence Completed", 
                                        fg_color="#007BFF", hover_color="#0069D9",
                                        height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                        command=self.complete_sentence)
        self.btn_complete.pack(fill="x", padx=30, pady=10)
        
        self.btn_speak = ctk.CTkButton(self.control_frame, text="Speak Audio", 
                                     fg_color="#6F42C1", hover_color="#5A32A3",
                                     height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                     command=self.speak_audio)
        self.btn_speak.pack(fill="x", padx=30, pady=10)
        
        self.btn_reset = ctk.CTkButton(self.control_frame, text="Reset Sentence", 
                                     fg_color="#DC3545", hover_color="#C82333",
                                     height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                     command=self.reset_sentence)
        self.btn_reset.pack(fill="x", padx=30, pady=(10, 30))
        
    def start_sentence(self):
        self.sentence.reset()
        self.active_detection = True
        self.update_ui_text()
        
    def complete_sentence(self):
        self.active_detection = False
        
    def speak_audio(self):
        txt = self.sentence.get_sentence()
        if txt and txt != "...":
            self.tts.speak(txt)
            
    def reset_sentence(self):
        self.sentence.reset()
        self.active_detection = False
        self.update_ui_text()
            
    def update_ui_text(self):
        ctx = self.sentence.context_manager.get_display_name()
        sent = self.sentence.get_sentence()
        
        self.context_label.configure(text=f"Context: {ctx}")
        if self.active_detection:
            self.sentence_label.configure(text=sent if sent else "Listening...")
        else:
            self.sentence_label.configure(text=sent if sent else "Press 'Start Sentence' to begin")
        
    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            if self.active_detection:
                landmarks = self.tracker.process_frame(frame)
                if landmarks is not None:
                    self.tracker.draw_landmarks(frame)
                    l_arr = np.array(landmarks).reshape(1, -1)
                    
                    # Normalize
                    mean = l_arr.mean()
                    std = l_arr.std()
                    if std > 0:
                        l_arr = (l_arr - mean) / std
                        
                    preds = self.model.predict(l_arr, verbose=0)[0]
                    conf = np.max(preds)
                    word = self.labels[np.argmax(preds)]
                    
                    static = self.motion.is_static(landmarks)
                    
                    if static and conf > self.CONF_THRESH and not self.locked:
                        self.sentence.add(word)
                        self.last_time = time.time()
                        self.locked = True
                        self.update_ui_text()
                        
                    if self.locked and (time.time() - self.last_time) > self.cooldown_time:
                        self.locked = False
                        
                    # Draw word on frame
                    cv2.putText(frame, f"{word} ({conf:.2f})", 
                               (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0), 2)
            
            # Convert frame for Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            # Resize image to fit label
            w = self.video_label.winfo_width()
            h = self.video_label.winfo_height()
            if w > 10 and h > 10:
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
            
        self.after(10, self.update_video)
        
    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = SignLanguageApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
