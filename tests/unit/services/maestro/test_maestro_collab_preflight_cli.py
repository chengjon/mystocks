from __future__ import annotations

import contextlib

import scripts.runtime.maestro_collab as maestro_collab


class _FakeFacade:
    def run_graphiti_preflight(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        write_memory: bool = False,
        max_wait_seconds: int = 60,
    ) -> dict:
        return {
            "work_item_id": work_item_id,
            "actor_cli": actor_cli,
            "task_path": task_path,
            "write_memory": write_memory,
            "max_wait_seconds": max_wait_seconds,
            "server_status": "ok",
            "ingest_status": "warming",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=2",
        }

    def run_graphiti_remember(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        max_wait_seconds: int = 60,
    ) -> dict:
        return {
            "work_item_id": work_item_id,
            "actor_cli": actor_cli,
            "task_path": task_path,
            "max_wait_seconds": max_wait_seconds,
            "server_status": "ok",
            "ingest_status": "completed",
            "episode_uuid": "ep-301",
            "group_id": "mystocks_spec_workers",
        }

    def run_graphiti_generic_remember(
        self,
        *,
        actor_cli: str,
        group_id: str,
        name: str,
        body: str,
        max_wait_seconds: int = 60,
    ) -> dict:
        return {
            "actor_cli": actor_cli,
            "group_id": group_id,
            "name": name,
            "body": body,
            "max_wait_seconds": max_wait_seconds,
            "server_status": "ok",
            "ingest_status": "completed",
            "episode_uuid": "ep-401",
        }

    def run_graphiti_generic_search(
        self,
        *,
        actor_cli: str,
        query: str,
        group_ids: list[str],
        query_type: str = "all",
        max_nodes: int = 5,
        max_facts: int = 5,
    ) -> dict:
        return {
            "actor_cli": actor_cli,
            "query": query,
            "group_ids": group_ids,
            "query_type": query_type,
            "max_nodes": max_nodes,
            "max_facts": max_facts,
            "server_status": "ok",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=1",
        }


def test_maestro_collab_cli_builds_work_preflight_subcommand() -> None:
    parser = maestro_collab.build_parser()
    args = parser.parse_args(
        [
            "--mongo-uri",
            "mongodb://localhost:27017",
            "work",
            "preflight",
            "MT-300",
            "--actor-cli",
            "cli-3",
        ]
    )

    assert args.command == "work"
    assert args.work_command == "preflight"
    assert args.work_item_id == "MT-300"
    assert args.actor_cli == "cli-3"
    assert args.max_wait_seconds == 60


def test_maestro_collab_cli_can_run_work_preflight(monkeypatch, capsys) -> None:
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda args: _FakeFacade())

    assert (
        maestro_collab.main(
            [
                "--mongo-uri",
                "mongodb://localhost:27017",
                "work",
                "preflight",
                "MT-301",
                "--actor-cli",
                "cli-3",
                "--max-wait-seconds",
                "75",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "server_status" in output
    assert "warming" in output
    assert "75" in output


def test_maestro_collab_cli_builds_work_remember_subcommand() -> None:
    parser = maestro_collab.build_parser()
    args = parser.parse_args(
        [
            "--mongo-uri",
            "mongodb://localhost:27017",
            "work",
            "remember",
            "MT-302",
            "--actor-cli",
            "cli-4",
        ]
    )

    assert args.command == "work"
    assert args.work_command == "remember"
    assert args.work_item_id == "MT-302"
    assert args.actor_cli == "cli-4"
    assert args.max_wait_seconds == 60


def test_maestro_collab_cli_can_run_work_remember(monkeypatch, capsys) -> None:
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda args: _FakeFacade())

    assert (
        maestro_collab.main(
            [
                "--mongo-uri",
                "mongodb://localhost:27017",
                "work",
                "remember",
                "MT-302",
                "--actor-cli",
                "cli-4",
                "--max-wait-seconds",
                "45",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "episode_uuid" in output
    assert "ep-301" in output
    assert "45" in output


def test_maestro_collab_cli_builds_graphiti_preflight_subcommand() -> None:
    parser = maestro_collab.build_parser()
    args = parser.parse_args(
        [
            "--mongo-uri",
            "mongodb://localhost:27017",
            "graphiti",
            "preflight",
            "--work-item-id",
            "MT-500",
            "--actor-cli",
            "cli-5",
        ]
    )

    assert args.command == "graphiti"
    assert args.graphiti_command == "preflight"
    assert args.work_item_id == "MT-500"
    assert args.actor_cli == "cli-5"


def test_maestro_collab_cli_builds_graphiti_generic_remember_subcommand() -> None:
    parser = maestro_collab.build_parser()
    args = parser.parse_args(
        [
            "--mongo-uri",
            "mongodb://localhost:27017",
            "graphiti",
            "remember",
            "--group-id",
            "mystocks_spec_docs",
            "--name",
            "Architecture Note",
            "--body",
            "Document explicit Graphiti CLI usage.",
        ]
    )

    assert args.command == "graphiti"
    assert args.graphiti_command == "remember"
    assert args.group_id == "mystocks_spec_docs"
    assert args.name == "Architecture Note"


def test_maestro_collab_cli_can_run_graphiti_generic_remember(monkeypatch, capsys) -> None:
    monkeypatch.setattr(maestro_collab, "_build_graphiti_facade", lambda args: _FakeFacade())

    assert (
        maestro_collab.main(
            [
                "--mongo-uri",
                "mongodb://localhost:27017",
                "graphiti",
                "remember",
                "--actor-cli",
                "cli-5",
                "--group-id",
                "mystocks_spec_docs",
                "--name",
                "Architecture Note",
                "--body",
                "Document explicit Graphiti CLI usage.",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "ep-401" in output
    assert "mystocks_spec_docs" in output


def test_maestro_collab_cli_can_run_graphiti_search(monkeypatch, capsys) -> None:
    monkeypatch.setattr(maestro_collab, "_build_graphiti_facade", lambda args: _FakeFacade())

    assert (
        maestro_collab.main(
            [
                "--mongo-uri",
                "mongodb://localhost:27017",
                "graphiti",
                "search",
                "--actor-cli",
                "cli-6",
                "--query",
                "Graphiti workflow guide",
                "--group-id",
                "mystocks_spec_docs",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "search_outcome" in output
    assert "nodes hit=1, facts hit=1" in output


def test_maestro_collab_cli_help_includes_graphiti_examples(capsys) -> None:
    with contextlib.suppress(SystemExit):
        maestro_collab.main(["--help"])

    output = capsys.readouterr().out
    assert "coordctl.py graphiti preflight" in output
    assert "coordctl.py graphiti remember" in output
    assert "coordctl.py graphiti search" in output
