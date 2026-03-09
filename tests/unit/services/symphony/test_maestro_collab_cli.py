from __future__ import annotations

from scripts.runtime.maestro_collab import build_parser, main


def test_maestro_collab_cli_builds_expected_subcommands() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--sqlite-path",
            "tracker.db",
            "assign",
            "MT-1",
            "--worker-cli",
            "cli-1",
        ]
    )

    assert args.sqlite_path == "tracker.db"
    assert args.command == "assign"
    assert args.issue_identifier == "MT-1"
    assert args.worker_cli == "cli-1"


def test_maestro_collab_cli_can_assign_and_read_state(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "tracker.db"

    assert (
        main(
            [
                "--sqlite-path",
                str(sqlite_path),
                "assign",
                "MT-1",
                "--worker-cli",
                "cli-1",
                "--assigned-by",
                "main",
                "--acceptance-summary",
                "ship it",
            ]
        )
        == 0
    )
    assign_output = capsys.readouterr().out
    assert "MT-1" in assign_output
    assert "cli-1" in assign_output

    assert main(["--sqlite-path", str(sqlite_path), "state", "MT-1"]) == 0
    state_output = capsys.readouterr().out
    assert "assigned_worker_cli" in state_output
    assert "cli-1" in state_output


def test_maestro_collab_cli_can_suggest_owner_from_task_and_ownership(tmp_path, capsys) -> None:
    ownership_path = tmp_path / ".FILE_OWNERSHIP"
    ownership_path.write_text(
        "\n".join(
            [
                "src/                               main      | 核心业务逻辑",
                "tests/                              cli-6     | 测试文件",
            ]
        ),
        encoding="utf-8",
    )
    task_path = tmp_path / "TASK.md"
    task_path.write_text(
        "- Verify tests/unit/services/symphony/test_status_api.py",
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--sqlite-path",
                str(tmp_path / "tracker.db"),
                "suggest",
                "--ownership-path",
                str(ownership_path),
                "--task-path",
                str(task_path),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "suggested_owner" in output
    assert "cli-6" in output
