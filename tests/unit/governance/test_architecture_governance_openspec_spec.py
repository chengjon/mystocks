from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ARCHITECTURE_GOVERNANCE_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "architecture-governance" / "spec.md"


def test_architecture_governance_spec_mentions_q2_closure_requirements() -> None:
    spec_text = ARCHITECTURE_GOVERNANCE_SPEC_PATH.read_text(encoding="utf-8")

    assert "Q2 Architecture Closure Program" in spec_text
    assert "Sequential Closure Gate For Cross-Cutting Waves" in spec_text
    assert "Backend Composition Source Of Truth" in spec_text
    assert "Realtime Delivery Truth Registry" in spec_text
    assert "single-CLI sequential delivery" in spec_text
    assert "canonical truths it intends to settle" in spec_text
    assert "compatibility-retained, delegated, or retirement-targeted" in spec_text
    assert "canonical realtime transport selection policy defined for API integration" in spec_text
