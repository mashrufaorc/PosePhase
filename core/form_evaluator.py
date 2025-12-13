from core.fsm.states import PhaseName

class FormEvaluator:
    def __init__(self, exercise, th):
        # Name of the exercise being evaluated (squat, pushup, lunge)
        self.exercise = exercise
        
        # Threshold values used for scoring movement quality
        self.th = th

        # Track phase transitions so we can evaluate depth even when the FSM
        # never reaches a strict "Bottom" threshold (e.g., shallow reps).
        self._prev_phase = None
        self._min_knee = None
        self._min_elbow = None
        self._min_front_knee = None
        self._min_back_knee = None
        self._lunge_rep_scored = False

    def scorePhase(self, state, f):
        # IMPORTANT: _prev_phase must refer to the *previous* frame's phase
        # while scoring the current frame. Update it only at the end.
        phase = getattr(state, "name", None)

        # Update per-exercise min-angle trackers used for "turnaround" checks.
        self._update_minima(phase, f)

        # Route scoring to the exercise-specific method
        if self.exercise == "squat":
            out = self._squat(state, f)
        elif self.exercise == "pushup":
            out = self._pushup(state, f)
        elif self.exercise == "lunge":
            out = self._lunge(state, f)
        else:
            # Default perfect score if exercise type is unrecognized
            out = {"score": 1.0, "warnings": []}

        # Store phase for the next frame's transition checks
        self._prev_phase = phase
        return out

    def _update_minima(self, phase, f):
        """
        Track the minimum angle reached during DESCENDING so we can evaluate
        depth at the direction reversal (DESCENDING -> ASCENDING).
        """
        # Reset trackers when we are clearly in a "top" position.
        #
        # For lunges we sometimes want to score *on* the first START frame
        # after ASCENDING (rep completion). In that case we must NOT clear the
        # stored minima before the scoring logic runs.
        if phase in (PhaseName.START, PhaseName.TOP, PhaseName.RESET):
            if (
                self.exercise == "lunge"
                and (self._prev_phase == PhaseName.ASCENDING)
                and (not self._lunge_rep_scored)
            ):
                return
            self._min_knee = None
            self._min_elbow = None
            self._min_front_knee = None
            self._min_back_knee = None
            self._lunge_rep_scored = False

        # Squat/pushup: minima only during DESCENDING (we score at turnaround).
        if phase == PhaseName.DESCENDING:
            if "knee_angle_avg" in f:
                self._min_knee = f["knee_angle_avg"] if self._min_knee is None else min(self._min_knee, f["knee_angle_avg"])
            if "elbow_angle_avg" in f:
                self._min_elbow = f["elbow_angle_avg"] if self._min_elbow is None else min(self._min_elbow, f["elbow_angle_avg"])

        # Lunge: track minima across the entire active rep (DESCENDING/BOTTOM/ASCENDING).
        # This avoids false warnings caused by early/noisy ASCENDING transitions.
        if self.exercise == "lunge" and phase in (PhaseName.DESCENDING, PhaseName.BOTTOM, PhaseName.ASCENDING):
            if "front_knee_angle" in f:
                self._min_front_knee = f["front_knee_angle"] if self._min_front_knee is None else min(self._min_front_knee, f["front_knee_angle"])
            if "back_knee_angle" in f:
                self._min_back_knee = f["back_knee_angle"] if self._min_back_knee is None else min(self._min_back_knee, f["back_knee_angle"])

    def _is_turnaround_to_ascending(self, state) -> bool:
        phase = getattr(state, "name", None)
        return phase == PhaseName.ASCENDING and self._prev_phase in (PhaseName.DESCENDING, PhaseName.BOTTOM)

    def _is_rep_complete_to_top(self, state) -> bool:
        phase = getattr(state, "name", None)
        return phase in (PhaseName.START, PhaseName.TOP) and self._prev_phase == PhaseName.ASCENDING

    def _squat(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Check knee symmetry error: excessive angle difference left vs right
        if f.get("sym_knee", 0.0) > self.th["sym_knee_max"]:
            warnings.append("Knee alignment uneven")
            score -= 0.3

        # Check squat depth at the turnaround into ASCENDING.
        # This works both for strict "Bottom" reps and shallow reps where the
        # FSM never entered Bottom.
        if self._is_turnaround_to_ascending(state) and (self._min_knee is not None) and (self._min_knee > self.th["bottom_knee_max"]):
            warnings.append("Insufficient squat depth")
            score -= 0.3

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}

    def _pushup(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Check plank-line straightness (shoulder–hip–ankle alignment)
        if f.get("shoulder_hip_ankle_angle_avg", 180.0) < self.th["plank_min"]:
            warnings.append("Body line not straight")
            score -= 0.3

        # Check push-up depth at the turnaround into ASCENDING.
        if self._is_turnaround_to_ascending(state) and (self._min_elbow is not None) and (self._min_elbow > self.th["bottom_elbow_max"]):
            warnings.append("Push-up depth insufficient")
            score -= 0.3

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}

    def _lunge(self, state, f):
        # Initialize full score and an empty list of warnings
        warnings, score = [], 1.0

        # Evaluate lunge depth once per rep, when returning to START after ASCENDING.
        # This prevents false positives on the first ASCENDING frame caused by
        # velocity noise, while still catching genuinely shallow reps.
        if (not self._lunge_rep_scored) and self._is_rep_complete_to_top(state):
            if (self._min_front_knee is not None) and (self._min_front_knee > self.th["bottom_front_knee_max"]):
                warnings.append("Front knee not bending enough")
                score -= 0.3

            if (self._min_back_knee is not None) and (self._min_back_knee > self.th["bottom_back_knee_max"]):
                warnings.append("Back knee not lowering enough")
                score -= 0.3

            self._lunge_rep_scored = True

        # Ensure score does not fall below zero
        return {"score": max(score, 0), "warnings": warnings}