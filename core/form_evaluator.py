class FormEvaluator:
    def __init__(self, exercise, th):
        self.exercise = exercise
        self.th = th

    def scorePhase(self, state, f):
        if self.exercise == "squat":
            return self._squat(state, f)
        if self.exercise == "pushup":
            return self._pushup(state, f)
        if self.exercise == "lunge":
            return self._lunge(state, f)
        return {"score": 1.0, "warnings": []}

    def _squat(self, state, f):
        warnings, score = [], 1.0
        if f["sym_knee"] > self.th["sym_knee_max"]:
            warnings.append("Keep knees even")
            score -= 0.2
        if state.pretty == "Bottom" and f["knee_angle_avg"] > self.th["bottom_knee_max"]:
            warnings.append("Go deeper")
            score -= 0.3
        return {"score": max(score, 0), "warnings": warnings}

    def _pushup(self, state, f):
        warnings, score = [], 1.0
        if f["shoulder_hip_ankle_angle_avg"] < self.th["plank_min"]:
            warnings.append("Keep body straight")
            score -= 0.3
        if state.pretty == "Bottom" and f["elbow_angle_avg"] > self.th["bottom_elbow_max"]:
            warnings.append("Lower your chest")
            score -= 0.3
        return {"score": max(score, 0), "warnings": warnings}

    def _lunge(self, state, f):
        warnings, score = [], 1.0
        if state.pretty == "Bottom":
            if f["front_knee_angle"] > self.th["bottom_front_knee_max"]:
                warnings.append("Bend front knee more")
                score -= 0.25
            if f["back_knee_angle"] > self.th["bottom_back_knee_max"]:
                warnings.append("Drop back knee lower")
                score -= 0.25
        return {"score": max(score, 0), "warnings": warnings}
