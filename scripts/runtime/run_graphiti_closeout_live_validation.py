from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


HOOK_SCRIPT = PROJECT_ROOT / ".claude" / "hooks" / "stop-graphiti-task-closeout.sh"
COORDCTL = PROJECT_ROOT / "scripts" / "runtime" / "coordctl.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a real Stop-hook-to-Graphiti closeout validation flow.")
    parser.add_argument("--timestamp", default=None, help="Validation timestamp label, defaults to current local time.")
    parser.add_argument("--session-id", default="live-closeout-session-1")
    parser.add_argument("--actor-cli", default="closeout-live")
    parser.add_argument("--completion-text", default=None)
    parser.add_argument("--user-text", default="请执行真实 closeout hook 验收")
    parser.add_argument("--report-file", default=None, help="Optional markdown report path to write validation result.")
    parser.add_argument("--output", choices=("json", "text"), default="json")
    return parser


def _default_completion_text() -> str:
    return (
        "收尾已完成\n"
        "- 已完成：真实 Graphiti closeout hook 验收\n"
        "- 验证：python scripts/runtime/smoke_graphiti_closeout_hook.py --output json\n"
        "- 验证：真实 Graphiti write/search smoke 已通过"
    )


def run_live_validation(
    *,
    timestamp: str,
    session_id: str,
    actor_cli: str,
    completion_text: str,
    user_text: str,
    report_file: str | None = None,
    run_command: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    group_id = f"mystocks_spec_closeout_hook_live_{timestamp}"
    report_path = Path(report_file) if report_file else None

    with tempfile.TemporaryDirectory(prefix="graphiti-closeout-live-") as temp_dir:
        root = Path(temp_dir)
        transcript = root / "transcript.jsonl"
        state_path = root / ".claude" / "graphiti-closeout-state.json"
        config_path = root / "config" / "hooks" / "graphiti-closeout.json"
        edit_log_path = root / ".claude" / "edit_log.jsonl"

        edit_log_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        transcript.write_text(
            json.dumps(
                {
                    "type": "user",
                    "timestamp": "2026-04-22T14:35:00+08:00",
                    "message": {"content": [{"type": "text", "text": user_text}]},
                },
                ensure_ascii=False,
            )
            + "\n"
            + json.dumps(
                {
                    "type": "assistant",
                    "timestamp": "2026-04-22T14:35:30+08:00",
                    "uuid": "assistant-live-closeout-1",
                    "message": {"model": "gpt-5", "content": [{"type": "text", "text": completion_text}]},
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        edit_log_path.write_text(
            json.dumps(
                {"session_id": session_id, "relative_path": "docs/guides/hooks/web-dev-hooks-guide.md"},
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        config_path.write_text(
            json.dumps(
                {
                    "actor_cli": actor_cli,
                    "group_id_template": group_id,
                    "positive_patterns": [
                        {"label": "收尾已完成", "pattern": "收尾已完成"},
                        {"label": "已完成", "pattern": "(^|\\n)\\s*已完成"},
                        {"label": "任务完成", "pattern": "任务完成"},
                    ],
                    "negative_patterns": ["未完成", "尚未完成", "not\\s+completed", "待继续"],
                    "verification_patterns": ["python", "验证", "smoke", "Graphiti"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["GRAPHITI_CLOSEOUT_SYNC"] = "1"
        env["GRAPHITI_CLOSEOUT_COMMAND"] = f"python {COORDCTL}"
        env["CLAUDE_PROJECT_DIR"] = str(PROJECT_ROOT)

        event = {"session_id": session_id, "transcript_path": str(transcript), "cwd": str(root)}
        hook_completed = run_command(
            [str(HOOK_SCRIPT)],
            input=json.dumps(event, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=PROJECT_ROOT,
            env=env,
            check=True,
        )

        state = json.loads(state_path.read_text(encoding="utf-8"))
        state_report = state["reports"][-1]

        search_completed = run_command(
            [
                "python",
                str(COORDCTL),
                "graphiti",
                "search",
                "--actor-cli",
                actor_cli,
                "--query",
                "真实 Graphiti closeout hook 验收",
                "--group-id",
                group_id,
                "--output",
                "json",
            ],
            text=True,
            capture_output=True,
            cwd=PROJECT_ROOT,
            check=True,
        )
        search_payload = json.loads(search_completed.stdout or "{}")

        result = {
            "hook_stdout": (hook_completed.stdout or "").strip(),
            "state_report": state_report,
            "group_id": group_id,
            "search": {
                "server_status": search_payload.get("server_status"),
                "search_outcome": search_payload.get("search_outcome"),
                "search_summary": search_payload.get("search_summary"),
                "matched_nodes_count": search_payload.get("matched_nodes_count"),
                "matched_facts_count": search_payload.get("matched_facts_count"),
            },
        }

        if report_path:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(render_report(result, timestamp=timestamp, session_id=session_id, actor_cli=actor_cli), encoding="utf-8")

        return result


def render_report(result: dict[str, Any], *, timestamp: str, session_id: str, actor_cli: str) -> str:
    state_report = result["state_report"]
    search = result["search"]
    return "\n".join(
        [
            "# Graphiti Closeout Hook Live Validation",
            "",
            f"- Timestamp: `{timestamp}`",
            f"- Session ID: `{session_id}`",
            f"- Actor CLI: `{actor_cli}`",
            f"- Group ID: `{result['group_id']}`",
            "",
            "## Local State Result",
            "",
            f"- Hook stdout: `{result['hook_stdout']}`",
            f"- Status: `{state_report.get('status')}`",
            f"- Completion phrase: `{state_report.get('completion_phrase')}`",
            f"- Episode UUID: `{state_report.get('episode_uuid')}`",
            f"- Ingest status: `{state_report.get('ingest_status')}`",
            "",
            "## Graphiti Search Result",
            "",
            f"- Server status: `{search.get('server_status')}`",
            f"- Search outcome: `{search.get('search_outcome')}`",
            f"- Search summary: `{search.get('search_summary')}`",
            f"- Matched nodes count: `{search.get('matched_nodes_count')}`",
            f"- Matched facts count: `{search.get('matched_facts_count')}`",
            "",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d%H%M%S")
    result = run_live_validation(
        timestamp=timestamp,
        session_id=args.session_id,
        actor_cli=args.actor_cli,
        completion_text=args.completion_text or _default_completion_text(),
        user_text=args.user_text,
        report_file=args.report_file,
    )
    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Graphiti closeout live validation passed")
        print(f"- group_id: {result['group_id']}")
        print(f"- episode_uuid: {result['state_report'].get('episode_uuid')}")
        print(f"- search_outcome: {result['search'].get('search_outcome')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
