from typing import Dict, Any, Union
import pandas as pd
from src.indicators.base import BatchIndicator, StreamingIndicator
from src.indicators.implementations.trend.ema import EMAIndicator

class MACDIndicator(BatchIndicator, StreamingIndicator):
    """
    MACD Implementation using nested EMA components.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        params = config.get('parameters', {})
        self.fast_p = params.get('fast_period', 12)
        self.slow_p = params.get('slow_period', 26)
        self.signal_p = params.get('signal_period', 9)
        
        # Components for Streaming
        self.fast_ema = EMAIndicator({'parameters': {'period': {'default': self.fast_p}}})
        self.slow_ema = EMAIndicator({'parameters': {'period': {'default': self.slow_p}}})
        self.signal_ema = EMAIndicator({'parameters': {'period': {'default': self.signal_p}}})

    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        col = self.config.get('required_columns', ['close'])[0]
        close = data[col]
        
        fast = close.ewm(span=self.fast_p, adjust=False).mean()
        slow = close.ewm(span=self.slow_p, adjust=False).mean()
        
        macd = fast - slow
        signal = macd.ewm(span=self.signal_p, adjust=False).mean()
        hist = macd - signal
        
        return pd.DataFrame({
            'macd': macd,
            'signal': signal,
            'hist': hist
        }, index=data.index)

    def update(self, bar: Dict[str, float]) -> Dict[str, float]:
        f_val = self.fast_ema.update(bar)
        s_val = self.slow_ema.update(bar)
        
        macd = f_val - s_val
        sig = self.signal_ema.update({'close': macd}) # Feed macd into signal EMA
        hist = macd - sig
        
        return {'macd': macd, 'signal': sig, 'hist': hist}

    def snapshot(self) -> Dict[str, Any]:
        return {
            'fast': self.fast_ema.snapshot(),
            'slow': self.slow_ema.snapshot(),
            'signal': self.signal_ema.snapshot()
        }

    def load_snapshot(self, state: Dict[str, Any]):
        self.fast_ema.load_snapshot(state['fast'])
        self.slow_ema.load_snapshot(state['slow'])
        self.signal_ema.load_snapshot(state['signal'])
