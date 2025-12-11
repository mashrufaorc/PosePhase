from core.fsm.states import PhaseName

class RepCounter:
    def __init__(self):
        # Total number of completed repetitions
        self.rep_count = 0
        
        # Previously observed phase/state
        self.prev = None

    def reset(self):
        # Reset repetition count and previously observed state
        self.rep_count = 0
        self.prev = None

    def update(self, state):
        # On the first update call, no prior state exists,
        # so record the current state and return the current count.
        if self.prev is None:
            self.prev = state.name
            return self.rep_count

        # A repetition is counted when:
        #   - The prior phase was ASCENDING (movement traveling upward)
        #   - The new phase is START or TOP (movement reached the top position)
        #
        # This transition pattern indicates completion of a full repetition.
        if self.prev == PhaseName.ASCENDING and state.name in (PhaseName.START, PhaseName.TOP):
            self.rep_count += 1

        # Store the current phase for the next comparison cycle
        self.prev = state.name

        # Return the updated repetition count
        return self.rep_count
