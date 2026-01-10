import pandas as pd
import sys
import os

sys.path.insert(0, os.getcwd())
from src.indicators.indicator_factory import IndicatorFactory

def test_macd():
    factory = IndicatorFactory()
    data = pd.DataFrame({
        'close': [100 + i for i in range(50)] # Steady uptrend
    }, index=pd.date_range('2024-01-01', periods=50))

    print("\n--- Testing MACD (Batch) ---")
    res = factory.calculate("macd.12.26.9", data)
    print("Columns:", res.columns.tolist())
    print("Latest Values:\n", res.tail(3))

    print("\n--- Testing MACD (Streaming) ---")
    streamer = factory.get_calculator("macd.12.26.9", streaming=True)
    for i in range(10):
        bar = {'close': 150 + i}
        val = streamer.update(bar)
        if i == 9:
            print(f"Tick {i} Result: {val}")

if __name__ == "__main__":
    test_macd()
