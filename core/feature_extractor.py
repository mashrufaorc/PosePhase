from typing import Dict, List, Any
from utils.geometry import angle_3pt, avg

class FeatureExtractor:
    def __init__(self, history=5):
        # Number of past frames stored to compute simple velocity estimates
        self.history = history

        # Rolling histories for angle-based velocity calculations
        self.knee_hist: List[float] = []
        self.elbow_hist: List[float] = []
        self.front_knee_hist: List[float] = []

    def compute_all(self, lm: Dict[str, Any]) -> Dict[str, float]:
        # Output dictionary containing all computed features
        f = {}

        # Knee and hip angles (left and right)
        knee_l = angle_3pt(lm["left_hip"], lm["left_knee"], lm["left_ankle"])
        knee_r = angle_3pt(lm["right_hip"], lm["right_knee"], lm["right_ankle"])
        hip_l  = angle_3pt(lm["left_shoulder"], lm["left_hip"], lm["left_knee"])
        hip_r  = angle_3pt(lm["right_shoulder"], lm["right_hip"], lm["right_knee"])

        # Store knee angles and average
        f["knee_angle_l"] = knee_l
        f["knee_angle_r"] = knee_r
        f["knee_angle_avg"] = avg(knee_l, knee_r)

        # Store hip angles and average
        f["hip_angle_l"] = hip_l
        f["hip_angle_r"] = hip_r
        f["hip_angle_avg"] = avg(hip_l, hip_r)

        # Symmetry measure between knees (absolute difference)
        f["sym_knee"] = abs(knee_l - knee_r)

        # Elbow angles
        elbow_l = angle_3pt(lm["left_shoulder"], lm["left_elbow"], lm["left_wrist"])
        elbow_r = angle_3pt(lm["right_shoulder"], lm["right_elbow"], lm["right_wrist"])

        f["elbow_angle_l"] = elbow_l
        f["elbow_angle_r"] = elbow_r
        f["elbow_angle_avg"] = avg(elbow_l, elbow_r)

        # Elbow symmetry measure
        f["sym_elbow"] = abs(elbow_l - elbow_r)

        # Full-body alignment angle (plank line)
        line_l = angle_3pt(lm["left_shoulder"], lm["left_hip"], lm["left_ankle"])
        line_r = angle_3pt(lm["right_shoulder"], lm["right_hip"], lm["right_ankle"])

        f["shoulder_hip_ankle_angle_avg"] = avg(line_l, line_r)

        # Velocities for knee and elbow angles
        f["knee_vel_avg"] = self._velocity(self.knee_hist, f["knee_angle_avg"])
        f["elbow_vel_avg"] = self._velocity(self.elbow_hist, f["elbow_angle_avg"])

        # Lunge-specific knee roles:
        # The knee with the smaller angle is treated as "front"
        if knee_l < knee_r:
            front_knee, back_knee = knee_l, knee_r
        else:
            front_knee, back_knee = knee_r, knee_l

        f["front_knee_angle"] = front_knee
        f["back_knee_angle"] = back_knee

        # Front knee velocity estimate
        f["front_knee_vel"] = self._velocity(self.front_knee_hist, front_knee)

        # Vertical (y-axis) positions for major joints
        # Averaged between left and right sides
        f["hip_y"] = avg(lm["left_hip"][1], lm["right_hip"][1])
        f["shoulder_y"] = avg(lm["left_shoulder"][1], lm["right_shoulder"][1])
        f["wrist_y"] = avg(lm["left_wrist"][1], lm["right_wrist"][1])

        return f

    def _velocity(self, hist: List[float], current: float) -> float:
        """
        Computes a simple velocity estimate by subtracting the previous
        stored value from the current value.

        Histories are kept at a fixed maximum length defined by `history`.
        """
        # Add new value to history
        hist.append(current)

        # Maintain history length limit
        if len(hist) > self.history:
            hist.pop(0)

        # If fewer than 2 samples exist, velocity cannot be computed
        if len(hist) < 2:
            return 0.0

        # Velocity = current value minus previous value
        return current - hist[-2]
