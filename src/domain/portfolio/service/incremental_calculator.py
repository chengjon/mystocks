"""Incremental value calculation for portfolio valuation."""

from __future__ import annotations


class IncrementalCalculator:
    """Track a numeric value and its recent incremental changes."""

    def __init__(self, initial_value: float = 0.0):
        self.value = initial_value
        self.history: list[float] = []
        self.max_history = 100

    def add_delta(self, delta: float) -> float:
        self.value += delta
        self.history.append(self.value)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        return self.value

    def set_value(self, value: float) -> float:
        delta = value - self.value
        self.value = value
        self.history.append(value)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        return delta

    def get_value(self) -> float:
        return self.value

    def get_change(self) -> float:
        if len(self.history) < 2:
            return 0.0
        return self.history[-1] - self.history[-2]

    def get_rate_of_change(self, window: int = 5) -> float:
        if len(self.history) < window + 1:
            return 0.0
        return (self.history[-1] - self.history[-window - 1]) / window
