"""
Finite-state machine for detecting squat phases.

This module defines SquatFSM, an FSM that tracks the phases of a squat
movement (START → DESCENDING → BOTTOM → ASCENDING → START). Transitions
are determined using knee and hip angles, as well as knee velocity,
compared against configurable threshold values. The FSM updates each
frame to identify when the user begins descending, reaches the bottom,
or returns to standing, enabling accurate rep detection and form checks.
"""

from .fsm_base import FiniteStateMachine
from .states import PhaseName

class SquatFSM(FiniteStateMachine):
    def __init__(self, th):
        super().__init__(initial=PhaseName.START)
        self.th = th
        self._build()

    def _build(self):
        th = self.th
        self.add_transition(
            PhaseName.START, PhaseName.DESCENDING,
            lambda f, c: f["knee_angle_avg"] < th["stand_knee"] and f["knee_vel_avg"] < -th["vel_eps"]
        )
        self.add_transition(
            PhaseName.DESCENDING, PhaseName.BOTTOM,
            lambda f, c: f["knee_angle_avg"] <= th["bottom_knee"] and abs(f["knee_vel_avg"]) <= th["vel_eps"]
        )
        # Escape hatch: if we miss the exact "bottom pause" frame (e.g., dropped frames),
        # allow switching to ASCENDING once velocity flips positive near the bottom.
        self.add_transition(
            PhaseName.DESCENDING, PhaseName.ASCENDING,
            lambda f, c: f["knee_vel_avg"] > th["vel_eps"] and f["knee_angle_avg"] <= (th["bottom_knee"] + 12)
        )
        self.add_transition(
            PhaseName.BOTTOM, PhaseName.ASCENDING,
            lambda f, c: f["knee_vel_avg"] > th["vel_eps"]
        )
        self.add_transition(
            PhaseName.ASCENDING, PhaseName.START,
            lambda f, c: f["knee_angle_avg"] >= th["stand_knee"] and f["hip_angle_avg"] >= th["stand_hip"]
        )
