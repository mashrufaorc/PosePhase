from dataclasses import dataclass
from typing import Dict, Optional


class EMAFilter:
    """
    Exponential Moving Average (EMA) filter for smoothing a 1D signal.
    Produces a weighted average where recent values have higher influence.
    """
    def __init__(self, alpha=0.3):
        # Smoothing factor; higher values react faster to changes
        self.alpha = alpha

        # Internal filtered state
        self.state: Optional[float] = None

    def update(self, x):
        """
        Update EMA with a new observation x.

        - First observation initializes the state.
        - Subsequent updates blend new and previous values.
        """
        if self.state is None:
            # Initialize filter state with the first value
            self.state = x
        else:
            # EMA update equation
            self.state = self.alpha * x + (1 - self.alpha) * self.state

        return self.state


@dataclass
class Kalman1D:
    """
    Basic 1D Kalman filter for smoothing noisy scalar signals.

    q = process noise (expected system variation)
    r = measurement noise (sensor noise level)
    x = estimated value
    p = error covariance
    k = Kalman gain
    """
    q: float = 0.01
    r: float = 1.0
    x: float = 0.0
    p: float = 1.0
    k: float = 0.0

    def update(self, z):
        """
        Update estimated value based on new measurement z.
        Steps follow the standard Kalman filter equations.
        """
        # Predict future variance
        self.p = self.p + self.q

        # Compute Kalman gain
        self.k = self.p / (self.p + self.r)

        # Update estimate using the gain
        self.x = self.x + self.k * (z - self.x)

        # Update covariance after measurement
        self.p = (1 - self.k) * self.p

        return self.x


class SignalSmoother:
    """
    Smoothing wrapper that applies EMA or Kalman filters
    to every key in a feature dictionary.

    Each key maintains an independent filter.
    """
    def __init__(self, method="ema", alpha=0.3, q=0.01, r=1.0):
        # Method can be "ema" or "kalman"
        self.method = method

        # EMA decay factor
        self.alpha = alpha

        # Kalman filter parameters
        self.q = q
        self.r = r

        # Dictionary of filters, one per feature name
        self.filters: Dict[str, object] = {}

    def update(self, signals: Dict[str, float]) -> Dict[str, float]:
        """
        Smooth all incoming signals.

        For each key:
          - Create a filter if none exists yet.
          - Apply the filter to the incoming value.
        """
        out = {}

        for k, v in signals.items():
            # Do not smooth velocity-like signals.
            # Velocity is already a derived quantity (difference of angles), and smoothing it
            # can suppress peaks and break threshold-based FSM transitions.
            if k.endswith("_vel") or k.endswith("_vel_avg"):
                out[k] = v
                continue

            filt = self.filters.get(k)

            # Create filter on first use
            if filt is None:
                if self.method == "ema":
                    filt = EMAFilter(self.alpha)
                else:
                    filt = Kalman1D(self.q, self.r)
                self.filters[k] = filt

            # Apply smoothing to the value
            out[k] = filt.update(v)

        return out
