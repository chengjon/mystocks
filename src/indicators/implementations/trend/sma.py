from typing import Dict, Any, Deque
from collections import deque
import pandas as pd
import numpy as np

from src.indicators.base import BatchIndicator, StreamingIndicator


class SMAIndicator(BatchIndicator, StreamingIndicator):
    """
    Simple Moving Average Implementation.
    Supports both Batch (Pandas) and Streaming (Deque) modes.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Default parameter extraction
        params = config.get("parameters", {})
        self.period = params.get("period", {}).get("default", 5)

        # Streaming State
        self._buffer: Deque[float] = deque(maxlen=self.period)
        self._initialized = False

    # ----------------------------------------------------------------
    # Batch Interface
    # ----------------------------------------------------------------
    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        Vectorized calculation using Pandas.
        """
        # Allow overriding period at runtime
        period = kwargs.get("period", self.period)
        col = self.config.get("required_columns", ["close"])[0]

        if col not in data.columns:
            raise ValueError(f"Column '{col}' missing from data")

        return data[col].rolling(window=period).mean()

    # ----------------------------------------------------------------
    # Streaming Interface
    # ----------------------------------------------------------------
    def update(self, bar: Dict[str, float]) -> float:
        """
        O(1) Streaming Update.
        """
        col = self.config.get("required_columns", ["close"])[0]
        price = bar.get(col)

        if price is None:
            return float("nan")

        self._buffer.append(price)

        if len(self._buffer) < self._buffer.maxlen:
            return float("nan")

        return sum(self._buffer) / len(self._buffer)

    def snapshot(self) -> Dict[str, Any]:
        return {"buffer": list(self._buffer), "period": self.period}

    def load_snapshot(self, state: Dict[str, Any]):
        self.period = state.get("period", self.period)
        self._buffer = deque(state.get("buffer", []), maxlen=self.period)
