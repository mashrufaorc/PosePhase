"""
Tracks the different stages of a squat using a simple state machine.

This class splits a squat into easy-to-understand phases:
  - START: standing upright
  - DESCENDING: moving down into the squat
  - BOTTOM: lowest position of the squat
  - ASCENDING: standing back up

By watching how the knees and hips bend and straighten, and how fast
they move, the system can accurately detect reps and check squat form.
"""

from .fsm_base import FiniteStateMachine
from .states import PhaseName


class SquatFSM(FiniteStateMachine):
    def __init__(self, th):
        # Start in the standing position
        super().__init__(initial=PhaseName.START)

        # Store threshold values (angles and speed limits)
        self.th = th

        # Define all rules for switching between squat phases
        self._build()

    def _build(self):
        th = self.th

        # START → DESCENDING 
        # If the knees begin to bend AND are moving downward,
        # the person has started a squat.
        self.add_transition(
            PhaseName.START,
            PhaseName.DESCENDING,
            lambda f, c:
                f["knee_angle_avg"] < th["stand_knee"] and
                f["knee_vel_avg"] < -th["vel_eps"]
        )

        # DESCENDING → BOTTOM
        # If the knees are bent deep enough AND movement slows down,
        # we assume the person has reached the bottom of the squat.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.BOTTOM,
            lambda f, c:
                f["knee_angle_avg"] <= th["bottom_knee"] and
                abs(f["knee_vel_avg"]) <= th["vel_eps"]
        )

        # DESCENDING → ASCENDING (fallback case)
        # Some people do shallow squats and turn around early.
        # If the knees start straightening before reaching the
        # bottom threshold, switch to ASCENDING so the system
        # does not get stuck in the DESCENDING phase.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.ASCENDING,
            lambda f, c:
                f["knee_vel_avg"] > th["vel_eps"] and
                f["knee_angle_avg"] > th["bottom_knee"]
        )

        # BOTTOM → ASCENDING 
        # When the knees start straightening,
        # the person is pushing back up.
        self.add_transition(
            PhaseName.BOTTOM,
            PhaseName.ASCENDING,
            lambda f, c:
                f["knee_vel_avg"] > th["vel_eps"]
        )

        # ASCENDING → START 
        # When both knees and hips are straight again,
        # the squat repetition is complete.
        self.add_transition(
            PhaseName.ASCENDING,
            PhaseName.START,
            lambda f, c:
                f["knee_angle_avg"] >= th["stand_knee"] and
                f["hip_angle_avg"] >= th["stand_hip"]
        )
