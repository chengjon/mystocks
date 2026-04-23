#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_CLOSEOUTS = (
    ("frontend_runtime_gate", "Frontend runtime gate", "mystocks_spec_quality_gates"),
    ("api_performance_gate", "API performance gate", "mystocks_spec_quality_gates"),
    ("docker_runtime_smoke", "Docker runtime smoke", "mystocks_spec_quality_gates"),
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payload(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        payload = load_json(path)
    except Exception as exc:
        return {
            "status": "invalid_payload",
            "ingest_status": "not_loaded",
            "error": str(exc),
            "_path": str(path),
        }
    if not isinstance(payload, dict):
        return {
            "status": "invalid_payload",
            "ingest_status": "not_loaded",
            "error": "closeout payload is not a JSON object",
            "_path": str(path),
        }
    payload["_path"] = str(path)
    return payload


def validate_closeouts(closeouts: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for key, label, expected_group_id in EXPECTED_CLOSEOUTS:
        payload = closeouts.get(key)
        if payload is None:
            items.append(
                {
                    "key": key,
                    "label": label,
                    "expected_group_id": expected_group_id,
                    "present": False,
                    "valid": False,
                    "reason": "missing_closeout",
                }
            )
            continue

        report = payload.get("report") if isinstance(payload.get("report"), dict) else {}
        status = payload.get("status")
        episode_uuid = payload.get("episode_uuid") or report.get("episode_uuid")
        group_id = payload.get("group_id") or report.get("group_id")
        ingest_status = payload.get("ingest_status") or report.get("ingest_status")
        error = payload.get("error")

        reason = "ok"
        valid = True
        if status != "completed":
            valid = False
            reason = f"status={status or 'missing'}"
        elif not isinstance(episode_uuid, str) or not episode_uuid.strip():
            valid = False
            reason = "missing_episode_uuid"
        elif group_id != expected_group_id:
            valid = False
            reason = f"group_id={group_id or 'missing'}"
        elif ingest_status not in {"warming", "completed"}:
            valid = False
            reason = f"ingest_status={ingest_status or 'missing'}"
        elif isinstance(error, str) and error.strip():
            valid = False
            reason = "payload_error"

        items.append(
            {
                "key": key,
                "label": label,
                "expected_group_id": expected_group_id,
                "present": True,
                "valid": valid,
                "reason": reason,
                "episode_uuid": episode_uuid,
                "group_id": group_id,
                "ingest_status": ingest_status,
                "path": payload.get("_path"),
            }
        )

    invalid_items = [item for item in items if not item["valid"]]
    return {
        "pass": not invalid_items,
        "total_expected": len(EXPECTED_CLOSEOUTS),
        "valid_count": len([item for item in items if item["valid"]]),
        "invalid_count": len(invalid_items),
        "items": items,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate child gate Graphiti closeouts for the full runtime delivery gate.")
    parser.add_argument("--frontend-closeout-json", required=True)
    parser.add_argument("--api-closeout-json", required=True)
    parser.add_argument("--docker-closeout-json", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fail-on-invalid", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    closeouts = {
        "frontend_runtime_gate": load_payload(Path(args.frontend_closeout_json)),
        "api_performance_gate": load_payload(Path(args.api_closeout_json)),
        "docker_runtime_smoke": load_payload(Path(args.docker_closeout_json)),
    }
    report = validate_closeouts(closeouts)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.fail_on_invalid and not report["pass"]:
        print("[runtime-child-closeouts] invalid child closeouts detected")
        for item in report["items"]:
            if not item["valid"]:
                print(f"- {item['label']}: {item['reason']}")
        return 1

    print(f"[runtime-child-closeouts] written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
