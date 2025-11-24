from typing import Dict, Any, List


class FeedbackEngine:
    """
    Generates:
      - ui_text: what appears on the overlay
      - speak_text: what TTS will say (only when changes)
      - warnings: list of warnings
      - score: numeric phase score
    """

    def __init__(self,
                 praise_threshold: float = 0.80,
                 praise_phases: List[str] = None):
        # praise only if score >= threshold and no warnings
        self.praise_threshold = praise_threshold

        self.praise_phases = praise_phases  # None means any phase is ok

        self.praise_lines = [
            "Good form!",
            "Nice rep!",
            "Looking strong!",
            "Great technique!",
            "Excellent movement!"
        ]

    def generate(self,
                 state,
                 phase_score: Dict[str, Any],
                 features: Dict[str, float],
                 rep_count: int) -> Dict[str, Any]:

        warnings = phase_score.get("warnings", []) or []
        score = float(phase_score.get("score", 1.0))

        # -------------------------------
        # Praise selection
        # -------------------------------
        praise_text = ""
        phase_ok = True
        if self.praise_phases is not None:
            phase_ok = state.pretty in self.praise_phases

        if (not warnings) and (score >= self.praise_threshold) and phase_ok:
            praise_text = self.praise_lines[rep_count % len(self.praise_lines)]

        # -------------------------------
        # Speak text priority:
        # warnings > praise > nothing
        # -------------------------------
        speak_text = ""
        if warnings:
            speak_text = warnings[0]
        elif praise_text:
            speak_text = praise_text

        # -------------------------------
        # UI text
        # -------------------------------
        if warnings:
            ui_text = f"Fix: {', '.join(warnings)} | Score {score:.2f}"
        elif praise_text:
            ui_text = f"{praise_text} | Score {score:.2f}"
        else:
            ui_text = f"Score {score:.2f}"

        return {
            "ui_text": ui_text,
            "speak_text": speak_text,
            "warnings": warnings,
            "score": score
        }
