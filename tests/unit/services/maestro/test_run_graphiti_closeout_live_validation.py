from __future__ import annotations

import json
import subprocess
from pathlib import Path

import scripts.runtime.run_graphiti_closeout_live_validation as live_validation


def test_run_live_validation_assembles_state_and_search_result(tmp_path: Path) -> None:
    def fake_run(cmd, **kwargs):
        if str(cmd[0]).endswith("stop-graphiti-task-closeout.sh"):
            root = Path(json.loads(kwargs["input"])["cwd"])
            state_path = root / ".claude" / "graphiti-closeout-state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "processed": ["live-closeout-session-1:assistant-live-closeout-1"],
                        "reports": [
                            {
                                "recorded_at": "2026-04-22T15:10:32",
                                "status": "completed",
                                "session_id": "live-closeout-session-1",
                                "dedupe_key": "live-closeout-session-1:assistant-live-closeout-1",
                                "completion_phrase": "收尾已完成",
                                "summary": "收尾已完成",
                                "changed_files_count": 1,
                                "episode_uuid": "ep-live-1",
                                "group_id": "mystocks_spec_closeout_hook_live_20260422150000",
                                "ingest_status": "warming",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(cmd, 0, stdout="{}\n", stderr="")
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps(
                {
                    "server_status": "ok",
                    "search_outcome": "hit",
                    "search_summary": "nodes hit=2, facts hit=2",
                    "matched_nodes_count": 2,
                    "matched_facts_count": 2,
                },
                ensure_ascii=False,
            ),
            stderr="",
        )

    result = live_validation.run_live_validation(
        timestamp="20260422150000",
        session_id="live-closeout-session-1",
        actor_cli="closeout-live",
        completion_text="收尾已完成",
        user_text="请执行真实 closeout hook 验收",
        run_command=fake_run,
    )

    assert result["hook_stdout"] == "{}"
    assert result["group_id"] == "mystocks_spec_closeout_hook_live_20260422150000"
    assert result["state_report"]["episode_uuid"] == "ep-live-1"
    assert result["search"]["search_outcome"] == "hit"


def test_render_report_contains_core_fields() -> None:
    report = live_validation.render_report(
        {
            "hook_stdout": "{}",
            "group_id": "mystocks_spec_closeout_hook_live_20260422150000",
            "state_report": {
                "status": "completed",
                "completion_phrase": "收尾已完成",
                "episode_uuid": "ep-live-1",
                "ingest_status": "warming",
            },
            "search": {
                "server_status": "ok",
                "search_outcome": "hit",
                "search_summary": "nodes hit=2, facts hit=2",
                "matched_nodes_count": 2,
                "matched_facts_count": 2,
            },
        },
        timestamp="20260422150000",
        session_id="live-closeout-session-1",
        actor_cli="closeout-live",
    )

    assert "Graphiti Closeout Hook Live Validation" in report
    assert "ep-live-1" in report
    assert "nodes hit=2, facts hit=2" in report
