from __future__ import annotations

from scripts.runtime.local_tracker import build_parser, main


def test_local_tracker_cli_builds_expected_subcommands() -> None:
    parser = build_parser()
    args = parser.parse_args(["--sqlite-path", "tracker.db", "create", "--title", "First issue"])

    assert args.sqlite_path == "tracker.db"
    assert args.command == "create"
    assert args.title == "First issue"


def test_local_tracker_cli_can_create_list_and_update_state(tmp_path, capsys) -> None:
    sqlite_path = tmp_path / "tracker.db"

    assert main(["--sqlite-path", str(sqlite_path), "create", "--title", "First local issue"]) == 0
    create_output = capsys.readouterr().out
    assert "LOCAL-1" in create_output

    assert main(["--sqlite-path", str(sqlite_path), "list"]) == 0
    list_output = capsys.readouterr().out
    assert "LOCAL-1" in list_output
    assert "Todo" in list_output

    assert main(["--sqlite-path", str(sqlite_path), "update-state", "LOCAL-1", "Done"]) == 0
    update_output = capsys.readouterr().out
    assert "Done" in update_output

    assert main(["--sqlite-path", str(sqlite_path), "list"]) == 0
    final_list_output = capsys.readouterr().out
    assert "LOCAL-1" in final_list_output
    assert "Done" in final_list_output
