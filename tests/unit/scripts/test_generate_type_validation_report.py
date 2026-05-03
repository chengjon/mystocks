from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_generate_type_validation_report_writes_latest_and_timestamped_json(tmp_path: Path) -> None:
    report_dir = tmp_path / "type-extension-report"

    completed = subprocess.run(
        [
            "node",
            "web/frontend/scripts/generate-type-validation-report.js",
            "--report-dir",
            str(report_dir),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout

    payload = json.loads(completed.stdout)

    assert payload["overall"]["ok"] is True
    assert payload["validation"]["ok"] is True
    assert payload["conflicts"]["ok"] is True
    assert payload["audit"]["naming"]["ok"] is True
    assert payload["audit"]["jsdoc"]["ok"] is True
    assert payload["audit"]["unused"]["count"] >= 1

    latest_report = Path(payload["report_paths"]["latest_json"])
    timestamped_report = Path(payload["report_paths"]["timestamped_json"])

    assert latest_report.is_file()
    assert timestamped_report.is_file()

    latest_payload = json.loads(latest_report.read_text(encoding="utf-8"))

    assert latest_payload["overall"]["ok"] is True
    assert latest_payload["audit"]["unused"]["count"] >= 1
