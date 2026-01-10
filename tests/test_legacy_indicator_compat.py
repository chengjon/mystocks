import pandas as pd
import pytest
from src.database.indicator_calculator import TechnicalIndicatorCalculator

class TestLegacyCalculatorBackwardCompatibility:
    
    def setup_method(self):
        self.calculator = TechnicalIndicatorCalculator()
        self.data = pd.DataFrame({
            'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            'volume': [100] * 15
        }, index=pd.date_range('2024-01-01', periods=15))

    def test_sma_calculation(self):
        # Calculate SMA(5)
        sma = self.calculator._calculate_sma(self.data['close'], period=5)
        
        # Expected: Mean of 10..14 = 12.0 at index 4
        assert sma.iloc[4] == 12.0
        assert len(sma) == 15

    def test_rsi_calculation(self):
        # Calculate RSI(14)
        # With linear growth, RSI should be 100
        rsi = self.calculator._calculate_rsi(self.data['close'], period=14)
        
        # Legacy implementation fills NaNs with 50, but RSI(14) needs 15 points to output one valid non-NaN usually
        # The legacy code: 
        # delta.where(...).rolling(min_periods=1) <-- starts immediately
        # So it will produce values from the start.
        
        assert len(rsi) == 15
        assert rsi.iloc[-1] > 90 # Should be very high for uptrend

    def test_public_interface(self):
        results = self.calculator.calculate_technical_indicators(self.data)
        assert 'sma' in results
        assert 'rsi' in results
        assert 'macd' in results
