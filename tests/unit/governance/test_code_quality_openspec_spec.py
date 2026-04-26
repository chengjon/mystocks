from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CODE_QUALITY_SPEC_PATH = PROJECT_ROOT / "openspec" / "specs" / "code-quality" / "spec.md"


def test_code_quality_openspec_spec_mentions_closure_wave_evidence_contract() -> None:
    spec_text = CODE_QUALITY_SPEC_PATH.read_text(encoding="utf-8")

    assert "Closure Wave Evidence Contract" in spec_text
    assert "verified truth source" in spec_text
    assert "executed validations" in spec_text
    assert "unresolved follow-up items" in spec_text
    assert "what was verified in code" in spec_text
    assert "what was verified in docs" in spec_text
    assert "reject narrative-only completion claims" in spec_text
