import tkinter as tk
from tkinter import filedialog
import traceback
import yaml

from core.session_runner import SessionRunner
from core.video_stream import VideoStream
from core.video_file_stream import VideoFileStream


def load_cfg():
    """
    Load configuration thresholds from YAML file.
    """
    with open("config/thresholds.yaml", "r") as f:
        return yaml.safe_load(f)


# Dark theme color palette for the launcher UI
BG = "#0f1115"
CARD = "#171a21"
TEXT = "#e6e6e6"
MUTED = "#9aa4b2"
ACCENT = "#4da3ff"
ACCENT2 = "#5df0a5"
WARN = "#ffb454"
DANGER = "#ff6b6b"
DISABLED_BG = "#1d2230"
DISABLED_FG = "#6f7785"

# Exercise metadata for buttons and labels
EXERCISE_INFO = {
    "squat":  {"icon": "🏋️", "title": "Squat"},
    "pushup": {"icon": "💪", "title": "Push-Up"},
    "lunge":  {"icon": "🤸", "title": "Lunge"},
}


class PosePhaseLauncher:
    """
    Main Tkinter launcher window for configuring and starting PosePhase sessions.
    Handles:
      - mode selection (webcam vs. video file)
      - exercise selection or auto-detect option
      - video file selection
      - session start, error handling, and summary display
    """
    def __init__(self, root):
        # Root Tkinter window
        self.root = root
        self.root.title("PosePhase")

        # Base window configuration
        self.root.geometry("560x650")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # UI state variables
        self.mode_var = tk.StringVar(value="webcam")   # "webcam" or "video"
        self.exercise_var = tk.StringVar(value="squat")
        self.auto_detect_var = tk.BooleanVar(value=False)
        self.video_path = None

        # Stores exercise button widgets for later refresh
        self.exercise_buttons = []

        # Build all UI widgets
        self._build_ui()

    # UI construction
    def _build_ui(self):
        """
        Build all UI components: header, mode card, exercise card,
        video input card, start button, and footer tip.
        """
        # Header title
        tk.Label(
            self.root, text="PosePhase",
            font=("Segoe UI", 22, "bold"),
            fg=TEXT, bg=BG
        ).pack(pady=(16, 6))

        # Subtitle
        tk.Label(
            self.root,
            text="Real-Time Pose-Based Exercise Coach",
            font=("Segoe UI", 10),
            fg=MUTED, bg=BG
        ).pack(pady=(0, 12))

        # Main container for cards
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True, padx=16)

        # Mode card 
        mode_card = self._card(container, "Mode")
        mode_card.pack(fill="x", pady=6)

        # Webcam radio option
        self._radio(
            mode_card, self.mode_var, "webcam",
            "📷  Webcam (Real-time)",
            self._on_mode_change
        ).pack(anchor="w", padx=12, pady=(8, 2))

        # Video file radio option
        self._radio(
            mode_card, self.mode_var, "video",
            "🎞️  Video File (Offline)",
            self._on_mode_change
        ).pack(anchor="w", padx=12, pady=(2, 8))

        # Exercise card 
        ex_card = self._card(container, "Exercise")
        ex_card.pack(fill="x", pady=6)

        # Auto-detect toggle row
        toggle_row = tk.Frame(ex_card, bg=CARD)
        toggle_row.pack(fill="x", padx=10, pady=(8, 4))

        tk.Checkbutton(
            toggle_row,
            text="🤖 Auto-Detect Exercise",
            variable=self.auto_detect_var,
            command=self._on_auto_toggle,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            activebackground=CARD, activeforeground=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        # Exercise button row
        ex_row = tk.Frame(ex_card, bg=CARD)
        ex_row.pack(fill="x", padx=8, pady=(4, 8))

        # Create a button for each exercise type
        for ex in ["squat", "pushup", "lunge"]:
            info = EXERCISE_INFO[ex]
            btn = self._exercise_button(ex_row, ex, f"{info['icon']}  {info['title']}")
            btn.pack(side="left", expand=True, fill="x", padx=6)
            self.exercise_buttons.append(btn)

        # Video input card
        self.video_card = self._card(container, "Video Input")
        self.video_card.pack(fill="x", pady=6)

        # Button to choose a video file when in "video" mode
        self.video_btn = tk.Button(
            self.video_card,
            text="Choose video file…",
            command=self._choose_video,
            bg=ACCENT, fg="white",
            activebackground="#6bb4ff",
            font=("Segoe UI", 10, "bold"),
            relief="flat", padx=10, pady=6,
            state="disabled"
        )
        self.video_btn.pack(anchor="w", padx=12, pady=(10, 6))

        # Label showing selected video path or placeholder text
        self.video_label = tk.Label(
            self.video_card,
            text="No video selected",
            fg=MUTED, bg=CARD,
            font=("Segoe UI", 9),
            wraplength=500, justify="left"
        )
        self.video_label.pack(anchor="w", padx=12, pady=(0, 10))

        # Start session card 
        start_card = self._card(container, "Start Session")
        start_card.pack(fill="x", pady=(10, 6))
        start_card.pack_propagate(False)
        start_card.configure(height=95)

        # Start button that launches the full PosePhase pipeline
        self.start_btn = tk.Button(
            start_card,
            text="▶  Start",
            bg=ACCENT2, fg="#0b0c0e",
            activebackground="#7af5bb",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=12, pady=10,
            command=self._start_safe
        )
        self.start_btn.pack(fill="x", padx=12, pady=12)

        # Footer tip about the OpenCV window quit key
        tk.Label(
            container,
            text="Tip: Press 'q' to quit the OpenCV window.",
            fg=MUTED, bg=BG, font=("Segoe UI", 9)
        ).pack(pady=(4, 0))

        # Initialize state of exercise buttons based on auto-detect toggle
        self._on_auto_toggle()

    def _card(self, parent, title):
        """
        Helper for creating a card-style frame with a title label.
        """
        frame = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground="#242a35")
        tk.Label(
            frame, text=title,
            bg=CARD, fg=TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=(8, 0))
        return frame

    def _radio(self, parent, var, value, text, cmd=None):
        """
        Helper for creating a styled radio button.
        """
        return tk.Radiobutton(
            parent, text=text,
            variable=var, value=value,
            command=cmd,
            bg=CARD, fg=TEXT, selectcolor=CARD,
            activebackground=CARD, activeforeground=TEXT,
            font=("Segoe UI", 10),
        )

    def _exercise_button(self, parent, ex_value, text):
        """
        Create a button for selecting a single exercise when auto-detect is disabled.
        """
        def set_ex():
            # No change when auto-detect mode is active
            if self.auto_detect_var.get():
                return
            # Update selected exercise value and refresh button appearance
            self.exercise_var.set(ex_value)
            self._refresh_exercise_buttons(parent)

        btn = tk.Button(
            parent, text=text, command=set_ex,
            bg="#202633", fg=TEXT,
            relief="flat", padx=8, pady=10,
            font=("Segoe UI", 10, "bold"),
            activebackground="#2a3345"
        )
        btn.ex_value = ex_value
        self._refresh_exercise_buttons(parent)
        return btn

    def _refresh_exercise_buttons(self, parent):
        """
        Update visual style of exercise buttons to indicate current selection.
        """
        chosen = self.exercise_var.get()
        for child in parent.winfo_children():
            if getattr(child, "ex_value", None) == chosen:
                child.configure(bg=ACCENT, fg="white")
            else:
                child.configure(bg="#202633", fg=TEXT)

    # Toggle
    def _on_auto_toggle(self):
        """
        Enable or disable manual exercise buttons based on auto-detect state.
        """
        auto = self.auto_detect_var.get()

        # Disable buttons when auto-detect is active
        for btn in self.exercise_buttons:
            if auto:
                btn.config(state="disabled", bg=DISABLED_BG, fg=DISABLED_FG)
            else:
                btn.config(state="normal", bg="#202633", fg=TEXT)

        # Ensure selected exercise button is highlighted if manual selection is active
        if not auto and self.exercise_buttons:
            parent = self.exercise_buttons[0].master
            self._refresh_exercise_buttons(parent)

    # Actions
    def _on_mode_change(self):
        """
        Respond to mode changes between webcam and video file.
        Controls availability of the video selection button.
        """
        if self.mode_var.get() == "video":
            self.video_btn.config(state="normal")
        else:
            self.video_btn.config(state="disabled")
            self.video_path = None
            self.video_label.config(text="No video selected", fg=MUTED)

    def _choose_video(self):
        """
        Open a file dialog to select a workout video file.
        Update label with selected path.
        """
        path = filedialog.askopenfilename(
            title="Select workout video",
            filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")]
        )
        if path:
            self.video_path = path
            self.video_label.config(text=path, fg=TEXT)

    def _start_safe(self):
        """
        Wrapper around _start that catches exceptions and shows an error dialog.
        """
        try:
            self._start()
        except Exception:
            err = traceback.format_exc()
            self._toast("Start failed. See error below:\n\n" + err, danger=True)

    def _start(self):
        """
        Launch a PosePhase session based on selected mode and exercise options.
        """
        mode = self.mode_var.get()
        auto = self.auto_detect_var.get()
        exercise = self.exercise_var.get()

        # Load configuration and create a session runner
        cfg = load_cfg()
        runner = SessionRunner(cfg)

        # Update start button to indicate active session
        self.start_btn.config(text="⏳  Running…", state="disabled")
        self.root.update()

        # Determine whether exercise type is fixed or auto-detected
        forced_ex = None if auto else exercise
        summary = None

        if mode == "webcam":
            # Webcam mode: real-time capture
            stream = VideoStream(cam_id=0)
            summary = runner.run(
                stream,
                mode="webcam",
                show_window=True,
                save_summary_path="reports/webcam_summary.json",
                forced_exercise=forced_ex
            )
        else:
            # Video mode requires a selected file path
            if not self.video_path:
                self.start_btn.config(text="▶  Start", state="normal")
                self.root.update()
                self._toast("Please choose a video file first.", danger=True)
                return

            stream = VideoFileStream(self.video_path)
            out_path = f"reports/annotated_{exercise if not auto else 'auto'}.mp4"
            summary = runner.run(
                stream,
                mode="video",
                output_path=out_path,
                show_window=True,
                save_summary_path="reports/video_summary.json",
                forced_exercise=forced_ex
            )

        # Restore start button label and state
        self.start_btn.config(text="▶  Start", state="normal")
        self.root.update()

        # Display results window when a summary is available
        if summary:
            self._show_results(summary)

    # Toast + Results
    def _toast(self, msg, danger=False):
        """
        Display a small modal window with a message and an OK button.
        When danger=True, use error styling.
        """
        win = tk.Toplevel(self.root)
        win.configure(bg=BG)
        win.title("PosePhase")
        win.geometry("520x280")
        win.resizable(False, False)

        tk.Label(
            win, text=("⚠️ " if danger else "ℹ️ ") + msg,
            bg=BG, fg=(DANGER if danger else TEXT),
            font=("Consolas", 9, "bold"),
            wraplength=500, justify="left"
        ).pack(expand=True, padx=12, pady=12)

        tk.Button(
            win, text="OK", command=win.destroy,
            bg=ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=14, pady=6
        ).pack(pady=8)

        # Ensure dialog is modal relative to main window
        win.transient(self.root)
        win.grab_set()

    def _show_results(self, summary: dict):
        """
        Display a session results window with repetitions,
        average score, and warning breakdown.
        """
        win = tk.Toplevel(self.root)
        win.title("Session Results")
        win.geometry("520x420")
        win.resizable(False, False)
        win.configure(bg=BG)

        # Determine exercise info based on summary
        ex = summary.get("exercise", "squat")
        ex_title = EXERCISE_INFO.get(ex, {"icon": "🏋️", "title": ex.title()})

        # Header section
        hdr = tk.Frame(win, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(
            hdr, text=f"{ex_title['icon']}  {ex_title['title']} Results",
            bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            hdr, text="Session summary + breakdown",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w")

        # Main statistics card
        stats = tk.Frame(win, bg=CARD, highlightthickness=1, highlightbackground="#242a35")
        stats.pack(fill="x", padx=16, pady=8)

        rep_count = summary.get("rep_count", 0)
        avg_score = summary.get("avg_score", 0.0)
        warn_count = summary.get("warnings_count", 0)

        self._stat_row(stats, "Repetitions", f"{rep_count}", ACCENT2)
        self._stat_row(stats, "Average Form Score", f"{avg_score:.3f}", ACCENT)
        self._stat_row(stats, "Total Warnings", f"{warn_count}", WARN)

        # Warnings breakdown card
        wb = tk.Frame(win, bg=CARD, highlightthickness=1, highlightbackground="#242a35")
        wb.pack(fill="both", expand=True, padx=16, pady=8)

        tk.Label(
            wb, text="Warnings Breakdown",
            bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 6))

        breakdown = summary.get("warnings_breakdown", {}) or {}
        if not breakdown:
            tk.Label(
                wb, text="✅ No warnings detected. Great form!",
                bg=CARD, fg=ACCENT2, font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", padx=12, pady=8)
        else:
            # List each warning and its frequency, sorted by count
            items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            for w, c in items:
                line = tk.Frame(wb, bg=CARD)
                line.pack(fill="x", padx=12, pady=3)

                tk.Label(
                    line, text=f"• {w}",
                    bg=CARD, fg=TEXT, font=("Segoe UI", 10)
                ).pack(side="left")

                tk.Label(
                    line, text=str(c),
                    bg=CARD, fg=WARN, font=("Segoe UI", 10, "bold")
                ).pack(side="right")

        # Close button for the results window
        tk.Button(
            win, text="Close",
            command=win.destroy,
            bg=ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=14, pady=7
        ).pack(pady=(6, 12))

        win.transient(self.root)
        win.grab_set()

    def _stat_row(self, parent, label, value, color):
        """
        Helper for adding a labeled statistic row to a stats card.
        """
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=10, pady=6)

        tk.Label(
            row, text=label,
            bg=CARD, fg=MUTED, font=("Segoe UI", 10)
        ).pack(side="left")

        tk.Label(
            row, text=value,
            bg=CARD, fg=color, font=("Segoe UI", 12, "bold")
        ).pack(side="right")


if __name__ == "__main__":
    # Create root window and start launcher
    root = tk.Tk()
    PosePhaseLauncher(root)
    root.mainloop()
