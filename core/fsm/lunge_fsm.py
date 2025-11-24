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
        self.add_transition(
            PhaseName.BOTTOM, PhaseName.ASCENDING,
            lambda f, c: f["front_knee_vel"] > th["vel_eps"]
        )
        self.add_transition(
            PhaseName.ASCENDING, PhaseName.START,
            lambda f, c: f["front_knee_angle"] >= th["stand_front_knee"]
                         and f["back_knee_angle"] >= th["stand_back_knee"]
        )
