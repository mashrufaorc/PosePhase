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
        self.add_transition(
            PhaseName.BOTTOM, PhaseName.ASCENDING,
            lambda f, c: f["knee_vel_avg"] > th["vel_eps"]
        )
        self.add_transition(
            PhaseName.ASCENDING, PhaseName.START,
            lambda f, c: f["knee_angle_avg"] >= th["stand_knee"] and f["hip_angle_avg"] >= th["stand_hip"]
        )
