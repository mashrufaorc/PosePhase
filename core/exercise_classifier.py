from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ExercisePrediction:
    # Predicted exercise label, confidence score, and diagnostic values
    label: str
    confidence: float
    debug: Dict[str, float]


class ExerciseClassifier:
    def __init__(self, th: Dict[str, float]):
        # Threshold dictionary used for scoring each exercise type
        self.th = th

        # Most recent predicted label
        self.current_label: Optional[str] = None

    def predict(self, f: Dict[str, float]) -> ExercisePrediction:
        th = self.th

        # Extract commonly used feature values with defaults
        trunk     = f.get("shoulder_hip_ankle_angle_avg", 180.0)
        knee_avg  = f.get("knee_angle_avg", 180.0)
        elbow_avg = f.get("elbow_angle_avg", 180.0)
        sym_knee  = f.get("sym_knee", 0.0)

        hip_y      = f.get("hip_y", 0.5)
        shoulder_y = f.get("shoulder_y", 0.4)
        wrist_y    = f.get("wrist_y", 0.6)

        # Push-up score:
        # Combines trunk straightness, wrist position, and elbow extension.
        # Each component is normalized using a ramp function.
        pushup_score = (
            self._ramp(trunk, th["pushup_trunk_min"], 180.0) +
            self._ramp(wrist_y - shoulder_y, th["pushup_wrist_below"], 0.6) +
            self._ramp(th["pushup_top_elbow"] - elbow_avg, 0.0, th["pushup_elbow_flex_range"])
        ) / 3.0

        # Squat score:
        # Uses trunk lean, knee bending depth, and knee symmetry.
        # Each term contributes equally.
        squat_score = (
            self._ramp(th["squat_trunk_max"] - trunk, 0.0, th["squat_trunk_range"]) +
            self._ramp(th["squat_stand_knee"] - knee_avg, 0.0, th["squat_knee_flex_range"]) +
            self._ramp(th["squat_sym_knee_max"] - sym_knee, 0.0, th["squat_sym_knee_max"])
        ) / 3.0

        # Lunge score:
        # Based entirely on the knee asymmetry gap.
        # A larger asymmetry suggests a forward-backward stance.
        lunge_score = self._ramp(sym_knee, th["lunge_asym_min"], th["lunge_asym_max"])

        # Collect all scores
        scores = {
            "pushup": pushup_score,
            "squat": squat_score,
            "lunge": lunge_score
        }

        # Select highest-scoring exercise label
        label = max(scores, key=scores.get)
        conf = scores[label]

        # Diagnostic output for debugging or UI overlays
        debug = {
            "pushup_score": pushup_score,
            "squat_score": squat_score,
            "lunge_score": lunge_score,
            "trunk": trunk,
            "knee_avg": knee_avg,
            "elbow_avg": elbow_avg,
            "sym_knee": sym_knee,
        }

        # Store most recent prediction
        self.current_label = label

        return ExercisePrediction(label, conf, debug)

    def _ramp(self, x, lo, hi):
        """
        Normalizes x into the range [0, 1] using a simple linear ramp.
        Returns:
            0.0 when x <= lo
            1.0 when x >= hi
            linear interpolation when lo < x < hi
        """
        # Invalid bounds produce zero contribution
        if hi <= lo:
            return 0.0

        # Clamp normalized value to [0, 1]
        return max(0.0, min(1.0, (x - lo) / (hi - lo)))
