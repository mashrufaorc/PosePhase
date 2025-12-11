class FormEvaluator:
    def __init__(self, exercise, th):
        # Name of the exercise being evaluated (squat, pushup, lunge)
        self.exercise = exercise
        
        # Threshold values used for scoring movement quality
        self.th = th

    def scorePhase(self, state, f):
        # Route scoring to the exercise-specific method
        if self.exercise == "squat":
            return self._squat(state, f)
        if self.exercise == "pushup":
            return self._pushup(state, f)
        if self.exercise == "lunge":
            return self._lunge(state, f)

        # Default perfect score if exercise type is unrecognized
        return {"score": 1.0, "warnings": []}

    def _squat(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Check knee symmetry error: excessive angle difference left vs right
        if f["sym_knee"] > self.th["sym_knee_max"]:
            warnings.append("Knee alignment uneven")
            score -= 0.2

        # Check squat depth only at the bottom phase
        if state.pretty == "Bottom" and f["knee_angle_avg"] > self.th["bottom_knee_max"]:
            warnings.append("Insufficient squat depth")
            score -= 0.3

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}

    def _pushup(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Check plank-line straightness (shoulder–hip–ankle alignment)
        if f["shoulder_hip_ankle_angle_avg"] < self.th["plank_min"]:
            warnings.append("Body line not straight")
            score -= 0.3

        # Check push-up depth only at the bottom phase
        if state.pretty == "Bottom" and f["elbow_angle_avg"] > self.th["bottom_elbow_max"]:
            warnings.append("Push-up depth insufficient")
            score -= 0.3

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}

    def _lunge(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Evaluate depth only at the bottom of the lunge
        if state.pretty == "Bottom":

            # Check front knee depth
            if f["front_knee_angle"] > self.th["bottom_front_knee_max"]:
                warnings.append("Front knee not bending enough")
                score -= 0.25

            # Check back knee depth
            if f["back_knee_angle"] > self.th["bottom_back_knee_max"]:
                warnings.append("Back knee not lowering enough")
                score -= 0.25

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}
