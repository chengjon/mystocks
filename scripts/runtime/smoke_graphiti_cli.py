from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.runtime import coordctl
from scripts.runtime.graphiti_smoke_common import run_coordctl_json
from src.utils.cli_error_output import (
    print_cli_error,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a repo-local Graphiti CLI smoke flow.")
    parser.add_argument("--actor-cli", required=True)
    parser.add_argument("--group-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-wait-seconds", type=int, default=60)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = run_smoke(
            actor_cli=args.actor_cli,
            group_id=args.group_id,
            name=args.name,
            body=args.body,
            query=args.query,
            max_wait_seconds=args.max_wait_seconds,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except RuntimeError as exc:
        print_cli_error(exc)
        return 1


def run_smoke(
    *,
    actor_cli: str,
    group_id: str,
    name: str,
    body: str,
    query: str,
    max_wait_seconds: int = 60,
) -> dict[str, object]:
    remember_payload = _run_coordctl_json(
        [
            "graphiti",
            "remember",
            "--actor-cli",
            actor_cli,
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
        ]
    )
    search_payload = _run_coordctl_json(
        [
            "graphiti",
            "search",
            "--actor-cli",
            actor_cli,
            "--query",
            query,
            "--group-id",
            group_id,
            "--output",
            "json",
        ]
    )

    return {
        "actor_cli": actor_cli,
        "group_id": group_id,
        "name": name,
        "query": query,
        "remember_server_status": remember_payload.get("server_status"),
        "remember_ingest_status": remember_payload.get("ingest_status"),
        "episode_uuid": remember_payload.get("episode_uuid"),
        "search_server_status": search_payload.get("server_status"),
        "search_outcome": search_payload.get("search_outcome"),
        "search_summary": search_payload.get("search_summary"),
        "matched_nodes_count": search_payload.get("matched_nodes_count"),
        "matched_facts_count": search_payload.get("matched_facts_count"),
    }


def _run_coordctl_json(argv: list[str]) -> dict[str, object]:
    return run_coordctl_json(argv, coordctl_main=coordctl.main)


if __name__ == "__main__":
    raise SystemExit(main())
