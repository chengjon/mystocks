from __future__ import annotations

import json

import scripts.runtime.smoke_graphiti_closeout_hook as smoke_closeout


def test_run_smoke_executes_stop_hook_end_to_end() -> None:
    result = smoke_closeout.run_smoke(
        completion_text="已完成\n- 验证: pytest smoke",
        user_text="请执行 closeout smoke",
        session_id="smoke-session-test",
        actor_cli="smoke-cli",
        group_id_template="smoke_{project_name}_closeouts",
    )

    assert result["hook_output"] == {}
    assert result["actor_cli"] == "smoke-cli"
    assert result["episode_uuid"] == "ep-smoke-1"
    assert result["summary"]["completed_count"] == 1
    assert result["summary"]["failed_count"] == 0
    assert result["group_id"].startswith("smoke_")

    args = result["args"]
    assert args[:4] == ["graphiti", "remember", "--actor-cli", "smoke-cli"]
    payload = json.loads(args[args.index("--body") + 1])
    assert payload["completion_phrase"] == "已完成"
