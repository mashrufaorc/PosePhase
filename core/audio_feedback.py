import time
from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class AudioFeedback:
    """
    Speaks only when feedback text CHANGES.
    - Same text will never be repeated.
    """
    def __init__(self, enabled=True, rate=185, change_gap_s=0.8):
        self.enabled = enabled and (pyttsx3 is not None)
        self.change_gap_s = change_gap_s

        self.last_spoken_time = 0.0
        self.last_spoken_text: Optional[str] = None

        if self.enabled:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
        else:
            self.engine = None

    def set_change_gap(self, seconds: float):
        self.change_gap_s = seconds

    def speak(self, text: str):
        if not self.enabled or not text:
            return

        now = time.time()

        # only speak if it's a NEW message
        if text == self.last_spoken_text:
            return

        # enforce a small gap between DIFFERENT messages
        if (now - self.last_spoken_time) < self.change_gap_s:
            return

        self.last_spoken_text = text
        self.last_spoken_time = now

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass
