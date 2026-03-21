from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def test_start_work_with_graphiti_script_runs_preflight_with_optional_write_memory(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "",
                "- Issue Identifier: `MT-410`",
            ]
        ),
        encoding="utf-8",
    )
    args_path = tmp_path / "args.json"
    command_path = tmp_path / "fake_preflight.sh"
    command_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"printf '%s\\n' \"$@\" | python -c 'import json,sys; open({json.dumps(str(args_path))}, \"w\", encoding=\"utf-8\").write(json.dumps(sys.stdin.read().splitlines()))'",
                "cat <<'EOF'",
                '{"server_status":"ok","ingest_status":"completed","search_summary":"nodes hit=1, facts hit=2","episode_uuid":"ep-410"}',
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
        ["/opt/claude/mystocks_spec/scripts/runtime/start_work_with_graphiti.sh", "--write-memory"],
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env=env,
        check=True,
    )

    payload = json.loads(completed.stdout)
    args = json.loads(args_path.read_text(encoding="utf-8"))
    assert payload["episode_uuid"] == "ep-410"
    assert args[0] == "MT-410"
    assert "--write-memory" in args
