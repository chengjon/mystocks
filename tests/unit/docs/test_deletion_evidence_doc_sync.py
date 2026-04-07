from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_deletion_evidence_guide_is_discoverable_and_points_to_canonical_artifacts() -> None:
    guide_path = PROJECT_ROOT / "docs" / "guides" / "governance" / "DELETION_EVIDENCE_GATE.md"
    docs_index = (PROJECT_ROOT / "docs" / "INDEX.md").read_text(encoding="utf-8")
    guides_index = (PROJECT_ROOT / "docs" / "guides" / "INDEX.md").read_text(encoding="utf-8")
    governance_index = (PROJECT_ROOT / "docs" / "guides" / "governance" / "INDEX.md").read_text(encoding="utf-8")
    mainline_readme = (PROJECT_ROOT / "governance" / "mainline" / "README.md").read_text(encoding="utf-8")

    assert guide_path.is_file()

    guide = guide_path.read_text(encoding="utf-8")
    assert "scripts/compliance/deletion_evidence_gate.py" in guide
    assert ".githooks/pre-commit" in guide
    assert ".claude/hooks/stop-deletion-evidence-gate.sh" in guide
    assert "governance/deletion-evidence.yaml" in guide
    assert "governance/waivers/deletion-evidence-waivers.yaml" in guide
    assert "`HEAD`" in guide
    assert "wildcard" in guide.lower()

    assert "guides/governance/DELETION_EVIDENCE_GATE.md" in docs_index
    assert "governance/DELETION_EVIDENCE_GATE.md" in guides_index
    assert "DELETION_EVIDENCE_GATE" in governance_index
    assert "docs/guides/governance/DELETION_EVIDENCE_GATE.md" in mainline_readme
