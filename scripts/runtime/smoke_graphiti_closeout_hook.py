from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.runtime.inspect_graphiti_closeout_state import summarize_state

HOOK_SCRIPT = PROJECT_ROOT / ".claude" / "hooks" / "stop-graphiti-task-closeout.sh"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an end-to-end smoke flow for the Stop Graphiti closeout hook.")
    parser.add_argument("--completion-text", default="已完成\n- 验证: pytest smoke")
    parser.add_argument("--user-text", default="请执行 closeout smoke")
    parser.add_argument("--session-id", default="smoke-session-1")
    parser.add_argument("--actor-cli", default="smoke-cli")
    parser.add_argument("--group-id-template", default="smoke_{project_name}_closeouts")
    parser.add_argument("--output", choices=("json", "text"), default="json")
    return parser


def run_smoke(
    *,
    completion_text: str,
    user_text: str,
    session_id: str,
    actor_cli: str,
    group_id_template: str,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="graphiti-closeout-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        transcript_path = temp_root / "transcript.jsonl"
        state_path = temp_root / ".claude" / "graphiti-closeout-state.json"
        args_path = temp_root / "graphiti-args.json"
        command_path = temp_root / "fake_graphiti.sh"
        config_path = temp_root / "config" / "hooks" / "graphiti-closeout.json"
        edit_log_path = temp_root / ".claude" / "edit_log.jsonl"

        transcript_path.write_text(
            "".join(
                [
                    json.dumps(
                        {
                            "type": "user",
                            "timestamp": "2026-04-22T10:00:00Z",
                            "message": {"content": [{"type": "text", "text": user_text}]},
                        },
                        ensure_ascii=False,
                    )
                    + "\n",
                    json.dumps(
                        {
                            "type": "assistant",
                            "timestamp": "2026-04-22T10:05:00Z",
                            "uuid": "assistant-smoke-1",
                            "message": {
                                "model": "gpt-5",
                                "content": [{"type": "text", "text": completion_text}],
                            },
                        },
                        ensure_ascii=False,
                    )
                    + "\n",
                ]
            ),
            encoding="utf-8",
        )

        edit_log_path.parent.mkdir(parents=True, exist_ok=True)
        edit_log_path.write_text(
            json.dumps({"session_id": session_id, "relative_path": "docs/example.md"}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(
                {
                    "actor_cli": actor_cli,
                    "group_id_template": group_id_template,
                    "positive_patterns": [
                        {"label": "已完成", "pattern": "(^|\\n)\\s*已完成"},
                        {"label": "任务完成", "pattern": "任务完成"},
                    ],
                    "negative_patterns": ["未完成", "尚未完成", "not\\s+completed", "待继续"],
                    "verification_patterns": ["pytest", "验证", "test"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        resolved_group_id = group_id_template.format(project_name=temp_root.name, project_root=str(temp_root.resolve()))
        command_path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "set -euo pipefail",
                    f"python -c 'import json,sys; open({json.dumps(str(args_path))}, \"w\", encoding=\"utf-8\").write(json.dumps(sys.argv[1:], ensure_ascii=False))' \"$@\"",
                    "cat <<'EOF'",
                    json.dumps(
                        {
                            "server_status": "ok",
                            "ingest_status": "completed",
                            "episode_uuid": "ep-smoke-1",
                            "group_id": resolved_group_id,
                        },
                        ensure_ascii=False,
                    ),
                    "EOF",
                ]
            ),
            encoding="utf-8",
        )
        command_path.chmod(0o755)

        event = {"session_id": session_id, "transcript_path": str(transcript_path), "cwd": str(temp_root)}
        env = os.environ.copy()
        env["GRAPHITI_CLOSEOUT_SYNC"] = "1"
        env["GRAPHITI_CLOSEOUT_COMMAND"] = str(command_path)
        env["CLAUDE_PROJECT_DIR"] = str(PROJECT_ROOT)

        completed = subprocess.run(
            [str(HOOK_SCRIPT)],
            input=json.dumps(event, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=PROJECT_ROOT,
            env=env,
            check=True,
        )

        hook_output = json.loads(completed.stdout or "{}")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        args = json.loads(args_path.read_text(encoding="utf-8"))
        summary = summarize_state(state, limit=5, state_path=str(state_path))
        payload = json.loads(args[args.index("--body") + 1])

        return {
            "hook_output": hook_output,
            "summary": summary,
            "group_id": payload["audit"]["group_id"],
            "actor_cli": payload["actor_cli"],
            "episode_uuid": state["reports"][-1]["episode_uuid"],
            "args": args,
        }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_smoke(
        completion_text=args.completion_text,
        user_text=args.user_text,
        session_id=args.session_id,
        actor_cli=args.actor_cli,
        group_id_template=args.group_id_template,
    )

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Graphiti closeout smoke passed")
        print(f"- actor_cli: {result['actor_cli']}")
        print(f"- group_id: {result['group_id']}")
        print(f"- episode_uuid: {result['episode_uuid']}")
        print(f"- completed_count: {result['summary']['completed_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
