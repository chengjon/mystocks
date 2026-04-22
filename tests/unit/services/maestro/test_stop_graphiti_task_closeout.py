from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module():
    module_path = Path("/opt/claude/mystocks_spec/.claude/hooks/record_graphiti_closeout.py")
    spec = importlib.util.spec_from_file_location("record_graphiti_closeout", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


record_graphiti_closeout = _load_module()


def _write_transcript(path: Path, *, user_text: str, assistant_text: str, assistant_id: str = "assistant-1") -> None:
    lines = [
        {
            "type": "user",
            "timestamp": "2026-04-22T10:00:00Z",
            "message": {"content": [{"type": "text", "text": user_text}]},
        },
        {
            "type": "assistant",
            "timestamp": "2026-04-22T10:05:00Z",
            "uuid": assistant_id,
            "message": {
                "model": "gpt-5",
                "content": [{"type": "text", "text": assistant_text}],
            },
        },
    ]
    path.write_text("".join(json.dumps(line, ensure_ascii=False) + "\n" for line in lines), encoding="utf-8")


def _write_edit_log(path: Path, *, session_id: str, files: list[str]) -> None:
    rows = [{"session_id": session_id, "relative_path": file_path} for file_path in files]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _write_closeout_config(path: Path, *, actor_cli: str = "codex", group_id_template: str = "{project_name}_task_closeouts") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "actor_cli": actor_cli,
                "group_id_template": group_id_template,
                "positive_patterns": record_graphiti_closeout.DEFAULT_CONFIG["positive_patterns"],
                "negative_patterns": record_graphiti_closeout.DEFAULT_CONFIG["negative_patterns"],
                "verification_patterns": record_graphiti_closeout.DEFAULT_CONFIG["verification_patterns"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _make_fake_graphiti_command(path: Path, args_path: Path, *, episode_uuid: str = "ep-closeout-1", group_id: str = "mystocks_spec_task_closeouts") -> None:
    script = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f"python -c 'import json,sys; open({json.dumps(str(args_path))}, \"w\", encoding=\"utf-8\").write(json.dumps(sys.argv[1:], ensure_ascii=False))' \"$@\"",
            "cat <<'EOF'",
            json.dumps(
                {
                    "server_status": "ok",
                    "ingest_status": "completed",
                    "episode_uuid": episode_uuid,
                    "group_id": group_id,
                },
                ensure_ascii=False,
            ),
            "EOF",
        ]
    )
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)


def test_process_closeout_writes_graphiti_payload(monkeypatch, tmp_path: Path) -> None:
    session_id = "session-closeout-1"
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        user_text="请执行 update-frontend-data-governance-with-fincept-patterns",
        assistant_text="已完成\n- 验证: pytest tests/unit/services/maestro/test_stop_graphiti_task_closeout.py",
    )
    _write_edit_log(tmp_path / ".claude" / "edit_log.jsonl", session_id=session_id, files=["web/frontend/src/api/demo.ts"])
    _write_closeout_config(tmp_path / "config" / "hooks" / "graphiti-closeout.json", actor_cli="cli-from-config")

    command_path = tmp_path / "fake_graphiti.sh"
    args_path = tmp_path / "graphiti_args.txt"
    _make_fake_graphiti_command(command_path, args_path)
    monkeypatch.setenv("GRAPHITI_CLOSEOUT_COMMAND", str(command_path))

    event = {"session_id": session_id, "transcript_path": str(transcript_path)}
    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0

    args = json.loads(args_path.read_text(encoding="utf-8"))
    assert args[:4] == ["graphiti", "remember", "--actor-cli", "cli-from-config"]
    assert f"{tmp_path.name}_task_closeouts" in args

    body = args[args.index("--body") + 1]
    payload = json.loads(body)
    assert payload["event_type"] == "stop_hook_task_closeout"
    assert payload["completion_phrase"] == "已完成"
    assert payload["actor_cli"] == "cli-from-config"
    assert payload["changed_files"] == ["web/frontend/src/api/demo.ts"]
    assert payload["request_context"]["latest_user_message"] == "请执行 update-frontend-data-governance-with-fincept-patterns"
    assert payload["verification"]["assistant_reported_checks"] == [
        "- 验证: pytest tests/unit/services/maestro/test_stop_graphiti_task_closeout.py"
    ]

    state = json.loads((tmp_path / ".claude" / "graphiti-closeout-state.json").read_text(encoding="utf-8"))
    assert state["processed"] == [f"{session_id}:assistant-1"]
    assert state["reports"][-1]["status"] == "completed"
    assert state["reports"][-1]["episode_uuid"] == "ep-closeout-1"


