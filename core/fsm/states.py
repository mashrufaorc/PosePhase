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
