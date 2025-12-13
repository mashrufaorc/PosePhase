import time
import threading
import queue
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

        # Store desired speech rate for engine initialization
        self._rate = rate

        # Minimum time gap required between two different spoken messages
        self.change_gap_s = change_gap_s

        # Timestamp and content of the most recently spoken message
        self.last_spoken_time = 0.0
        self.last_spoken_text: Optional[str] = None

        # Non-blocking TTS: run pyttsx3 in a dedicated worker thread
        self._q: Optional["queue.Queue[Optional[str]]"] = None
        self._thread: Optional[threading.Thread] = None
        self._engine = None

        if self.enabled:
            self._q = queue.Queue(maxsize=1)
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def set_change_gap(self, seconds: float):
        # Adjust the minimum allowed interval between spoken messages
        self.change_gap_s = seconds

    def close(self, timeout_s: float = 1.0):
        """
        Stop the TTS worker thread (best-effort).
        Safe to call multiple times.
        """
        if not self.enabled:
            return
        if self._q is None:
            return

        try:
            # Signal shutdown
            self._q.put_nowait(None)
        except queue.Full:
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(None)
            except Exception:
                pass

        if self._thread is not None:
            self._thread.join(timeout=timeout_s)

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

        # Enqueue for background speech (never block the main loop)
        if self._q is None:
            return

        try:
            self._q.put_nowait(text)
        except queue.Full:
            # Drop the older queued message and replace it with the latest
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(text)
            except Exception:
                pass

    def _worker(self):
        """
        Dedicated TTS thread. All pyttsx3 calls occur here to avoid blocking
        the video processing loop and to keep engine use thread-confined.
        """
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
        except Exception:
            # Disable silently if engine initialization fails
            self.enabled = False
            self._engine = None
            return

        assert self._q is not None
        while True:
            try:
                text = self._q.get()
            except Exception:
                continue

            # Shutdown signal
            if text is None:
                break

            if not text:
                continue

            try:
                # Best-effort: stop any ongoing utterance and speak the latest text
                self._engine.stop()
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                # Ignore speech errors to avoid killing the worker thread
                pass