def test_process_closeout_skips_negative_phrase(monkeypatch, tmp_path: Path) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        user_text="继续",
        assistant_text="尚未完成，待继续处理。",
    )
    command_path = tmp_path / "fake_graphiti.sh"
    args_path = tmp_path / "graphiti_args.txt"
    _make_fake_graphiti_command(command_path, args_path)
    monkeypatch.setenv("GRAPHITI_CLOSEOUT_COMMAND", str(command_path))

    event = {"session_id": "session-negative", "transcript_path": str(transcript_path)}
    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0
    assert not args_path.exists()
    assert not (tmp_path / ".claude" / "graphiti-closeout-state.json").exists()


def test_process_closeout_skips_when_no_completion_phrase(monkeypatch, tmp_path: Path) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        user_text="继续",
        assistant_text="我先整理上下文，下一步会继续实现。",
    )
    command_path = tmp_path / "fake_graphiti.sh"
    args_path = tmp_path / "graphiti_args.txt"
    _make_fake_graphiti_command(command_path, args_path)
    monkeypatch.setenv("GRAPHITI_CLOSEOUT_COMMAND", str(command_path))

    event = {"session_id": "session-no-trigger", "transcript_path": str(transcript_path)}
    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0
    assert not args_path.exists()
    assert not (tmp_path / ".claude" / "graphiti-closeout-state.json").exists()


def test_process_closeout_dedupes_same_final_message(monkeypatch, tmp_path: Path) -> None:
    session_id = "session-dedupe"
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        user_text="继续",
        assistant_text="任务完成\n- 验证: lint passed",
    )
    command_path = tmp_path / "fake_graphiti.sh"
    args_path = tmp_path / "graphiti_args.txt"
    _make_fake_graphiti_command(command_path, args_path)
    monkeypatch.setenv("GRAPHITI_CLOSEOUT_COMMAND", str(command_path))

    event = {"session_id": session_id, "transcript_path": str(transcript_path)}
    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0
    first_args = args_path.read_text(encoding="utf-8")

    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0
    second_args = args_path.read_text(encoding="utf-8")

    assert first_args == second_args
    state = json.loads((tmp_path / ".claude" / "graphiti-closeout-state.json").read_text(encoding="utf-8"))
    assert len(state["processed"]) == 1
    assert len(state["reports"]) == 1


def test_process_closeout_respects_configured_group_id_template(monkeypatch, tmp_path: Path) -> None:
    session_id = "session-closeout-config-group"
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        user_text="继续",
        assistant_text="任务完成\n- 验证: pytest done",
    )
    _write_closeout_config(
        tmp_path / "config" / "hooks" / "graphiti-closeout.json",
        actor_cli="cli-9",
        group_id_template="ops_{project_name}_closeouts",
    )

    command_path = tmp_path / "fake_graphiti.sh"
    args_path = tmp_path / "graphiti_args.txt"
    _make_fake_graphiti_command(command_path, args_path, group_id="ops_tmp_closeouts")
    monkeypatch.setenv("GRAPHITI_CLOSEOUT_COMMAND", str(command_path))

    event = {"session_id": session_id, "transcript_path": str(transcript_path)}
    assert record_graphiti_closeout.process_closeout(event, tmp_path) == 0

    args = json.loads(args_path.read_text(encoding="utf-8"))
    expected_group_id = "ops_" + tmp_path.name + "_closeouts"
    assert expected_group_id in args
    body = json.loads(args[args.index("--body") + 1])
    assert body["audit"]["group_id"] == expected_group_id
