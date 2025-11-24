from core.fsm.states import PhaseName

class RepCounter:
    def __init__(self):
        self.rep_count = 0
        self.prev = None

    def reset(self):
        self.rep_count = 0
        self.prev = None

    def update(self, state):
        if self.prev is None:
            self.prev = state.name
            return self.rep_count

        if self.prev == PhaseName.ASCENDING and state.name in (PhaseName.START, PhaseName.TOP):
            self.rep_count += 1

        self.prev = state.name
        return self.rep_count
