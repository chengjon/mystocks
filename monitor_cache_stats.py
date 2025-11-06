#!/usr/bin/env python3
"""
Cache Statistics Monitoring Script - Task 2.1

Real-time monitoring of TDengine cache statistics:
- Cache hit rate (target: ≥80%)
- Total cached records
- Unique symbols cached
- Cache operations performance
- Hot symbol identification

Run with: python monitor_cache_stats.py
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class CacheMonitor:
    """Monitor TDengine cache statistics"""

    def __init__(self, interval: int = 5):
        """
        Initialize cache monitor

        Args:
            interval: Update interval in seconds
        """
        self.interval = interval
        self.manager = None
        self.start_time = datetime.now()
        self.stats_history = []
        self.max_history = 100

    def initialize(self) -> bool:
        """Initialize cache manager"""
        try:
            from web.backend.app.core.tdengine_manager import TDengineManager

            self.manager = TDengineManager()
            if not self.manager.initialize():
                print("❌ Failed to initialize TDengineManager")
                return False

            print("✅ Cache monitor initialized")
            return True

        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            return False

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get current cache statistics"""
        if not self.manager:
            return None

        try:
            stats = self.manager.get_cache_stats()
            if stats:
                stats["timestamp"] = datetime.now().isoformat()
                return stats
            return None

        except Exception as e:
            print(f"⚠️ Error getting stats: {str(e)}")
            return None

    def calculate_hit_rate(self) -> Optional[float]:
        """Calculate cache hit rate"""
        if not self.manager:
            return None

        try:
            # This would require tracking hits and misses
            # For now, query basic stats
            stats = self.manager.get_cache_stats()
            if stats and "hit_rate" in stats:
                return stats["hit_rate"]
            return None

        except Exception as e:
            print(f"⚠️ Error calculating hit rate: {str(e)}")
            return None

    def get_hot_symbols(self) -> Optional[list]:
        """Get hot symbols from cache"""
        if not self.manager:
            return None

        try:
            # Query hot symbols from database
            sql = """
                SELECT symbol, access_count, last_access
                FROM hot_symbols
                ORDER BY access_count DESC
                LIMIT 10
            """
            result = self.manager._execute_query(sql)
            if result:
                return [
                    {"symbol": row[0], "access_count": row[1], "last_access": row[2]}
                    for row in result
                ]
            return []

        except Exception as e:
            print(f"⚠️ Error getting hot symbols: {str(e)}")
            return None

    def print_stats(self, stats: Dict[str, Any]):
        """Print formatted statistics"""
        print(f"\n{'=' * 70}")
        print(f"  Cache Statistics - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 70}")

        if stats:
            print(f"\n  📊 Cache Overview:")
            print(f"    Total Records:   {stats.get('total_records', 'N/A')}")
            print(f"    Unique Symbols:  {stats.get('unique_symbols', 'N/A')}")
            print(f"    Timestamp:       {stats.get('timestamp', 'N/A')}")

            # Calculate uptime
            uptime = datetime.now() - self.start_time
            print(f"\n  ⏱️  Uptime:        {uptime}")

            # Show hit rate
            hit_rate = self.calculate_hit_rate()
            if hit_rate is not None:
                status = "✅" if hit_rate >= 0.8 else "⚠️"
                print(f"\n  {status} Cache Hit Rate:   {hit_rate:.1%}")
            else:
                print(f"\n  ⚠️ Cache Hit Rate:   Not available yet")

            # Show hot symbols
            hot_symbols = self.get_hot_symbols()
            if hot_symbols:
                print(f"\n  🔥 Hot Symbols (Top 10):")
                for i, symbol in enumerate(hot_symbols[:10], 1):
                    print(
                        f"    {i:2}. {symbol['symbol']} - "
                        f"Accesses: {symbol['access_count']} - "
                        f"Last: {symbol['last_access']}"
                    )
            else:
                print(f"\n  ℹ️ No hot symbols data available yet")

        print(f"\n{'=' * 70}\n")

    def print_header(self):
        """Print monitor header"""
        print("\n" + "=" * 70)
        print("  TDengine Cache Statistics Monitor - Task 2.1")
        print("=" * 70)
        print(f"  Started: {self.start_time.isoformat()}")
        print(f"  Update Interval: {self.interval} seconds")
        print(f"  Press Ctrl+C to stop monitoring")
        print("=" * 70 + "\n")

    def run_once(self) -> bool:
        """Run one monitoring cycle"""
        stats = self.get_cache_stats()

        if stats:
            self.stats_history.append(stats)
            if len(self.stats_history) > self.max_history:
                self.stats_history.pop(0)

            self.print_stats(stats)
            return True
        else:
            print(
                f"⚠️ Could not retrieve cache statistics at {datetime.now().isoformat()}"
            )
            return False

    def print_summary(self):
        """Print monitoring summary"""
        print(f"\n{'=' * 70}")
        print(f"  Monitoring Summary")
        print(f"{'=' * 70}")

        uptime = datetime.now() - self.start_time
        print(f"\n  ⏱️  Total Uptime:        {uptime}")
        print(f"  📊 Statistics Recorded: {len(self.stats_history)}")

        if self.stats_history:
            first = self.stats_history[0]
            last = self.stats_history[-1]

            print(f"\n  📈 Growth:")
            total_records = last.get("total_records", 0)
            print(f"    Total Records:   {total_records}")
            print(f"    Unique Symbols:  {last.get('unique_symbols', 0)}")

            if total_records > 0:
                avg_record_size = 1024  # Approximate
                total_size_mb = (total_records * avg_record_size) / (1024 * 1024)
                print(f"    Estimated Size:  {total_size_mb:.2f} MB")

        print(f"\n  ℹ️ Recommendations:")
        print(f"    1. Monitor cache hit rate target: ≥80%")
        print(f"    2. Review hot symbols for optimization")
        print(f"    3. Check database performance metrics")
        print(f"    4. Monitor disk space usage")

        print(f"\n{'=' * 70}\n")

    def run_continuous(self):
        """Run continuous monitoring"""
        self.print_header()

        try:
            while True:
                self.run_once()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n✋ Monitoring stopped")
            self.print_summary()

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        if self.manager:
            self.manager.close()
            print("✅ Cache monitor closed")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor TDengine cache statistics")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)",
    )
    parser.add_argument("--once", action="store_true", help="Run once and exit")

    args = parser.parse_args()

    monitor = CacheMonitor(interval=args.interval)

    if not monitor.initialize():
        print("❌ Failed to initialize monitor")
        return 1

    if args.once:
        monitor.run_once()
        monitor.cleanup()
    else:
        monitor.run_continuous()

    return 0


if __name__ == "__main__":
    sys.exit(main())
