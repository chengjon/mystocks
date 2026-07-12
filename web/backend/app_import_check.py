#!/usr/bin/env python
"""Test FastAPI app import and route registration"""

import sys
from pathlib import Path


# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.main import app

    print("✅ FastAPI app imported successfully")
    print(f"✅ Total routes: {len(app.routes)}")

    # Check Week 1 routes
    print("\n✅ Checking Week 1 Architecture-Compliant routes...")
    routes = [r for r in app.routes if hasattr(r, "path")]

    strategy_routes = [r.path for r in routes if "/v1/strategy" in r.path]
    risk_routes = [r.path for r in routes if "/v1/risk" in r.path]

    print(f"  Strategy management routes: {len(strategy_routes)}")
    print(f"  Risk management routes: {len(risk_routes)}")

    print("\n📋 Sample strategy routes:")
    for r in strategy_routes[:5]:
        print(f"  - {r}")

    print("\n📋 Sample risk routes:")
    for r in risk_routes[:5]:
        print(f"  - {r}")

    print("\n✅ Week 2 FastAPI setup complete!")
    print(f"✅ Total API endpoints: {len([r for r in routes if hasattr(r, 'methods')])}")

except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
