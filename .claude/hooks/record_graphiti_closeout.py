#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "actor_cli": "codex",
    "group_id_template": "{project_name}_task_closeouts",
    "positive_patterns": [
        {"label": "收尾已完成", "pattern": r"收尾已完成"},
        {"label": "任务完成", "pattern": r"任务完成"},
        {"label": "已完成", "pattern": r"(^|\n)\s*已完成"},
        {"label": "完成了", "pattern": r"完成了"},
        {"label": "已修复", "pattern": r"已修复|修复完成"},
        {"label": "done", "pattern": r"\bdone\b"},
        {"label": "finished", "pattern": r"\bfinished\b"},
        {"label": "task completed", "pattern": r"\btask\s+completed\b"},
    ],
    "negative_patterns": [r"未完成", r"尚未完成", r"not\s+completed", r"待继续"],
    "verification_patterns": [
        r"pytest",
        r"vitest",
        r"playwright",
        r"\blint\b",
        r"\bbuild\b",
        r"\btest",
        r"\be2e\b",
        r"\bsmoke\b",
        r"验证",
        r"通过",
        r"pm2",
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_closeout_config(project_root: Path) -> dict[str, Any]:
    config_path_raw = os.environ.get("GRAPHITI_CLOSEOUT_CONFIG", "").strip()
    config_path = Path(config_path_raw).expanduser() if config_path_raw else project_root / "config" / "hooks" / "graphiti-closeout.json"

    config = dict(DEFAULT_CONFIG)
    loaded = load_json(config_path)
    if not isinstance(loaded, dict):
        return config

    for key in ("actor_cli", "group_id_template"):
        value = loaded.get(key)
        if isinstance(value, str) and value.strip():
            config[key] = value.strip()

    for key in ("positive_patterns", "negative_patterns", "verification_patterns"):
        value = loaded.get(key)
        if isinstance(value, list) and value:
            config[key] = value
    return config


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            try:
                rows.append(json.loads(raw))
            except Exception:
                continue
    return rows


def _extract_text_parts(content: Any) -> str:
    text_parts: list[str] = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    text_parts.append(text.strip())
    elif isinstance(content, str) and content.strip():
        text_parts.append(content.strip())
    return "\n".join(text_parts).strip()


def extract_last_message(transcript_path: Path, role: str) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for obj in load_jsonl(transcript_path):
        if obj.get("type") != role:
            continue
        message = obj.get("message") if isinstance(obj.get("message"), dict) else {}
        text = _extract_text_parts(message.get("content"))
        message_id = obj.get("uuid") or message.get("id") or obj.get("id")
        if not message_id:
            seed = f"{obj.get('timestamp', '')}::{role}::{text}".encode("utf-8", "ignore")
            message_id = hashlib.sha1(seed).hexdigest()[:16]
        last = {
            "id": str(message_id),
            "timestamp": obj.get("timestamp") or "",
            "model": message.get("model") or "",
            "text": text,
        }
    return last


def detect_completion_phrase(text: str, config: dict[str, Any]) -> str | None:
    lowered = text.lower()
    for pattern in config.get("negative_patterns", []):
        if not isinstance(pattern, str):
            continue
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return None
    for item in config.get("positive_patterns", []):
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        pattern = item.get("pattern")
        if not isinstance(label, str) or not isinstance(pattern, str):
            continue
        if re.search(pattern, text, flags=re.IGNORECASE):
            return label
    return None


def short_summary(text: str) -> str:
    if not text.strip():
        return "(no assistant text)"
    for line in text.splitlines():
        stripped = line.strip(" -*")
        if stripped and not stripped.startswith("#"):
            return stripped[:180]
    return text.strip()[:180]


def extract_verification(text: str, config: dict[str, Any]) -> list[str]:
    verification_lines: list[str] = []
    seen: set[str] = set()
    verification_patterns = [pattern for pattern in config.get("verification_patterns", []) if isinstance(pattern, str)]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if not any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in verification_patterns):
            continue
        if stripped in seen:
            continue
        seen.add(stripped)
        verification_lines.append(stripped[:220])
        if len(verification_lines) >= 8:
            break
    return verification_lines


