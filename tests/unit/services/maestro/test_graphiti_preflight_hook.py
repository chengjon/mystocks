from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def test_graphiti_preflight_hook_injects_summary_for_start_work_prompt(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "",
                "- Issue Identifier: `MT-400`",
            ]
        ),
        encoding="utf-8",
    )
    command_path = tmp_path / "fake_preflight.sh"
    command_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "cat <<'EOF'",
                '{"server_status":"ok","ingest_status":"warming","search_summary":"nodes hit=1, facts hit=2"}',
                "EOF",
            ]
        ),
        encoding="utf-8",
    )
    command_path.chmod(0o755)

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = "/opt/claude/mystocks_spec"
    env["GRAPHITI_PREFLIGHT_COMMAND"] = str(command_path)

    completed = subprocess.run(
        ["/opt/claude/mystocks_spec/.claude/hooks/user-prompt-submit-graphiti-preflight.sh"],
        input=json.dumps({"prompt": "请按你当前 worktree 的 TASK.md 开工。"}),
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )

    payload = json.loads(completed.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "Graphiti preflight" in context
    assert "server_status=ok" in context
    assert "ingest_status=warming" in context
    assert "nodes hit=1, facts hit=2" in context


def test_graphiti_preflight_hook_skips_non_matching_prompt(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = "/opt/claude/mystocks_spec"

    completed = subprocess.run(
        ["/opt/claude/mystocks_spec/.claude/hooks/user-prompt-submit-graphiti-preflight.sh"],
        input=json.dumps({"prompt": "这是一个普通问题"}),
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )

    assert completed.stdout.strip() == ""


def test_graphiti_preflight_hook_accepts_graphiti_marker_prompt(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "",
                "- Issue Identifier: `MT-401`",
            ]
        ),
        encoding="utf-8",
    )
    command_path = tmp_path / "fake_preflight.sh"
    command_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "cat <<'EOF'",
                '{"server_status":"ok","ingest_status":"warming","search_summary":"nodes hit=2, facts hit=1"}',
                "EOF",
            ]
        ),
        encoding="utf-8",
    )
    command_path.chmod(0o755)

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = "/opt/claude/mystocks_spec"
    env["GRAPHITI_START_WORK_COMMAND"] = str(command_path)

    completed = subprocess.run(
        ["/opt/claude/mystocks_spec/.claude/hooks/user-prompt-submit-graphiti-preflight.sh"],
        input=json.dumps({"prompt": "@graphiti 先补一下这个任务的上下文"}),
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )

    payload = json.loads(completed.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    assert "server_status=ok" in context
    assert "nodes hit=2, facts hit=1" in context
