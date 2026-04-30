from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports" / "quality" / "windows-qmt-contract-acceptance"
BASELINE_SCHEMA_VERSION = 1
BASELINE_KIND = "windows_qmt_contract_acceptance"


def _load_json_object(path: Path) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, Mapping):
        return None
    return payload


def build_timestamped_baseline_output_path(
    baseline_dir: str | Path,
    *,
    now: datetime | None = None,
) -> Path:
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    return Path(baseline_dir) / f"{timestamp}-windows-qmt-contract-baseline.json"


def build_frozen_baseline(
    summary: Mapping[str, Any],
    *,
    source_summary_path: str | Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    frozen_baseline = dict(summary)
    frozen_baseline["baseline_schema_version"] = BASELINE_SCHEMA_VERSION
    frozen_baseline["baseline_kind"] = BASELINE_KIND
    frozen_baseline["baseline_frozen_at"] = (now or datetime.now(timezone.utc)).isoformat()
    frozen_baseline["frozen_from_summary_path"] = str(Path(source_summary_path))
    return frozen_baseline


def write_json_output(payload: Mapping[str, Any], output_path: str | Path) -> Path:
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target_path


def persist_frozen_baseline(
    frozen_baseline: Mapping[str, Any],
    *,
    baseline_dir: str | Path,
    now: datetime | None = None,
) -> dict[str, str]:
    baseline_root = Path(baseline_dir)
    timestamped_baseline_path = build_timestamped_baseline_output_path(baseline_root, now=now)
    latest_baseline_path = baseline_root / "latest-baseline.json"
    write_json_output(frozen_baseline, timestamped_baseline_path)
    write_json_output(frozen_baseline, latest_baseline_path)
    return {
        "timestamped_baseline_path": str(timestamped_baseline_path),
        "latest_baseline_path": str(latest_baseline_path),
    }


def build_failure_payload(
    *,
    status_label: str,
    recommended_exit_code: int,
    source_summary_path: str | Path,
    baseline_dir: str | Path,
    issues: list[str],
) -> dict[str, Any]:
    return {
        "status_label": status_label,
        "recommended_exit_code": recommended_exit_code,
        "source_summary_path": str(Path(source_summary_path)),
        "baseline_dir": str(Path(baseline_dir)),
        "issues": issues,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the latest Windows qmt acceptance summary into a reusable baseline artifact."
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory containing latest.json and the default baselines/ output directory.",
    )
    parser.add_argument(
        "--source-summary",
        default=None,
        help="Optional explicit path to the acceptance summary JSON to freeze. Defaults to <report-dir>/latest.json.",
    )
    parser.add_argument(
        "--baseline-dir",
        default=None,
        help="Optional explicit baseline output directory. Defaults to <report-dir>/baselines.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report_dir = Path(getattr(args, "report_dir"))
    source_summary_path = Path(getattr(args, "source_summary") or (report_dir / "latest.json"))
    baseline_dir = Path(getattr(args, "baseline_dir") or (report_dir / "baselines"))

    summary = _load_json_object(source_summary_path)
    if summary is None:
        payload = build_failure_payload(
            status_label="source_summary_missing",
            recommended_exit_code=2,
            source_summary_path=source_summary_path,
            baseline_dir=baseline_dir,
            issues=["source acceptance summary is missing or invalid"],
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    if summary.get("ok") is not True or str(summary.get("stage", "")).strip() != "completed":
        payload = build_failure_payload(
            status_label="source_summary_ineligible",
            recommended_exit_code=1,
            source_summary_path=source_summary_path,
            baseline_dir=baseline_dir,
            issues=["acceptance summary is not eligible for baseline freeze; expected ok=true and stage=completed"],
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    frozen_baseline = build_frozen_baseline(summary, source_summary_path=source_summary_path)
    artifacts = persist_frozen_baseline(frozen_baseline, baseline_dir=baseline_dir)
    payload = {
        "status_label": "baseline_frozen",
        "recommended_exit_code": 0,
        "source_summary_path": str(source_summary_path),
        "baseline_dir": str(baseline_dir),
        "baseline_schema_version": BASELINE_SCHEMA_VERSION,
        "baseline_kind": BASELINE_KIND,
        **artifacts,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
