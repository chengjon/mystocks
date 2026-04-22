# Graphiti Closeout Hook Live Validation

- Date: `2026-04-22`
- Scope: `stop-graphiti-task-closeout`
- Validation Type: `live stop-hook -> real Graphiti remember -> real Graphiti search`

## Goal

Validate that the Stop hook can detect a real completion-style final assistant message, write a closeout record through the shared Graphiti CLI contract, and be verified through both local state and Graphiti search.

## Validation Input

- Session ID: `live-closeout-session-1`
- Completion phrase used: `收尾已完成`
- Group ID: `mystocks_spec_closeout_hook_live_20260422143500`
- Actor CLI: `closeout-live`

## Execution Path

1. Construct a real Stop event payload with transcript and cwd.
2. Invoke `.claude/hooks/stop-graphiti-task-closeout.sh`.
3. Force sync mode for deterministic validation using `GRAPHITI_CLOSEOUT_SYNC=1`.
4. Let the hook call the real shared CLI contract:
   `python scripts/runtime/coordctl.py graphiti remember ...`
5. Query Graphiti with:
   `python scripts/runtime/coordctl.py graphiti search ...`

## Local State Result

- Hook stdout: `{}`
- Local state status: `completed`
- Dedupe key: `live-closeout-session-1:assistant-live-closeout-1`
- Episode UUID: `4e514076-bf1e-4ab8-a982-6a0309364799`
- Ingest status at write time: `warming`

## Graphiti Search Result

- Server status: `ok`
- Search outcome: `hit`
- Search summary: `nodes hit=5, facts hit=5`
- Matched nodes count: `5`
- Matched facts count: `5`

## Verdict

The live validation passed.

The Stop hook wrote a real closeout episode into Graphiti and the written content was queryable immediately afterward. Although the local write result reported ingest status `warming`, the follow-up real search returned `hit`, so the end-to-end acceptance criterion is satisfied.
