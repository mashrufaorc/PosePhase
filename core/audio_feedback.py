import time
from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class AudioFeedback:
    """
    Text-to-speech controller.
    Outputs speech only when the feedback text changes.
    Identical messages are not repeated.
    """

    def __init__(self, enabled=True, rate=185, change_gap_s=0.8):
        # Text-to-speech activation state
        self.enabled = enabled and (pyttsx3 is not None)

        # Minimum time gap required between two different spoken messages
        self.change_gap_s = change_gap_s

        # Timestamp and content of the most recently spoken message
        self.last_spoken_time = 0.0
        self.last_spoken_text: Optional[str] = None

        # Initialize TTS engine when available and enabled
        if self.enabled:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
        else:
            self.engine = None

    def set_change_gap(self, seconds: float):
        # Adjust the minimum allowed interval between spoken messages
        self.change_gap_s = seconds

    def speak(self, text: str):
        # Skip when disabled or when there is no provided text
        if not self.enabled or not text:
            return

        now = time.time()

        # Skip if the message is identical to the previously spoken message
        if text == self.last_spoken_text:
            return

        # Skip when the time interval since the last message is too short
        if (now - self.last_spoken_time) < self.change_gap_s:
            return

        # Update internal tracking for speech output
        self.last_spoken_text = text
        self.last_spoken_time = now

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

