import tkinter as tk
from tkinter import filedialog, ttk
import threading
from exercise_modules.squat_analyser import SquatAnalyser
from exercise_modules.pushup_analyser import PushupAnalyser
from exercise_modules.pullup_analyser import PullupAnalyser

EXERCISES = ['Squat', 'Push-up', 'Pull-up']

class ExerciseAnalyserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Analysis")
        self.root.geometry("350x200")
        self.exercise_var = tk.StringVar(value=EXERCISES[0])
        self.label = tk.Label(root, text="Choose Exercise and Input:")
        self.label.pack(pady=10)
        self.combo = ttk.Combobox(root, textvariable=self.exercise_var, values=EXERCISES)
        self.combo.pack(pady=5)
        self.webcam_button = tk.Button(root, text="Webcam", command=self.start_webcam_analysis)
        self.webcam_button.pack(pady=5)
        self.video_button = tk.Button(root, text="Video File", command=self.choose_video_file)
        self.video_button.pack(pady=5)

    def start_webcam_analysis(self):
        exercise = self.exercise_var.get()
        analyser = self.get_analyser(0, exercise)
        threading.Thread(target=analyser.process_frame, daemon=True).start()

    def choose_video_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            exercise = self.exercise_var.get()
            analyser = self.get_analyser(1, exercise, file_path)
            threading.Thread(target=analyser.process_frame, daemon=True).start()

    def get_analyser(self, mode, exercise, file_path=None):
        if exercise == "Squat":
            return SquatAnalyser(mode, file_path)
        elif exercise == "Push-up":
            return PushupAnalyser(mode, file_path)
        elif exercise == "Pull-up":
            return PullupAnalyser(mode, file_path)
        else:
            raise ValueError("Invalid exercise selected")
