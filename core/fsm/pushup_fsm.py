"""
Tracks the different stages of a push-up using a simple state machine.

This class breaks a push-up into clear phases:
  - TOP: arms straight at the top position
  - DESCENDING: lowering the body toward the ground
  - BOTTOM: lowest point of the push-up
  - ASCENDING: pushing back up

By watching how the elbows bend and straighten, and whether the body
stays in a straight plank, the system can reliably count reps and
check push-up form.
"""

from .fsm_base import FiniteStateMachine
from .states import PhaseName


class PushupFSM(FiniteStateMachine):
    def __init__(self, th):
        # Start at the top of the push-up (arms straight)
        super().__init__(initial=PhaseName.TOP)

        # Store threshold values (angles and speed limits)
        self.th = th

        # Set up all the phase-change rules
        self._build()

    def _build(self):
        th = self.th

        # TOP → DESCENDING
        # If the elbows start bending AND are moving downward,
        # the person has begun lowering into a push-up.
        self.add_transition(
            PhaseName.TOP,
            PhaseName.DESCENDING,
            lambda f, c:
                f["elbow_angle_avg"] < th["top_elbow"] and
                f["elbow_vel_avg"] < -th["vel_eps"]
        )

        # DESCENDING → BOTTOM 
        # If the elbows are bent enough AND movement slows down,
        # we assume the person has reached the bottom of the push-up.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.BOTTOM,
            lambda f, c:
                f["elbow_angle_avg"] <= th["bottom_elbow"] and
                abs(f["elbow_vel_avg"]) <= th["vel_eps"]
        )

        # DESCENDING → ASCENDING (fallback case)
        # Some people don’t go all the way down.
        # If the elbows start straightening again before reaching
        # the bottom threshold, switch to ASCENDING so we don’t
        # get stuck in the descending phase.
        self.add_transition(
            PhaseName.DESCENDING,
            PhaseName.ASCENDING,
            lambda f, c:
                f["elbow_vel_avg"] > th["vel_eps"] and
                f["elbow_angle_avg"] > th["bottom_elbow"]
        )

        # BOTTOM → ASCENDING 
        # When the elbows start straightening,
        # the person is pushing back up.
        self.add_transition(
            PhaseName.BOTTOM,
            PhaseName.ASCENDING,
            lambda f, c:
                f["elbow_vel_avg"] > th["vel_eps"]
        )

        # ASCENDING → TOP 
        # When the arms are straight again AND the body is in a
        # straight plank line, the push-up is complete.
        self.add_transition(
            PhaseName.ASCENDING,
            PhaseName.TOP,
            lambda f, c:
                f["elbow_angle_avg"] >= th["top_elbow"] and
                f["shoulder_hip_ankle_angle_avg"] >= th["plank_line"]
        )
