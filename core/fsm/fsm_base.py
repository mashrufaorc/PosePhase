"""
A simple finite-state machine (FSM) used to track exercise phases.

This code defines a generic FSM where each state can transition to another
state when a user-supplied condition function is met. The FSM stores the
current phase, a context dictionary for persistent state, and a set of
transition rules. On each update(features) call, it checks which transition
should fire and moves to the appropriate next phase. This is used to
segment exercises (e.g., pushup → down → up) based on computed features.
"""

from dataclasses import dataclass
from typing import Dict, Callable, Any
from .states import PhaseState, PhaseName

# A condition takes (features, context) and returns True if a transition should trigger
Condition = Callable[[Dict[str, float], Dict[str, Any]], bool]

@dataclass
class Transition:
    to_state: PhaseName        # Next state the FSM should move to
    condition: Condition       # Function that decides when the transition happens

class FiniteStateMachine:
    def __init__(self, initial: PhaseName):
        self.initial = initial
        self.current = PhaseState(initial, pretty=initial.name.title())  
        # Context object for storing mutable state across transitions
        self.ctx: Dict[str, Any] = {}
        # Mapping: current_state → list of possible transitions
        self.transitions: Dict[PhaseName, list[Transition]] = {}

    def reset(self):
        # Reset state and clear internal context
        self.current = PhaseState(self.initial, pretty=self.initial.name.title())
        self.ctx.clear()

    def add_transition(self, from_s, to_s, cond):
        # Add a transition rule from one state to another
        self.transitions.setdefault(from_s, []).append(Transition(to_s, cond))

    def update(self, features):
        # Check all transitions for the current state
        for t in self.transitions.get(self.current.name, []):
            # Trigger transition if condition is satisfied
            if t.condition(features, self.ctx):
                self.current = PhaseState(t.to_state, pretty=t.to_state.name.title())
                break
        return self.current
