import tkinter as tk
from PIL import Image, ImageTk
import os


class AppGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Marathi Sign Language System")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f5f5f5")

        # ===== FIXED PATH (IMPORTANT) =====
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.gesture_folder = os.path.join(BASE_DIR, "assets", "gesture_images")

        # ===== VARIABLES =====
        self.current_word = tk.StringVar()
        self.sentence_text = tk.StringVar()
        self.search_text = tk.StringVar()
        self.detection_active = True

        # ================= LEFT SIDE =================
        left_frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Detected Word",
                 font=("Mangal", 20, "bold"),
                 bg="#ffffff").pack(pady=5)

        self.word_label = tk.Label(left_frame,
                                   textvariable=self.current_word,
                                   font=("Mangal", 32),
                                   fg="green",
                                   bg="#ffffff")
        self.word_label.pack(pady=10)

        tk.Label(left_frame, text="Sentence",
                 font=("Mangal", 18, "bold"),
                 bg="#ffffff").pack(pady=5)

        self.sentence_label = tk.Label(left_frame,
                                       textvariable=self.sentence_text,
                                       font=("Mangal", 22),
                                       wraplength=400,
                                       bg="#ffffff")
        self.sentence_label.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(left_frame, bg="#ffffff")
        button_frame.pack(pady=15)

        self.complete_btn = tk.Button(button_frame,
                                      text="Sentence Complete",
                                      command=self.complete_sentence,
                                      bg="#4CAF50",
                                      fg="white",
                                      width=18)
        self.complete_btn.grid(row=0, column=0, padx=10)

        self.toggle_btn = tk.Button(button_frame,
                                    text="Stop Detection",
                                    command=self.toggle_detection,
                                    bg="#f44336",
                                    fg="white",
                                    width=18)
        self.toggle_btn.grid(row=0, column=1, padx=10)

        # ================= RIGHT SIDE =================
        right_frame = tk.Frame(self.root, bg="#eaeaea", padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right_frame, text="Gesture Guide",
                 font=("Arial", 18, "bold"),
                 bg="#eaeaea").pack(pady=5)

        search_entry = tk.Entry(right_frame,
                                textvariable=self.search_text,
                                width=25)
        search_entry.pack(pady=5)
        search_entry.bind("<KeyRelease>", self.filter_words)

        self.word_listbox = tk.Listbox(right_frame, width=25, height=15)
        self.word_listbox.pack(pady=10)
        self.word_listbox.bind("<<ListboxSelect>>", self.show_image)

        self.image_label = tk.Label(right_frame, bg="#eaeaea")
        self.image_label.pack(pady=10)

        self.load_words()

    # ================= LOAD WORDS =================
    def load_words(self):
        self.words = []

        if os.path.exists(self.gesture_folder):
            for file in os.listdir(self.gesture_folder):
                if file.lower().endswith((".jpg", ".png", ".jpeg")):
                    word = os.path.splitext(file)[0]
                    self.words.append(word)

        self.words.sort()

        for word in self.words:
            self.word_listbox.insert(tk.END, word)

    # ================= FILTER WORDS =================
    def filter_words(self, event=None):
        search_term = self.search_text.get().lower()
        self.word_listbox.delete(0, tk.END)

        for word in self.words:
            if search_term in word.lower():
                self.word_listbox.insert(tk.END, word)

    # ================= SHOW IMAGE =================
    def show_image(self, event):
        selection = self.word_listbox.curselection()
        if selection:
            word = self.word_listbox.get(selection[0])

            # Try different extensions
            for ext in [".jpg", ".png", ".jpeg"]:
                image_path = os.path.join(self.gesture_folder, word + ext)
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize((250, 250))
                    photo = ImageTk.PhotoImage(img)

                    self.image_label.config(image=photo)
                    self.image_label.image = photo
                    break

    # ================= UPDATE WORD =================
    def update_word(self, word):
        if self.detection_active:
            self.current_word.set(word)

    # ================= UPDATE SENTENCE =================
    def update_sentence(self, sentence):
        if self.detection_active:
            self.sentence_text.set(sentence)

    # ================= COMPLETE SENTENCE =================
    def complete_sentence(self):
        self.detection_active = False
        self.toggle_btn.config(text="Start Detection",
                               bg="#2196F3")

    # ================= TOGGLE =================
    def toggle_detection(self):
        self.detection_active = not self.detection_active

        if self.detection_active:
            self.toggle_btn.config(text="Stop Detection",
                                   bg="#f44336")
        else:
            self.toggle_btn.config(text="Start Detection",
                                   bg="#2196F3")

    # ================= RUN =================
    def run(self):
        self.root.mainloop()
