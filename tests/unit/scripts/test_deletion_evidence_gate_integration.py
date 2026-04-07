from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_pre_commit_config_registers_deletion_evidence_gate() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: deletion-evidence-gate" in content
    assert "name: Deletion Evidence Gate" in content
    assert "python scripts/compliance/deletion_evidence_gate.py --root-dir . --format text --scope staged" in content
    assert "pass_filenames: false" in content


def test_githooks_pre_commit_runs_deletion_evidence_gate() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "run_deletion_evidence_gate" in content
    assert "deletion evidence gate" in content.lower()
    assert "deletion_evidence_gate.py" in content
    assert "DISABLE_DELETION_EVIDENCE_GATE" in content
    assert "SKIP=deletion-evidence-gate" in content or "deletion-evidence-gate" in content


def test_claude_settings_register_stop_deletion_evidence_gate() -> None:
    payload = json.loads((PROJECT_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    stop_hooks = payload["hooks"]["Stop"]
    commands = [hook["hooks"][0]["command"] for hook in stop_hooks]

    assert "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-deletion-evidence-gate.sh" in commands


def test_governance_registry_files_exist() -> None:
    assert (PROJECT_ROOT / "governance" / "deletion-evidence.yaml").is_file()
    assert (PROJECT_ROOT / "governance" / "waivers" / "deletion-evidence-waivers.yaml").is_file()
