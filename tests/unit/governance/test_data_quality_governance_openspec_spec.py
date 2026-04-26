from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_QUALITY_GOVERNANCE_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "data-quality-governance" / "spec.md"


def test_data_quality_governance_spec_mentions_phase_c_requirements() -> None:
    spec_text = DATA_QUALITY_GOVERNANCE_SPEC_PATH.read_text(encoding="utf-8")

    assert "Canonical Data Quality Model" in spec_text
    assert "Data Quality Component Classification" in spec_text
    assert "Data Quality Closure Evidence" in spec_text
    assert "completeness, anomaly detection, temporal alignment, and repair or fallback handling" in spec_text
    assert "storage-specific quality concerns when the data spans multiple storage engines" in spec_text
    assert "validation, monitoring, repair, or reporting" in spec_text
    assert "implemented controls from planned future controls" in spec_text
