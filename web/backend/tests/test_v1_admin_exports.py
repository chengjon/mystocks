from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def test_v1_admin_exports_exclude_parallel_auth_router() -> None:
    from app.api.v1.admin import __all__

    assert __all__ == ["audit_router", "optimization_router"]
