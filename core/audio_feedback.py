import time
from typing import Optional

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class AudioFeedback:
    """
    Text-to-speech controller.
    Outputs speech with basic rate limiting to avoid spamming.
    Identical messages are allowed to repeat (after the time gap).
    """

    def __init__(self, enabled=True, rate=185, change_gap_s=0.8):
        # Text-to-speech activation state
        self.enabled = enabled and (pyttsx3 is not None)

        # Minimum time gap required between spoken messages
        self.change_gap_s = change_gap_s

        # Timestamp and content of the most recently spoken message
        self.last_spoken_time = 0.0
        self.last_spoken_text: Optional[str] = None

        # TTS engine settings (we intentionally create a fresh engine per call;
        # persistent pyttsx3 engines can stop speaking after the first runAndWait()
        # on some Linux backends).
        self._rate = rate

    def set_change_gap(self, seconds: float):
        # Adjust the minimum allowed interval between spoken messages
        self.change_gap_s = seconds

    def speak(self, text: str, force: bool = False):
        """
        Speak text aloud.

        By default, speech is rate-limited:
          - a minimum time gap is required between spoken messages
          - identical messages are allowed to repeat after the gap

        When force=True, debouncing is bypassed (used for rep-final feedback).
        """
        # Skip when disabled or when there is no provided text
        if not self.enabled or not text:
            return

        now = time.time()

        if not force:
            # Skip when the time interval since the last message is too short
            if (now - self.last_spoken_time) < self.change_gap_s:
                return

        if pyttsx3 is None:
            return

        # One-shot engine per message for reliability.
        try:
            eng = pyttsx3.init()
            eng.setProperty("rate", self._rate)
            eng.say(text)
            eng.runAndWait()
            try:
                eng.stop()
            except Exception:
                pass

            # Only mark as spoken after a successful runAndWait.
            self.last_spoken_text = text
            self.last_spoken_time = time.time()
        except Exception:
            return