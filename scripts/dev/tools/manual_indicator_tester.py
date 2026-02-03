#!/usr/bin/env python3
"""
Manual Indicator Tester V2.1
CLI Tool for testing and benchmarking indicators.
"""

import argparse
import sys
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from src.indicators.indicator_factory import IndicatorFactory

class IndicatorTester:
    def __init__(self):
        self.factory = IndicatorFactory()

    def generate_dummy_data(self, rows: int = 1000) -> pd.DataFrame:
        """Generate random OHLCV data."""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=rows, freq='min')
        close = np.random.normal(100, 1, rows).cumsum()
        high = close + np.random.random(rows)
        low = close - np.random.random(rows)
        open_ = close + np.random.normal(0, 0.5, rows)
        volume = np.random.randint(100, 10000, rows)
        
        return pd.DataFrame({
            'open': open_,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)

    def run_test(self, indicator_id: str, rows: int = 1000, verbose: bool = False):
        print(f"\n{'='*60}")
        print(f"Testing Indicator: {indicator_id}")
        print(f"{'='*60}")
        
        # 1. Prepare Data
        data = self.generate_dummy_data(rows)
        print(f"Generated {rows} rows of dummy data.")
        
        # 2. Batch Test
        print("\n[1/3] Running Batch Calculation...")
        start_t = time.time()
        try:
            batch_result = self.factory.calculate(indicator_id, data)
            batch_time = (time.time() - start_t) * 1000
            print(f"✅ Batch Success: {batch_time:.2f} ms")
        except Exception as e:
            print(f"❌ Batch Failed: {e}")
            return

        # 3. Streaming Test
        print("\n[2/3] Running Streaming Simulation...")
        try:
            streamer = self.factory.get_calculator(indicator_id, streaming=True)
        except Exception as e:
            print(f"⚠️ Streaming not supported/failed: {e}")
            return

        stream_results = []
        start_t = time.time()
        
        for i, row in data.iterrows():
            # Convert row to dict
            bar = row.to_dict()
            val = streamer.update(bar)
            stream_results.append(val)
            
        stream_total_time = (time.time() - start_t) * 1000
        avg_tick_time = (stream_total_time / rows) * 1000 # microseconds
        print(f"✅ Streaming Success: {stream_total_time:.2f} ms total ({avg_tick_time:.2f} µs/tick)")

        # 4. Consistency Check
        print("\n[3/3] Checking Consistency (Batch vs Streaming)...")
        
        # Align series
        batch_vals = batch_result.fillna(0).values
        stream_vals = np.array([0.0 if np.isnan(x) else x for x in stream_results])
        
        # Calculate Difference
        # Note: Some divergence is expected due to floating point or different init logic
        # We skip the first N rows (warmup)
        warmup = 50 
        if rows > warmup:
            diff = np.abs(batch_vals[warmup:] - stream_vals[warmup:])
            max_diff = np.max(diff)
            mean_diff = np.mean(diff)
            
            print(f"   Max Difference: {max_diff:.6f}")
            print(f"   Mean Difference: {mean_diff:.6f}")
            
            if max_diff < 0.01: # Loose tolerance for now due to Wilder's/EMA init differences
                print("✅ Consistency: PASS")
            else:
                print("⚠️ Consistency: WARNING (Significant deviation detected)")
                print("   Note: Deviation is often expected for recursive indicators (EMA/RSI) due to initialization differences.")
        else:
            print("⚠️ Not enough data for consistency check")

def main():
    parser = argparse.ArgumentParser(description="Manual Indicator Tester")
    parser.add_argument("indicator_id", type=str, help="Indicator ID (e.g., sma.5)")
    parser.add_argument("--rows", type=int, default=1000, help="Number of data rows")
    args = parser.parse_args()
    
    tester = IndicatorTester()
    tester.run_test(args.indicator_id, args.rows)

if __name__ == "__main__":
    main()
