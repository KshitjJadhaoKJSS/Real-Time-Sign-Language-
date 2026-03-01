import sys
import os
import cv2
import numpy as np
import tensorflow as tf
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from utils.hand_tracking import HandTracker
from utils.sentence_builder import SentenceBuilder
from utils.motion_detector import MotionDetector
from utils.tts import MarathiTTS


model = tf.keras.models.load_model(
    os.path.join(ROOT_DIR, "models", "gesture_classifier.h5")
)

data_dir = os.path.join(ROOT_DIR, "data", "raw_landmarks")
labels = sorted([f.strip().lower() for f in os.listdir(data_dir) if not f.startswith(".")])


ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
IMAGE_MAP = {}

for file in os.listdir(ASSETS_DIR):
    name, ext = os.path.splitext(file)
    if ext.lower() in [".jpg", ".jpeg", ".png"]:
        IMAGE_MAP[name.strip().lower()] = file


tracker = HandTracker()
sentence = SentenceBuilder()
motion = MotionDetector()
tts = MarathiTTS()

cap = cv2.VideoCapture(0)

CONF_THRESH = 0.80
COOLDOWN_TIME = 1.5
locked = False
last_time = 0
detection_active = True


root = tk.Tk()
root.title("Marathi Sign Language System")
root.geometry("1350x820")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11), padding=6)
style.configure("TEntry", padding=6)

# ================= LAYOUT =================
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(main_frame, bg="#2b2b2b", width=420)
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

right_frame = tk.Frame(main_frame, bg="#1e1e1e")
right_frame.pack(side="right", fill="both", expand=True)



tk.Label(
    left_frame,
    text="Gesture Library",
    font=("Segoe UI", 20, "bold"),
    fg="white",
    bg="#2b2b2b"
).pack(pady=15)

search_var = tk.StringVar()

search_entry = ttk.Entry(
    left_frame,
    textvariable=search_var,
    font=("Segoe UI", 12),
    width=28
)
search_entry.pack(pady=5)

dropdown_container = tk.Frame(left_frame, bg="#2b2b2b", height=0)
dropdown_container.pack(fill="x")
dropdown_container.pack_propagate(False)

listbox = tk.Listbox(
    dropdown_container,
    font=("Segoe UI", 11),
    height=6,
    activestyle="none",
    bg="#1e1e1e",
    fg="white",
    selectbackground="#00aa88"
)
listbox.pack(fill="both", expand=True)

dropdown_open = False
current_height = 0
max_height = 160

def animate_dropdown(opening=True):
    global current_height, dropdown_open
    step = 20

    if opening:
        if current_height < max_height:
            current_height += step
            dropdown_container.config(height=current_height)
            root.after(8, lambda: animate_dropdown(True))
        else:
            dropdown_open = True
    else:
        if current_height > 0:
            current_height -= step
            dropdown_container.config(height=current_height)
            root.after(8, lambda: animate_dropdown(False))
        else:
            dropdown_open = False

def toggle_dropdown(event=None):
    if dropdown_open:
        animate_dropdown(False)
    else:
        update_list()
        animate_dropdown(True)

def update_list(event=None):
    typed = search_var.get().strip().lower()
    listbox.delete(0, tk.END)
    for word in labels:
        if typed in word:
            listbox.insert(tk.END, word)

search_entry.bind("<Button-1>", toggle_dropdown)
search_entry.bind("<KeyRelease>", update_list)


preview_label = tk.Label(
    left_frame,
    text="Select a gesture",
    font=("Segoe UI", 14, "bold"),
    fg="#00ffcc",
    bg="#2b2b2b"
)
preview_label.pack(pady=10)

gesture_image_label = tk.Label(left_frame, bg="#2b2b2b")
gesture_image_label.pack(pady=10)

def show_gesture(word):
    word = word.strip().lower()

    if word in IMAGE_MAP:
        img_path = os.path.join(ASSETS_DIR, IMAGE_MAP[word])

        img = Image.open(img_path)
        img = img.resize((330, 330))
        img_tk = ImageTk.PhotoImage(img)

        gesture_image_label.imgtk = img_tk
        gesture_image_label.configure(image=img_tk)
        preview_label.config(text=f"Preview: {word}")
    else:
        preview_label.config(text=f"No image mapped for '{word}'")
        gesture_image_label.configure(image="")
        gesture_image_label.imgtk = None

def on_select(event):
    selection = listbox.curselection()
    if selection:
        word = listbox.get(selection[0])
        search_var.set(word)
        show_gesture(word)
        animate_dropdown(False)

listbox.bind("<<ListboxSelect>>", on_select)



video_label = tk.Label(right_frame, bg="#1e1e1e")
video_label.pack(pady=10)

sentence_label = tk.Label(
    right_frame,
    text="",
    font=("Segoe UI", 26),
    fg="#00ff88",
    bg="#1e1e1e"
)
sentence_label.pack(pady=10)

status_label = tk.Label(
    right_frame,
    text="Detecting...",
    font=("Segoe UI", 14),
    fg="yellow",
    bg="#1e1e1e"
)
status_label.pack()

confidence_label = tk.Label(
    right_frame,
    text="",
    font=("Segoe UI", 12),
    fg="cyan",
    bg="#1e1e1e"
)
confidence_label.pack()

btn_frame = tk.Frame(right_frame, bg="#1e1e1e")
btn_frame.pack(pady=15)

def speak_sentence():
    text = sentence.get_sentence()
    if text.strip():
        tts.speak(text)

def complete_sentence():
    global detection_active
    detection_active = False
    status_label.config(text="Sentence Completed.", fg="red")

def start_new_sentence():
    global detection_active
    sentence.reset()
    sentence_label.config(text="")
    detection_active = True
    status_label.config(text="Detecting...", fg="yellow")

ttk.Button(btn_frame, text="Speak", command=speak_sentence).grid(row=0, column=0, padx=10)
ttk.Button(btn_frame, text="Sentence Complete", command=complete_sentence).grid(row=0, column=1, padx=10)
ttk.Button(btn_frame, text="Start New Sentence", command=start_new_sentence).grid(row=0, column=2, padx=10)



def update_frame():
    global locked, last_time

    ret, frame = cap.read()
    if not ret:
        root.after(15, update_frame)
        return

    display_conf = ""

    if detection_active:
        landmarks = tracker.get_landmarks(frame)

        if landmarks is not None:
            static = motion.is_static(landmarks)

            input_landmarks = landmarks.reshape(1, -1)
            preds = model.predict(input_landmarks, verbose=0)[0]

            conf = float(np.max(preds))
            word = labels[np.argmax(preds)]

            display_conf = f"{word} ({conf:.2f})"

            if static and conf > CONF_THRESH and not locked:
                sentence.add(word)
                show_gesture(word)
                last_time = time.time()
                locked = True

            if locked and (time.time() - last_time) > COOLDOWN_TIME:
                locked = False

    sentence_label.config(text=sentence.get_sentence())
    confidence_label.config(text=display_conf)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (750, 500))

    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(15, update_frame)



def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

update_frame()
root.mainloop()
