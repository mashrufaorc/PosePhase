"""
Tracks the different stages of a lunge using a simple state machine.

This class watches how the knees move over time and decides which part
of a lunge the person is currently in:
  - START: standing upright
  - DESCENDING: moving down into the lunge
  - BOTTOM: lowest position of the lunge
  - ASCENDING: pushing back up to standing

By switching between these stages at the right moments, the system can
count reps and check form in a consistent way.
"""

from .fsm_base import FiniteStateMachine
from .states import PhaseName


class LungeFSM(FiniteStateMachine):
    def __init__(self, th):
        # Start in the standing position
        super().__init__(initial=PhaseName.START)

        # Store threshold values (angle and speed limits)
        self.th = th

        # Build all the rules that control when we change phases
        self._build()

    def _build(self):
        th = self.th

        # START → DESCENDING
        # If the front knee starts bending AND is moving downward,
        # we assume the person has begun a lunge.
        self.add_transition(
            PhaseName.START,
            PhaseName.DESCENDING,
            lambda f, c:
                f["front_knee_angle"] < th["stand_front_knee"] and
                f["front_knee_vel"] < -th["vel_eps"]
        )

        # DESCENDING → BOTTOM
        # If both knees are bent deep enough AND the movement slows down,
        # we assume the person has reached the bottom of the lunge.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.BOTTOM,
            lambda f, c:
                f["front_knee_angle"] <= th["bottom_front_knee"] and
                f["back_knee_angle"] <= th["bottom_back_knee"] and
                abs(f["front_knee_vel"]) <= th["vel_eps"]
        )

        # DESCENDING → ASCENDING (fallback case)
        # Sometimes people don’t go deep enough.
        # If the knee starts straightening again BEFORE reaching the bottom,
        # we move directly to ASCENDING so the system doesn’t get stuck.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.ASCENDING,
            lambda f, c:
                f["front_knee_vel"] > th["vel_eps"] and (
                    f["front_knee_angle"] > th["bottom_front_knee"] or
                    f["back_knee_angle"] > th["bottom_back_knee"]
                )
        )

        # BOTTOM → ASCENDING
        # When the front knee starts straightening,
        # the person is pushing back up.
        self.add_transition(
            PhaseName.BOTTOM,
            PhaseName.ASCENDING,
            lambda f, c:
                f["front_knee_vel"] > th["vel_eps"]
        )

        # ASCENDING → START
        # When both knees are straight again,
        # the person has returned to the standing position.
        self.add_transition(
            PhaseName.ASCENDING,
            PhaseName.START,
            lambda f, c:
                f["front_knee_angle"] >= th["stand_front_knee"] and
                f["back_knee_angle"] >= th["stand_back_knee"]
        )
