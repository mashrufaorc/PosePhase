"""
Finite-state machine for detecting lunge phases.

This module defines LungeFSM, a specialized FSM that transitions through the
phases of a lunge movement (START → DESCENDING → BOTTOM → ASCENDING → START).
Transitions are triggered based on knee angles and knee velocities, using
thresholds provided in a configuration dictionary. The FSM updates each frame
to determine whether the user is lowering, at the bottom, or rising from a
lunge, enabling consistent rep detection and form analysis.
"""

from .fsm_base import FiniteStateMachine
from .states import PhaseName

class LungeFSM(FiniteStateMachine):
    def __init__(self, th):
        super().__init__(initial=PhaseName.START)
        self.th = th
        self._build()

    def _build(self):
        th = self.th
        self.add_transition(
            PhaseName.START, PhaseName.DESCENDING,
            lambda f, c: f["front_knee_angle"] < th["stand_front_knee"] and f["front_knee_vel"] < -th["vel_eps"]
        )
        self.add_transition(
            PhaseName.DESCENDING, PhaseName.BOTTOM,
            lambda f, c: f["front_knee_angle"] <= th["bottom_front_knee"]
                         and f["back_knee_angle"] <= th["bottom_back_knee"]
                         and abs(f["front_knee_vel"]) <= th["vel_eps"]
        )
        # Fallback for shallow lunges: if direction reverses (front knee angle increasing)
        # before reaching configured bottom thresholds, don't get stuck in DESCENDING.
        self.add_transition(
            PhaseName.DESCENDING, PhaseName.ASCENDING,
            lambda f, c: f["front_knee_vel"] > th["vel_eps"] and (
                f["front_knee_angle"] > th["bottom_front_knee"] or f["back_knee_angle"] > th["bottom_back_knee"]
            )
        )
        self.add_transition(
            PhaseName.BOTTOM, PhaseName.ASCENDING,
            lambda f, c: f["front_knee_vel"] > th["vel_eps"]
        )
        self.add_transition(
            PhaseName.ASCENDING, PhaseName.START,
            lambda f, c: f["front_knee_angle"] >= th["stand_front_knee"]
                         and f["back_knee_angle"] >= th["stand_back_knee"]
        )
