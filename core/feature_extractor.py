from typing import Dict, List, Any
from utils.geometry import angle_3pt, avg

class FeatureExtractor:
    def __init__(self, history=5):
        self.history = history
        self.knee_hist: List[float] = []
        self.elbow_hist: List[float] = []
        self.front_knee_hist: List[float] = []

    def compute_all(self, lm: Dict[str, Any]) -> Dict[str, float]:
        f = {}

        knee_l = angle_3pt(lm["left_hip"], lm["left_knee"], lm["left_ankle"])
        knee_r = angle_3pt(lm["right_hip"], lm["right_knee"], lm["right_ankle"])
        hip_l  = angle_3pt(lm["left_shoulder"], lm["left_hip"], lm["left_knee"])
        hip_r  = angle_3pt(lm["right_shoulder"], lm["right_hip"], lm["right_knee"])

        f["knee_angle_l"] = knee_l
        f["knee_angle_r"] = knee_r
        f["knee_angle_avg"] = avg(knee_l, knee_r)

        f["hip_angle_l"] = hip_l
        f["hip_angle_r"] = hip_r
        f["hip_angle_avg"] = avg(hip_l, hip_r)

        f["sym_knee"] = abs(knee_l - knee_r)

        elbow_l = angle_3pt(lm["left_shoulder"], lm["left_elbow"], lm["left_wrist"])
        elbow_r = angle_3pt(lm["right_shoulder"], lm["right_elbow"], lm["right_wrist"])
        f["elbow_angle_l"] = elbow_l
        f["elbow_angle_r"] = elbow_r
        f["elbow_angle_avg"] = avg(elbow_l, elbow_r)
        f["sym_elbow"] = abs(elbow_l - elbow_r)

        line_l = angle_3pt(lm["left_shoulder"], lm["left_hip"], lm["left_ankle"])
        line_r = angle_3pt(lm["right_shoulder"], lm["right_hip"], lm["right_ankle"])
        f["shoulder_hip_ankle_angle_avg"] = avg(line_l, line_r)

        f["knee_vel_avg"] = self._velocity(self.knee_hist, f["knee_angle_avg"])
        f["elbow_vel_avg"] = self._velocity(self.elbow_hist, f["elbow_angle_avg"])

        if knee_l < knee_r:
            front_knee, back_knee = knee_l, knee_r
        else:
            front_knee, back_knee = knee_r, knee_l

        f["front_knee_angle"] = front_knee
        f["back_knee_angle"] = back_knee
        f["front_knee_vel"] = self._velocity(self.front_knee_hist, front_knee)

        f["hip_y"] = avg(lm["left_hip"][1], lm["right_hip"][1])
        f["shoulder_y"] = avg(lm["left_shoulder"][1], lm["right_shoulder"][1])
        f["wrist_y"] = avg(lm["left_wrist"][1], lm["right_wrist"][1])

        return f

    def _velocity(self, hist: List[float], current: float) -> float:
        hist.append(current)
        if len(hist) > self.history:
            hist.pop(0)
        if len(hist) < 2:
            return 0.0
        return current - hist[-2]
