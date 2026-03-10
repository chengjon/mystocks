from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_pm2_first_class_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "PM2 First-Class Gate" in content
    assert "python scripts/compliance/pm2_first_class_gate.py --format json" in content
    assert "pm2-first-class-gate-report.json" in content


def test_pre_commit_config_registers_pm2_first_class_gate() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: pm2-first-class-gate" in content
    assert "name: PM2 First-Class Gate" in content
    assert "python scripts/compliance/pm2_first_class_gate.py --format text" in content


def test_githooks_pre_commit_runs_pm2_first_class_gate() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "pm2_first_class_gate.py" in content
    assert "Running PM2 first-class gate" in content
    assert "pm2-first-class-gate" in content
