#!/usr/bin/env python3
"""Gate context-mode/GitNexus handoff evidence for agent workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


CODE_SUFFIXES = {
    ".bash",
    ".cjs",
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".mjs",
    ".py",
    ".pyi",
    ".sh",
    ".sql",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
    ".zsh",
}

CODE_PREFIXES = (
    ".claude/hooks/",
    ".githooks/",
    ".github/workflows/",
    "config/",
    "scripts/",
    "src/",
    "tests/",
    "web/backend/",
    "web/frontend/",
)

EXCLUDED_PATHS = {
    ".claude/edit_log.jsonl",
    ".claude/gitnexus-evidence.jsonl",
}

GITNEXUS_TOOL_PREFIX = "mcp__gitnexus__"
EVIDENCE_ACTIONS = {"context", "cypher", "detect_changes", "impact", "query", "rename"}
STRONG_EVIDENCE_ACTIONS = {"detect_changes", "impact", "rename"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def project_root_from(args: argparse.Namespace, event: dict[str, Any] | None = None) -> Path:
    candidates = [
        getattr(args, "project_root", None),
        (event or {}).get("cwd"),
        os.environ.get("CLAUDE_PROJECT_DIR"),
        os.getcwd(),
    ]
    for candidate in candidates:
        if candidate:
            return Path(str(candidate)).expanduser().resolve()
    return Path.cwd().resolve()


def evidence_path(project_root: Path) -> Path:
    return project_root / ".claude" / "gitnexus-evidence.jsonl"


def edit_log_path(project_root: Path) -> Path:
    return project_root / ".claude" / "edit_log.jsonl"


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                records.append(value)
    return records


def normalize_repo_path(path_value: str, project_root: Path | None = None) -> str:
    path_value = path_value.replace("\\", "/")
    if project_root:
        try:
            absolute = Path(path_value).expanduser()
            if absolute.is_absolute():
                return absolute.resolve().relative_to(project_root).as_posix()
        except (OSError, ValueError):
            pass
    return path_value.lstrip("./")


def is_code_like(path_value: str, project_root: Path | None = None) -> bool:
    normalized = normalize_repo_path(path_value, project_root)
    if normalized in EXCLUDED_PATHS:
        return False
    if normalized.endswith(".md") or normalized.startswith("docs/"):
        return False
    if normalized == ".claude/settings.json":
        return True
    if normalized.startswith(CODE_PREFIXES):
        return True
    return Path(normalized).suffix.lower() in CODE_SUFFIXES


def action_from_tool(tool_name: str) -> str:
    if tool_name.startswith(GITNEXUS_TOOL_PREFIX):
        return tool_name.removeprefix(GITNEXUS_TOOL_PREFIX)
    if "gitnexus" in tool_name:
        return tool_name.rsplit("_", 1)[-1]
    return tool_name


def extract_target(tool_input: dict[str, Any]) -> str:
    for key in ("target", "name", "query", "symbol_name", "symbol_uid", "file_path"):
        value = tool_input.get(key)
        if value:
            return str(value)
    return ""


def extract_risk(tool_response: Any) -> str:
    try:
        text = json.dumps(tool_response, ensure_ascii=False)
    except TypeError:
        text = str(tool_response)
    match = re.search(r"\b(CRITICAL|HIGH|MEDIUM|LOW)\b", text)
    return match.group(1) if match else ""


def response_success(tool_response: Any) -> bool:
    if isinstance(tool_response, dict):
        if tool_response.get("success") is False:
            return False
        if "error" in tool_response:
            return False
    try:
        text = json.dumps(tool_response, ensure_ascii=False)
    except TypeError:
        text = str(tool_response)
    return '"error"' not in text[:5000]


def recent_records(records: list[dict[str, Any]], hours: float) -> list[dict[str, Any]]:
    cutoff = utc_now() - timedelta(hours=hours)
    recent: list[dict[str, Any]] = []
    for record in records:
        timestamp = parse_time(str(record.get("timestamp", "")))
        if timestamp and timestamp >= cutoff:
            recent.append(record)
    return recent


def has_evidence(
    records: list[dict[str, Any]],
    *,
    session_id: str | None = None,
    max_age_hours: float = 24.0,
    strong_only: bool = True,
) -> bool:
    actions = STRONG_EVIDENCE_ACTIONS if strong_only else EVIDENCE_ACTIONS
    for record in recent_records(records, max_age_hours):
        if session_id and record.get("session_id") != session_id:
            continue
        if record.get("action") not in actions:
            continue
        if record.get("success") is False:
            continue
        return True
    return False


def current_staged_files(project_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(project_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def should_skip() -> bool:
    if os.environ.get("DISABLE_GITNEXUS_WORKFLOW_GATE") == "1":
        return True
    return "gitnexus-workflow-gate" in os.environ.get("SKIP", "")


def gate_mode(default: str) -> str:
    return os.environ.get("GITNEXUS_WORKFLOW_GATE_MODE", default).lower()


def emit_gate_failure(message: str, *, default_mode: str) -> int:
    mode = gate_mode(default_mode)
    if mode == "warn":
        print(f"[gitnexus-workflow-gate] WARNING: {message}", file=sys.stderr)
        return 0
    print(f"[gitnexus-workflow-gate] BLOCKED: {message}", file=sys.stderr)
    return 2


def record_evidence(args: argparse.Namespace) -> int:
    event = read_stdin_json()
    tool_name = str(event.get("tool_name") or "")
    if "gitnexus" not in tool_name:
        return 0

    action = action_from_tool(tool_name)
    if action not in EVIDENCE_ACTIONS:
        return 0

    project_root = project_root_from(args, event)
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    tool_response = event.get("tool_response", {})

    record = {
        "timestamp": iso_now(),
        "session_id": str(event.get("session_id") or "unknown"),
        "repo": str(project_root),
        "tool_name": tool_name,
        "action": action,
        "target": extract_target(tool_input),
        "scope": tool_input.get("scope", ""),
        "direction": tool_input.get("direction", ""),
        "base_ref": tool_input.get("base_ref", ""),
        "risk": extract_risk(tool_response),
        "success": response_success(tool_response),
    }
    append_jsonl(evidence_path(project_root), record)
    return 0


def stop_gate(args: argparse.Namespace) -> int:
    if should_skip():
        return 0
    event = read_stdin_json()
    if event.get("stop_hook_active") is True:
        return 0
    project_root = project_root_from(args, event)
    session_id = str(event.get("session_id") or "")
    if not session_id:
        return 0

    edits = read_jsonl(edit_log_path(project_root))
    code_edits = [
        record
        for record in edits
        if record.get("session_id") == session_id and is_code_like(str(record.get("file_path", "")), project_root)
    ]
    if not code_edits:
        return 0

    evidence = read_jsonl(evidence_path(project_root))
    if has_evidence(evidence, session_id=session_id, max_age_hours=float(args.max_age_hours), strong_only=True):
        return 0

    sample_paths = sorted({normalize_repo_path(str(record.get("file_path", "")), project_root) for record in code_edits})[:8]
    return emit_gate_failure(
        "code-like files were edited without same-session GitNexus impact/detect evidence. "
        f"Run GitNexus impact or detect_changes before closing out. Files: {', '.join(sample_paths)}",
        default_mode=args.default_mode,
    )


def pre_commit_gate(args: argparse.Namespace) -> int:
    if should_skip():
        return 0
    project_root = project_root_from(args)
    staged = current_staged_files(project_root)
    code_staged = [path for path in staged if is_code_like(path, project_root)]
    if not code_staged:
        print("[gitnexus-workflow-gate] No staged code-like files.")
        return 0

    evidence = read_jsonl(evidence_path(project_root))
    if has_evidence(evidence, max_age_hours=float(args.max_age_hours), strong_only=True):
        print("[gitnexus-workflow-gate] Recent GitNexus evidence found.")
        return 0

    sample_paths = ", ".join(code_staged[:8])
    return emit_gate_failure(
        "staged code-like files require recent GitNexus impact/detect evidence. "
        f"Run GitNexus impact or detect_changes first. Files: {sample_paths}",
        default_mode=args.default_mode,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record-evidence")
    record_parser.add_argument("--project-root")
    record_parser.set_defaults(func=record_evidence)

    stop_parser = subparsers.add_parser("stop-gate")
    stop_parser.add_argument("--project-root")
    stop_parser.add_argument("--max-age-hours", default=os.environ.get("GITNEXUS_EVIDENCE_MAX_AGE_HOURS", "24"))
    stop_parser.add_argument("--default-mode", choices=("block", "warn"), default="block")
    stop_parser.set_defaults(func=stop_gate)

    pre_commit_parser = subparsers.add_parser("pre-commit-gate")
    pre_commit_parser.add_argument("--project-root")
    pre_commit_parser.add_argument("--max-age-hours", default=os.environ.get("GITNEXUS_EVIDENCE_MAX_AGE_HOURS", "24"))
    pre_commit_parser.add_argument("--default-mode", choices=("block", "warn"), default="block")
    pre_commit_parser.set_defaults(func=pre_commit_gate)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
