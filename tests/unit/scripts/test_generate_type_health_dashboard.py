from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_generate_type_health_dashboard_writes_latest_and_timestamped_html(tmp_path: Path) -> None:
    report_dir = tmp_path / "type-extension-report"
    report_dir.mkdir(parents=True, exist_ok=True)

    latest_report = report_dir / "latest.json"
    latest_report.write_text(
        json.dumps(
            {
                "summary_schema_version": 1,
                "generated_at": "2026-05-03T02:20:00.000Z",
                "validation": {"ok": True},
                "conflicts": {"ok": True},
                "audit": {
                    "naming": {"ok": True},
                    "jsdoc": {"ok": True},
                    "unused": {"count": 2, "names": ["UnusedAlpha", "UnusedBeta"]},
                },
                "usage": {"extensions": {"files": 7, "exported_types": 94}},
                "typecheck": {"ok": True, "type_error_count": 0},
                "overall": {
                    "ok": True,
                    "observations": {"unused_type_definition_count": 2},
                },
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            "node",
            "web/frontend/scripts/generate-type-health-dashboard.js",
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

    latest_dashboard = Path(payload["dashboard_paths"]["latest_html"])
    timestamped_dashboard = Path(payload["dashboard_paths"]["timestamped_html"])

    assert latest_dashboard.is_file()
    assert timestamped_dashboard.is_file()

    html = latest_dashboard.read_text(encoding="utf-8")
    assert "Type Extension Health Dashboard" in html
    assert "UnusedAlpha" in html
    assert "UnusedBeta" in html
