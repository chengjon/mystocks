import pandas as pd
import numpy as np
import sys
import os

# Add root to path
sys.path.insert(0, os.getcwd())

from src.indicators.indicator_factory import IndicatorFactory

def test_v2_architecture():
    print("--- Starting V2 Indicator System Smoke Test ---")
    
    # 1. Initialize Factory
    try:
        factory = IndicatorFactory()
        print("✅ Factory Initialized")
    except Exception as e:
        print(f"❌ Factory Init Failed: {e}")
        return

    # 2. Test Batch Calculation
    print("\n--- Testing Batch Mode (SMA.5) ---")
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    }, index=pd.date_range('2024-01-01', periods=10))
    
    try:
        result = factory.calculate("sma.5", data)
        print(f"Result Length: {len(result)}")
        print(f"Result Head:\n{result.head(7)}")
        
        # Verify Alignment
        if not result.index.equals(data.index):
            print("❌ Index Alignment Failed!")
        else:
            print("✅ Index Alignment Verified")
            
        # Verify Values (Simple arithmetic: mean of 10,11,12,13,14 = 12.0)
        # result[4] should be 12.0
        expected_val = 12.0
        actual_val = result.iloc[4]
        if abs(actual_val - expected_val) < 0.001:
             print(f"✅ Calculation Correct (Expected {expected_val}, Got {actual_val})")
        else:
             print(f"❌ Calculation Wrong (Expected {expected_val}, Got {actual_val})")

    except Exception as e:
        print(f"❌ Batch Calculation Failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Test Streaming Mode
    print("\n--- Testing Streaming Mode (SMA.5) ---")
    try:
        # Get Streaming Calculator explicitly
        streamer = factory.get_calculator("sma.5", streaming=True)
        print(f"✅ Got Streaming Calculator: {type(streamer)}")
        
        # Simulate feeding bars one by one
        stream_results = []
        for i, row in data.iterrows():
            bar = {'close': row['close']}
            val = streamer.update(bar)
            stream_results.append(val)
            print(f"Update({row['close']}) -> {val}")
            
        # Verify Consistency with Batch
        batch_values = result.fillna(0).values # NaNs are tricky, fill 0 for comparison checks or skip
        
        # Check the 5th value (index 4)
        stream_val_4 = stream_results[4]
        batch_val_4 = result.iloc[4]
        
        if abs(stream_val_4 - batch_val_4) < 0.001:
            print("✅ Streaming vs Batch Consistency Verified")
        else:
            print(f"❌ Consistency Check Failed: Stream={stream_val_4}, Batch={batch_val_4}")

    except Exception as e:
        print(f"❌ Streaming Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v2_architecture()
