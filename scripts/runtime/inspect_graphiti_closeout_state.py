from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect local Graphiti closeout hook audit state.")
    parser.add_argument("--state-file", default=".claude/graphiti-closeout-state.json")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", choices=("text", "json"), default="text")
    return parser


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"processed": [], "reports": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"processed": [], "reports": []}
    if not isinstance(data, dict):
        return {"processed": [], "reports": []}
    if not isinstance(data.get("processed"), list):
        data["processed"] = []
    if not isinstance(data.get("reports"), list):
        data["reports"] = []
    return data


def summarize_state(state: dict[str, Any], *, limit: int = 5, state_path: str | None = None) -> dict[str, Any]:
    reports = [report for report in state.get("reports", []) if isinstance(report, dict)]
    successes = [report for report in reports if report.get("status") == "completed"]
    failures = [report for report in reports if report.get("status") != "completed"]
    recent_failures = list(reversed(failures[-limit:])) if limit > 0 else []
    recent_successes = list(reversed(successes[-limit:])) if limit > 0 else []

    return {
        "state_file": state_path,
        "processed_count": len(state.get("processed", [])) if isinstance(state.get("processed", []), list) else 0,
        "report_count": len(reports),
        "completed_count": len(successes),
        "failed_count": len(failures),
        "latest_reported_at": reports[-1].get("recorded_at") if reports else None,
        "recent_failures": recent_failures,
        "recent_successes": recent_successes,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "Graphiti Closeout State",
        f"- State File: {summary.get('state_file') or '(unknown)'}",
        f"- Processed Keys: {summary['processed_count']}",
        f"- Reports: {summary['report_count']}",
        f"- Completed: {summary['completed_count']}",
        f"- Failed: {summary['failed_count']}",
        f"- Latest Reported At: {summary.get('latest_reported_at') or '(none)'}",
        "",
        "Recent Failures:",
    ]

    failures = summary.get("recent_failures", [])
    if failures:
        for report in failures:
            lines.append(
                "- {recorded_at} | session={session_id} | phrase={completion_phrase} | error={error}".format(
                    recorded_at=report.get("recorded_at") or "(unknown)",
                    session_id=report.get("session_id") or "(unknown)",
                    completion_phrase=report.get("completion_phrase") or "(unknown)",
                    error=report.get("error") or "(none)",
                )
            )
    else:
        lines.append("- (none)")

    lines.extend(["", "Recent Successes:"])
    successes = summary.get("recent_successes", [])
    if successes:
        for report in successes:
            lines.append(
                "- {recorded_at} | session={session_id} | episode={episode_uuid} | group={group_id}".format(
                    recorded_at=report.get("recorded_at") or "(unknown)",
                    session_id=report.get("session_id") or "(unknown)",
                    episode_uuid=report.get("episode_uuid") or "(unknown)",
                    group_id=report.get("group_id") or "(unknown)",
                )
            )
    else:
        lines.append("- (none)")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state_path = Path(args.state_file)
    summary = summarize_state(load_state(state_path), limit=max(args.limit, 0), state_path=str(state_path))

    if args.output == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_text(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
