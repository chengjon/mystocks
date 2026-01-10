from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from src.indicators.base import BatchIndicator, StreamingIndicator

class EMAIndicator(BatchIndicator, StreamingIndicator):
    """
    Exponential Moving Average (EMA) Implementation.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        params = config.get('parameters', {})
        self.period = params.get('period', {}).get('default', 12)
        self.alpha = 2.0 / (self.period + 1)
        
        # Streaming State
        self._current_ema = float('nan')
        self._initialized = False

    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        period = kwargs.get('period', self.period)
        col = self.config.get('required_columns', ['close'])[0]
        return data[col].ewm(span=period, adjust=False).mean()

    def update(self, bar: Dict[str, float]) -> float:
        col = self.config.get('required_columns', ['close'])[0]
        price = bar.get(col)
        if price is None: return float('nan')

        if not self._initialized:
            self._current_ema = price
            self._initialized = True
            return price
            
        self._current_ema = (price - self._current_ema) * self.alpha + self._current_ema
        return self._current_ema

    def snapshot(self) -> Dict[str, Any]:
        return {'ema': self._current_ema, 'initialized': self._initialized}

    def load_snapshot(self, state: Dict[str, Any]):
        self._current_ema = state.get('ema', float('nan'))
        self._initialized = state.get('initialized', False)
