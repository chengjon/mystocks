from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
API_INTEGRATION_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "api-integration" / "spec.md"


def test_api_integration_spec_mentions_canonical_realtime_transport_selection() -> None:
    spec_text = API_INTEGRATION_SPEC_PATH.read_text(encoding="utf-8")

    assert "Canonical Realtime Transport Selection" in spec_text
    assert "canonical transport used for that capability" in spec_text
    assert "approved fallback or coexistence transport" in spec_text
    assert "selection SHALL align with the realtime delivery truth registry" in spec_text
    assert "non-canonical paths SHALL remain compatibility-scoped or cleanup-scoped until retired" in spec_text
    assert "canonical designation SHALL match the registered realtime delivery truth" in spec_text
