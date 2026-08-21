"""State containers for the evolution kernel. Plain data, no simulation
logic -- integrators.py fills these in."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class EvolutionState:
    """A single (time, value) sample."""
    t: float
    y: np.ndarray


@dataclass
class Trajectory:
    """The full recorded history of a numerical time evolution."""
    times: list[float]
    states: list[np.ndarray]
    method: str
    rhs_name: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.times) != len(self.states):
            raise ValueError(
                f"times and states must have the same length "
                f"(got {len(self.times)} times, {len(self.states)} states)")
        if len(self.times) == 0:
            raise ValueError("a Trajectory must contain at least one recorded state")

    @property
    def y0(self) -> np.ndarray:
        return self.states[0]

    @property
    def n_recorded(self) -> int:
        return len(self.times)

    def initial(self) -> EvolutionState:
        return EvolutionState(self.times[0], self.states[0])

    def final(self) -> EvolutionState:
        return EvolutionState(self.times[-1], self.states[-1])

    def at_step(self, i: int) -> EvolutionState:
        return EvolutionState(self.times[i], self.states[i])

    def nearest(self, t: float) -> EvolutionState:
        """The recorded sample whose time is closest to `t`."""
        idx = min(range(len(self.times)), key=lambda i: abs(self.times[i] - t))
        return EvolutionState(self.times[idx], self.states[idx])

    def as_array(self) -> np.ndarray:
        """Stacks every recorded state into one (n_recorded, *state_shape) array."""
        return np.stack(self.states)
