from dataclasses import dataclass
from typing import Dict, Optional

class EMAFilter:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.state: Optional[float] = None

    def update(self, x):
        if self.state is None:
            self.state = x
        else:
            self.state = self.alpha * x + (1 - self.alpha) * self.state
        return self.state

@dataclass
class Kalman1D:
    q: float = 0.01
    r: float = 1.0
    x: float = 0.0
    p: float = 1.0
    k: float = 0.0

    def update(self, z):
        self.p = self.p + self.q
        self.k = self.p / (self.p + self.r)
        self.x = self.x + self.k * (z - self.x)
        self.p = (1 - self.k) * self.p
        return self.x

class SignalSmoother:
    def __init__(self, method="ema", alpha=0.3, q=0.01, r=1.0):
        self.method = method
        self.alpha = alpha
        self.q = q
        self.r = r
        self.filters: Dict[str, object] = {}

    def update(self, signals: Dict[str, float]) -> Dict[str, float]:
        out = {}
        for k, v in signals.items():
            filt = self.filters.get(k)
            if filt is None:
                filt = EMAFilter(self.alpha) if self.method == "ema" else Kalman1D(self.q, self.r)
                self.filters[k] = filt
            out[k] = filt.update(v)
        return out
