"""
Definitions for exercise phase names and state objects.

This module provides:
  • PhaseName — an enum listing all possible movement phases
    (e.g., START, DESCENDING, BOTTOM, ASCENDING, TOP, RESET).
  • PhaseState — a simple dataclass storing the current phase and an
    optional human-readable label.

These definitions are used by all FSM classes to represent and track the
current stage of an exercise movement.
"""

from dataclasses import dataclass
from enum import Enum, auto

class PhaseName(Enum):
    START = auto()
    DESCENDING = auto()
    BOTTOM = auto()
    ASCENDING = auto()
    TOP = auto()
    RESET = auto()

@dataclass
class PhaseState:
    name: PhaseName
    pretty: str = ""
