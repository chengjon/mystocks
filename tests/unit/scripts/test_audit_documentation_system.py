from __future__ import annotations

import textwrap
from pathlib import Path

from scripts.governance.audit_documentation_system import build_report, load_taxonomy


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TAXONOMY_PATH = PROJECT_ROOT / "config" / "governance" / "documentation-taxonomy.yaml"


def write_taxonomy(tmp_path: Path, content: str) -> Path:
    target = tmp_path / "config" / "governance" / "documentation-taxonomy.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return target


def test_load_taxonomy_reads_expected_sections() -> None:
    taxonomy = load_taxonomy(DEFAULT_TAXONOMY_PATH)

    assert taxonomy["metadata"]["id"] == "documentation-governance-taxonomy"
    assert "delete_candidate" in taxonomy["lifecycle_classes"]
    assert "decision_register_marks_delete" in taxonomy["delete_gate_requirements"]
    assert any(trunk["id"] == "documentation-governance-trunk" for trunk in taxonomy["trunks"])


def test_build_report_flags_duplicate_truth_concerns(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "docs" / "b.md").write_text("# B\n", encoding="utf-8")
    taxonomy_path = write_taxonomy(
        tmp_path,
        """
        metadata:
          id: duplicate-truth-test
          version: 1
        scan_roots:
          - docs
        decision_statuses: [keep-canonical, delete, needs-replacement]
        lifecycle_classes:
          canonical: {description: canonical, current_truth_allowed: true}
          delete_candidate: {description: delete, current_truth_allowed: false}
        archive_targets:
          retired_docs: archive/docs/
        delete_gate_requirements:
          - canonical_replacement_exists
        trunks:
          - id: first
            concern: same-concern
            path: docs/a.md
            path_kind: file
            lifecycle: canonical
            current_truth: true
          - id: second
            concern: same-concern
            path: docs/b.md
            path_kind: file
            lifecycle: canonical
            current_truth: true
        protected_doc_families: []
        families: []
        """,
    )

    report = build_report(tmp_path, taxonomy_path=taxonomy_path)

    assert report["summary"]["duplicate_truths"] == 1
    assert report["findings"]["duplicate_truths"][0]["concern"] == "same-concern"


def test_build_report_blocks_delete_candidate_without_replacement(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "legacy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Legacy\n", encoding="utf-8")
    taxonomy_path = write_taxonomy(
        tmp_path,
        """
        metadata:
          id: delete-gate-test
          version: 1
        scan_roots:
          - docs
        decision_statuses: [keep-canonical, delete, needs-replacement]
        lifecycle_classes:
          canonical: {description: canonical, current_truth_allowed: true}
          delete_candidate: {description: delete, current_truth_allowed: false}
        archive_targets:
          retired_docs: archive/docs/
        delete_gate_requirements:
          - canonical_replacement_exists
          - inbound_links_updated_or_retired
          - no_retention_duty_remains
          - decision_register_marks_delete
        trunks:
          - id: docs-entrypoint
            concern: docs
            path: docs/README.md
            path_kind: file
            lifecycle: canonical
            current_truth: true
        protected_doc_families: []
        families:
          - id: stale-family
            concern: docs
            match_paths:
              - docs/legacy.md
            lifecycle: delete_candidate
            canonical_trunk_id: docs-entrypoint
            delete_gate:
              inbound_links: pending-review
              retention_duty: none
              decision_status: needs-replacement
        """,
    )

    report = build_report(tmp_path, taxonomy_path=taxonomy_path)

    assert report["summary"]["blocked_delete_candidates"] == 1
    blocked = report["findings"]["blocked_delete_candidates"][0]
    assert blocked["family_id"] == "stale-family"
    assert "missing canonical_replacement" in blocked["issues"]
    assert "delete_gate.inbound_links=pending-review" in blocked["issues"]
    assert "delete_gate.decision_status=needs-replacement" in blocked["issues"]


def test_build_report_skips_deleted_web_dev_compatibility_entrypoints() -> None:
    assert not (PROJECT_ROOT / "docs" / "web-dev").exists()

    report = build_report(
        PROJECT_ROOT,
        taxonomy_path=DEFAULT_TAXONOMY_PATH,
        paths=["docs/web-dev/INDEX.md", "docs/web-dev/GUIDE.md"],
    )

    assert report["scanned_files"] == 0
    assert report["classified_files"] == 0
    assert report["summary"]["unclassified"] == 0
    assert report["summary"]["blocked_delete_candidates"] == 0
    assert report["classifications"] == []
