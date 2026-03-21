from __future__ import annotations

import io
import json
import os
import subprocess

from scripts.runtime import smoke_graphiti_cli


def test_run_smoke_executes_remember_then_search_via_shared_cli(monkeypatch) -> None:
    calls: list[list[str]] = []

    def _fake_run(argv: list[str]) -> dict[str, object]:
        calls.append(argv)
        if argv[:2] == ["graphiti", "remember"]:
            return {
                "server_status": "ok",
                "ingest_status": "completed",
                "episode_uuid": "ep-smoke",
                "group_id": "mystocks_spec_smoke",
            }
        return {
            "server_status": "ok",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=1",
            "matched_nodes_count": 1,
            "matched_facts_count": 1,
        }

    monkeypatch.setattr(smoke_graphiti_cli, "_run_coordctl_json", _fake_run)

    summary = smoke_graphiti_cli.run_smoke(
        actor_cli="cli-smoke",
        group_id="mystocks_spec_smoke",
        name="Smoke Memory",
        body="Graphiti smoke body",
        query="Smoke Memory",
    )

    assert summary["remember_server_status"] == "ok"
    assert summary["remember_ingest_status"] == "completed"
    assert summary["search_outcome"] == "hit"
    assert calls[0][:2] == ["graphiti", "remember"]
    assert calls[1][:2] == ["graphiti", "search"]


def test_main_emits_json_summary(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke_graphiti_cli,
        "run_smoke",
        lambda **_: {
            "remember_server_status": "ok",
            "remember_ingest_status": "completed",
            "search_outcome": "hit",
        },
    )

    assert smoke_graphiti_cli.main(
        [
            "--actor-cli",
            "cli-smoke",
            "--group-id",
            "mystocks_spec_smoke",
            "--name",
            "Smoke Memory",
            "--body",
            "Graphiti smoke body",
            "--query",
            "Smoke Memory",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["remember_server_status"] == "ok"


def test_smoke_graphiti_cli_script_runs_standalone_with_external_command(tmp_path) -> None:
    fake_command = tmp_path / "fake_coordctl.sh"
    fake_command.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "if [ \"$2\" = \"remember\" ]; then",
                "  cat <<'EOF'",
                '  {"server_status":"ok","ingest_status":"completed","episode_uuid":"ep-standalone","group_id":"mystocks_spec_smoke"}',
                "EOF",
                "else",
                "  cat <<'EOF'",
                '  {"server_status":"ok","search_outcome":"hit","search_summary":"nodes hit=1, facts hit=1","matched_nodes_count":1,"matched_facts_count":1}',
                "EOF",
                "fi",
            ]
        ),
        encoding="utf-8",
    )
    fake_command.chmod(0o755)

    env = os.environ.copy()
    env["GRAPHITI_SMOKE_COMMAND"] = str(fake_command)

    completed = subprocess.run(
        [
            "python",
            "/opt/claude/mystocks_spec/scripts/runtime/smoke_graphiti_cli.py",
            "--actor-cli",
            "cli-smoke",
            "--group-id",
            "mystocks_spec_smoke",
            "--name",
            "Smoke Memory",
            "--body",
            "Graphiti smoke body",
            "--query",
            "Smoke Memory",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["episode_uuid"] == "ep-standalone"
    assert payload["search_outcome"] == "hit"
