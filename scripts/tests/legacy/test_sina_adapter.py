#!/usr/bin/env python3
"""
Test Sina Finance stock ratings adapter
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly to avoid adapters __init__.py issues
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "adapters"))

from sina_finance_adapter import SinaFinanceDataSource


def test_sina_finance_adapter():
    """Test the Sina Finance adapter directly"""
    print("Testing Sina Finance stock ratings adapter...")

    try:
        # Create adapter instance
        adapter = SinaFinanceDataSource()

        # Test getting data
        result = adapter.get_data(max_pages=1)

        print("✓ Adapter created successfully")
        print(f"✓ Data retrieved: {len(result)} records")

        if len(result) > 0:
            print("Sample record:")
            print(result.head(1).to_dict("records")[0])

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sina_finance_adapter()
    sys.exit(0 if success else 1)
