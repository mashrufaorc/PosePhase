from .fsm_base import FiniteStateMachine
from .states import PhaseName

class PushupFSM(FiniteStateMachine):
    def __init__(self, th):
        super().__init__(initial=PhaseName.TOP)
        self.th = th
        self._build()

    def _build(self):
        th = self.th
        self.add_transition(
            PhaseName.TOP, PhaseName.DESCENDING,
            lambda f, c: f["elbow_angle_avg"] < th["top_elbow"] and f["elbow_vel_avg"] < -th["vel_eps"]
        )
        self.add_transition(
            PhaseName.DESCENDING, PhaseName.BOTTOM,
            lambda f, c: f["elbow_angle_avg"] <= th["bottom_elbow"] and abs(f["elbow_vel_avg"]) <= th["vel_eps"]
        )
        self.add_transition(
            PhaseName.BOTTOM, PhaseName.ASCENDING,
            lambda f, c: f["elbow_vel_avg"] > th["vel_eps"]
        )
        self.add_transition(
            PhaseName.ASCENDING, PhaseName.TOP,
            lambda f, c: f["elbow_angle_avg"] >= th["top_elbow"] and
                         f["shoulder_hip_ankle_angle_avg"] >= th["plank_line"]
        )
