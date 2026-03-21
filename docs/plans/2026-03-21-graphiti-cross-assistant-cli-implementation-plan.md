# Graphiti Cross-Assistant CLI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose Graphiti through one assistant-agnostic repo-local CLI contract with explicit scoped-preflight and generic-memory modes, while preserving Mongo as workflow truth.

**Architecture:** Keep the existing Graphiti adapter/service layer as the only transport/orchestration boundary and move assistant-specific behavior into thin wrappers. Extend the current transitional CLI surface first (`coordctl.py` / `maestro_collab.py`) so the same command contract can later be carried into `maestroctl.py` without re-implementing Graphiti logic.

**Tech Stack:** Python 3.12, argparse CLI, Mongo-backed `maestro.collab` services, Graphiti MCP over HTTP JSON-RPC, pytest, shell wrapper scripts.

---

已执行完成，实际实现与验证以以下路径为准：

- `scripts/runtime/maestro_collab.py`
- `src/services/maestro/collab/services/graphiti_preflight.py`
- `scripts/runtime/start_work_with_graphiti.sh`
- `.claude/hooks/user-prompt-submit-graphiti-preflight.sh`
- `tests/unit/services/maestro/test_graphiti_generic_memory_cli.py`
- `tests/unit/services/maestro/test_maestro_collab_preflight_cli.py`
- `tests/unit/services/maestro/test_graphiti_preflight_hook.py`

验证命令：

```bash
pytest --no-cov tests/unit/services/maestro/test_graphiti_adapter.py tests/unit/services/maestro/test_graphiti_preflight.py tests/unit/services/maestro/test_graphiti_generic_memory_cli.py tests/unit/services/maestro/test_graphiti_preflight_hook.py tests/unit/services/maestro/test_start_work_with_graphiti_script.py tests/unit/services/maestro/test_maestro_collab_preflight_cli.py tests/unit/services/maestro/test_task_report_graphiti_projection.py tests/unit/runtime/test_maestro_coordination_cli.py -q

openspec validate add-graphiti-cross-assistant-cli --strict

bash -n .claude/hooks/user-prompt-submit-graphiti-preflight.sh scripts/runtime/start_work_with_graphiti.sh
```