def read_changed_files(project_root: Path, session_id: str) -> list[str]:
    edit_log = project_root / ".claude" / "edit_log.jsonl"
    files: list[str] = []
    seen: set[str] = set()
    for row in load_jsonl(edit_log):
        if row.get("session_id") != session_id:
            continue
        file_path = row.get("relative_path") or row.get("file_path") or row.get("absolute_path")
        if not isinstance(file_path, str) or not file_path:
            continue
        normalized = file_path
        try:
            path_obj = Path(file_path)
            if path_obj.is_absolute():
                normalized = str(path_obj.resolve().relative_to(project_root.resolve()))
        except Exception:
            normalized = file_path
        if normalized in seen:
            continue
        seen.add(normalized)
        files.append(normalized)
        if len(files) >= 20:
            break
    return files


def load_state(state_file: Path) -> dict[str, Any]:
    if not state_file.exists():
        return {"processed": [], "reports": []}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {"processed": [], "reports": []}
    if not isinstance(data, dict):
        return {"processed": [], "reports": []}
    if not isinstance(data.get("processed"), list):
        data["processed"] = []
    if not isinstance(data.get("reports"), list):
        data["reports"] = []
    return data


def save_state(state_file: Path, state: dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    processed = state.get("processed", [])
    if isinstance(processed, list) and len(processed) > 2000:
        state["processed"] = processed[-1000:]
    reports = state.get("reports", [])
    if isinstance(reports, list) and len(reports) > 500:
        state["reports"] = reports[-200:]
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def determine_actor_cli() -> str:
    actor_cli = os.environ.get("GRAPHITI_CLOSEOUT_ACTOR_CLI", "").strip()
    if actor_cli:
        return actor_cli
    return ""


def resolve_actor_cli(config: dict[str, Any]) -> str:
    actor_cli = determine_actor_cli()
    if actor_cli:
        return actor_cli
    configured_actor = config.get("actor_cli")
    if isinstance(configured_actor, str) and configured_actor.strip():
        return configured_actor.strip()
    return "codex"


def resolve_group_id(project_root: Path, config: dict[str, Any]) -> str:
    override = os.environ.get("GRAPHITI_CLOSEOUT_GROUP_ID", "").strip()
    if override:
        return override

    template = config.get("group_id_template")
    if not isinstance(template, str) or not template.strip():
        template = "{project_name}_task_closeouts"
    try:
        return template.format(project_name=project_root.name, project_root=str(project_root.resolve()))
    except Exception:
        return f"{project_root.name}_task_closeouts"


def build_closeout_payload(
    *,
    project_root: Path,
    config: dict[str, Any],
    session_id: str,
    transcript_path: Path,
    completion_phrase: str,
    assistant: dict[str, Any],
    user_message: dict[str, Any],
    changed_files: list[str],
) -> dict[str, Any]:
    recorded_at = datetime.now().isoformat(timespec="seconds")
    summary = short_summary(str(assistant.get("text") or ""))
    verification = extract_verification(str(assistant.get("text") or ""), config)
    dedupe_key = f"{session_id}:{assistant.get('id', '')}"
    group_id = resolve_group_id(project_root, config)
    return {
        "event_type": "stop_hook_task_closeout",
        "session_id": session_id,
        "actor_cli": resolve_actor_cli(config),
        "project_root": str(project_root.resolve()),
        "summary": summary,
        "completion_phrase": completion_phrase,
        "changed_files": changed_files,
        "verification": {
            "assistant_reported_checks": verification,
            "assistant_model": assistant.get("model") or "",
            "assistant_timestamp": assistant.get("timestamp") or "",
        },
        "request_context": {
            "latest_user_message": (user_message.get("text") or "")[:500],
            "transcript_path": str(transcript_path),
        },
        "audit": {
            "dedupe_key": dedupe_key,
            "assistant_message_id": assistant.get("id") or "",
            "recorded_at": recorded_at,
            "hook_name": "stop-graphiti-task-closeout",
            "hook_version": "1",
            "group_id": group_id,
        },
    }


def build_graphiti_command(project_root: Path) -> list[str]:
    override = os.environ.get("GRAPHITI_CLOSEOUT_COMMAND", "").strip()
    if override:
        return shlex.split(override)
    return [sys.executable, str(project_root / "scripts" / "runtime" / "coordctl.py")]


def write_graphiti_closeout(project_root: Path, payload: dict[str, Any], *, max_wait_seconds: int = 60) -> dict[str, Any]:
    command = build_graphiti_command(project_root)
    name = f"Task closeout {payload['session_id']}"
    group_id = str(payload.get("audit", {}).get("group_id") or f"{project_root.name}_task_closeouts")
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    completed = subprocess.run(
        [
            *command,
            "graphiti",
            "remember",
            "--actor-cli",
            str(payload["actor_cli"]),
            "--group-id",
            group_id,
            "--name",
            name,
            "--body",
            body,
            "--max-wait-seconds",
            str(max_wait_seconds),
            "--output",
            "json",
        ],
        text=True,
        capture_output=True,
        cwd=project_root,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "graphiti command failed")
    result = json.loads(completed.stdout or "{}")
    if not result.get("episode_uuid") or not result.get("group_id"):
        raise RuntimeError("graphiti command returned incomplete durable metadata")
    return result


def append_report(state: dict[str, Any], report: dict[str, Any]) -> None:
    reports = state.setdefault("reports", [])
    if not isinstance(reports, list):
        reports = []
        state["reports"] = reports
    reports.append(report)


def process_closeout(event: dict[str, Any], project_root: Path) -> int:
    session_id = str(event.get("session_id") or "unknown")
    config = load_closeout_config(project_root)
    transcript_path_raw = event.get("transcript_path")
    if not isinstance(transcript_path_raw, str) or not transcript_path_raw:
        return 0

    transcript_path = Path(transcript_path_raw).expanduser()
    assistant = extract_last_message(transcript_path, "assistant")
    if not assistant:
        return 0

    completion_phrase = detect_completion_phrase(str(assistant.get("text") or ""), config)
    if not completion_phrase:
        return 0

    state_file = project_root / ".claude" / "graphiti-closeout-state.json"
    state = load_state(state_file)
    dedupe_key = f"{session_id}:{assistant.get('id', '')}"
    processed = state.get("processed", [])
    if isinstance(processed, list) and dedupe_key in processed:
        return 0

    user_message = extract_last_message(transcript_path, "user")
    changed_files = read_changed_files(project_root, session_id)
    payload = build_closeout_payload(
        project_root=project_root,
        config=config,
        session_id=session_id,
        transcript_path=transcript_path,
        completion_phrase=completion_phrase,
        assistant=assistant,
        user_message=user_message,
        changed_files=changed_files,
    )

    report = {
        "recorded_at": payload["audit"]["recorded_at"],
        "status": "failed",
        "session_id": session_id,
        "dedupe_key": dedupe_key,
        "completion_phrase": completion_phrase,
        "summary": payload["summary"],
        "changed_files_count": len(changed_files),
    }

    try:
        result = write_graphiti_closeout(project_root, payload)
        processed_list = state.setdefault("processed", [])
        if isinstance(processed_list, list):
            processed_list.append(dedupe_key)
        report.update(
            {
                "status": "completed",
                "episode_uuid": result.get("episode_uuid"),
                "group_id": result.get("group_id"),
                "ingest_status": result.get("ingest_status"),
            }
        )
    except Exception as exc:
        report["error"] = str(exc)[:500]

    append_report(state, report)
    save_state(state_file, state)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-json", required=True)
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args(argv)

    event_path = Path(args.event_json)
    event = load_json(event_path)
    try:
        if event_path.exists():
            event_path.unlink()
    except Exception:
        pass

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        return 0
    return process_closeout(event, project_root)


if __name__ == "__main__":
    raise SystemExit(main())
