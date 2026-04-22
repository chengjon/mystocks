from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import scripts.runtime.inspect_graphiti_closeout_state as inspector


def test_summarize_state_counts_successes_and_failures() -> None:
    state = {
        "processed": ["s1:m1", "s2:m2"],
        "reports": [
            {
                "recorded_at": "2026-04-22T10:00:00",
                "status": "completed",
                "session_id": "s1",
                "episode_uuid": "ep-1",
                "group_id": "g-1",
            },
            {
                "recorded_at": "2026-04-22T11:00:00",
                "status": "failed",
                "session_id": "s2",
                "completion_phrase": "任务完成",
                "error": "graphiti command failed",
            },
        ],
    }

    summary = inspector.summarize_state(state, limit=5, state_path=".claude/graphiti-closeout-state.json")

    assert summary["processed_count"] == 2
    assert summary["report_count"] == 2
    assert summary["completed_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["latest_reported_at"] == "2026-04-22T11:00:00"
    assert summary["recent_failures"][0]["session_id"] == "s2"
    assert summary["recent_successes"][0]["episode_uuid"] == "ep-1"


def test_render_text_includes_failure_and_success_sections() -> None:
    summary = {
        "state_file": ".claude/graphiti-closeout-state.json",
        "processed_count": 1,
        "report_count": 2,
        "completed_count": 1,
        "failed_count": 1,
        "latest_reported_at": "2026-04-22T11:00:00",
        "recent_failures": [
            {
                "recorded_at": "2026-04-22T11:00:00",
                "session_id": "s2",
                "completion_phrase": "任务完成",
                "error": "graphiti command failed",
            }
        ],
        "recent_successes": [
            {
                "recorded_at": "2026-04-22T10:00:00",
                "session_id": "s1",
                "episode_uuid": "ep-1",
                "group_id": "g-1",
            }
        ],
    }

    output = inspector.render_text(summary)

    assert "Graphiti Closeout State" in output
    assert "Recent Failures:" in output
    assert "graphiti command failed" in output
    assert "Recent Successes:" in output
    assert "episode=ep-1" in output


def test_main_outputs_json_summary(tmp_path: Path) -> None:
    state_path = tmp_path / "graphiti-closeout-state.json"
    state_path.write_text(
        json.dumps(
            {
                "processed": ["s1:m1"],
                "reports": [
                    {
                        "recorded_at": "2026-04-22T10:00:00",
                        "status": "completed",
                        "session_id": "s1",
                        "episode_uuid": "ep-1",
                        "group_id": "g-1",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert inspector.main(["--state-file", str(state_path), "--output", "json"]) == 0

    payload = json.loads(stdout.getvalue())
    assert payload["completed_count"] == 1
    assert payload["failed_count"] == 0
    assert payload["state_file"] == str(state_path)
