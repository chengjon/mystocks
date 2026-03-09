from pathlib import Path

from src.services.maestro.collab import (
    FileOwnershipIndex,
    OwnershipEntry,
    OwnershipSuggestionEngine,
    extract_task_path_hints,
    load_file_ownership,
)


def test_load_file_ownership_parses_owner_entries(tmp_path: Path) -> None:
    ownership_file = tmp_path / ".FILE_OWNERSHIP"
    ownership_file.write_text(
        "\n".join(
            [
                "# comment",
                "src/                               main      | 核心业务逻辑",
                "web/frontend/src/components/Charts/  cli-1     | K线图组件",
                "docs/guides/GPU_MONITORING*          cli-5     | GPU监控文档",
            ]
        ),
        encoding="utf-8",
    )

    entries = load_file_ownership(ownership_file)

    assert entries == [
        OwnershipEntry(pattern="src/", owner="main", note="核心业务逻辑"),
        OwnershipEntry(pattern="web/frontend/src/components/Charts/", owner="cli-1", note="K线图组件"),
        OwnershipEntry(pattern="docs/guides/GPU_MONITORING*", owner="cli-5", note="GPU监控文档"),
    ]


def test_owner_suggestion_engine_prefers_matching_owner_and_defaults_unknown_to_main(tmp_path: Path) -> None:
    ownership_file = tmp_path / ".FILE_OWNERSHIP"
    ownership_file.write_text(
        "\n".join(
            [
                "src/                               main      | 核心业务逻辑",
                "web/frontend/src/components/Charts/  cli-1     | K线图组件",
                "tests/                              cli-6     | 测试文件",
            ]
        ),
        encoding="utf-8",
    )

    engine = OwnershipSuggestionEngine(FileOwnershipIndex(load_file_ownership(ownership_file)))
    suggestion = engine.suggest(
        candidate_paths=[
            "web/frontend/src/components/Charts/ProChart.vue",
            "web/frontend/src/components/Charts/Indicator.vue",
            "unknown/file.txt",
        ]
    )

    assert suggestion["suggested_owner"] == "cli-1"
    assert suggestion["matched_paths"]["cli-1"] == [
        "web/frontend/src/components/Charts/ProChart.vue",
        "web/frontend/src/components/Charts/Indicator.vue",
    ]
    assert suggestion["unowned_paths"] == ["unknown/file.txt"]
    assert suggestion["fallback_owner"] == "main"


def test_extract_task_path_hints_reads_backticked_and_bare_paths(tmp_path: Path) -> None:
    task_file = tmp_path / "TASK.md"
    task_file.write_text(
        "\n".join(
            [
                "# TASK",
                "- Update `web/frontend/src/components/Charts/KLine.vue`",
                "- Verify tests/unit/services/symphony/test_status_api.py",
            ]
        ),
        encoding="utf-8",
    )

    hints = extract_task_path_hints(task_file)

    assert "web/frontend/src/components/Charts/KLine.vue" in hints
    assert "tests/unit/services/symphony/test_status_api.py" in hints


def test_owner_suggestion_engine_falls_back_to_main_when_top_owners_tie(tmp_path: Path) -> None:
    ownership_file = tmp_path / ".FILE_OWNERSHIP"
    ownership_file.write_text(
        "\n".join(
            [
                "web/frontend/src/components/Charts/  cli-1     | K线图组件",
                "tests/                              cli-6     | 测试文件",
            ]
        ),
        encoding="utf-8",
    )

    engine = OwnershipSuggestionEngine(FileOwnershipIndex(load_file_ownership(ownership_file)))
    suggestion = engine.suggest(
        candidate_paths=[
            "web/frontend/src/components/Charts/ProChart.vue",
            "tests/unit/services/symphony/test_status_api.py",
        ]
    )

    assert suggestion["suggested_owner"] == "main"


def test_extract_task_path_hints_ignores_non_repo_slash_phrases(tmp_path: Path) -> None:
    task_file = tmp_path / "TASK.md"
    task_file.write_text(
        "\n".join(
            [
                "# TASK",
                "- Status: Now/Next/Blocked",
                "- Topic: ownership/DDL",
                "- Update tests/unit/services/symphony/test_status_api.py",
            ]
        ),
        encoding="utf-8",
    )

    hints = extract_task_path_hints(task_file)

    assert "Now/Next/Blocked" not in hints
    assert "ownership/DDL" not in hints
    assert "tests/unit/services/symphony/test_status_api.py" in hints
