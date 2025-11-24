from dataclasses import dataclass
from typing import Dict, Callable, Any
from .states import PhaseState, PhaseName

Condition = Callable[[Dict[str, float], Dict[str, Any]], bool]

@dataclass
class Transition:
    to_state: PhaseName
    condition: Condition

class FiniteStateMachine:
    def __init__(self, initial: PhaseName):
        self.initial = initial
        self.current = PhaseState(initial, pretty=initial.name.title())
        self.ctx: Dict[str, Any] = {}
        self.transitions: Dict[PhaseName, list[Transition]] = {}

    def reset(self):
        self.current = PhaseState(self.initial, pretty=self.initial.name.title())
        self.ctx.clear()

    def add_transition(self, from_s, to_s, cond):
        self.transitions.setdefault(from_s, []).append(Transition(to_s, cond))

    def update(self, features):
        for t in self.transitions.get(self.current.name, []):
            if t.condition(features, self.ctx):
                self.current = PhaseState(t.to_state, pretty=t.to_state.name.title())
                break
        return self.current
