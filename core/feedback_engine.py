from typing import Dict, Any, List


class FeedbackEngine:
    """
    Creates structured feedback for the UI and TTS system, including:
      - ui_text: text displayed in the on-screen overlay
      - speak_text: text spoken aloud (triggered only when feedback changes)
      - warnings: list of detected movement issues
      - score: numeric score for the current phase
    """

    def __init__(self,
                 praise_threshold: float = 0.80,
                 praise_phases: List[str] = None):

        # Minimum score required before praise is allowed.
        # Praise also requires zero warnings.
        self.praise_threshold = praise_threshold

        # Optional list of valid phases where praise is permitted.
        # None = praise allowed in any phase.
        self.praise_phases = praise_phases

        # List of predefined praise messages, cycled by repetition count.
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

        # Extract warnings and score from phase_score dictionary.
        warnings = phase_score.get("warnings", []) or []
        score = float(phase_score.get("score", 1.0))

        # Praise selection
        praise_text = ""

        # Determine whether praise is allowed in the current movement phase.
        phase_ok = True
        if self.praise_phases is not None:
            phase_ok = state.pretty in self.praise_phases

        # Praise conditions:
        #   - no warnings present
        #   - score meets or exceeds praise threshold
        #   - current phase is allowed for praise
        if (not warnings) and (score >= self.praise_threshold) and phase_ok:
            # Cycle through praise lines based on repetition count
            praise_text = self.praise_lines[rep_count % len(self.praise_lines)]
            
        # Speak-text priority:
        # warnings > praise > no audio
        speak_text = ""
        if warnings:
            # Use the first warning as spoken feedback
            speak_text = warnings[0]
        elif praise_text:
            speak_text = praise_text

        # UI text construction
        if warnings:
            # Display warnings first when any appear
            ui_text = f"Fix: {', '.join(warnings)} | Score {score:.2f}"
        elif praise_text:
            # Display praise message when applicable
            ui_text = f"{praise_text} | Score {score:.2f}"
        else:
            # Default UI text when no warnings or praise conditions are met
            ui_text = f"Score {score:.2f}"

        return {
            "ui_text": ui_text,
            "speak_text": speak_text,
            "warnings": warnings,
            "score": score
        }
