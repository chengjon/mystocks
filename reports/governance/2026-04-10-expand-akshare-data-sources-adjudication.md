# Adjudication: expand-akshare-data-sources

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `expand-akshare-data-sources` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `expand-akshare-data-sources` active, but treat it as a partially landed AkShare market-expansion line with drifted execution artifacts rather than a literally completed checklist.

## Why It Should Stay

- The change is structurally valid: `openspec validate expand-akshare-data-sources --strict` passes.
- Current repo evidence shows broad real implementation already exists across adapter, backend API, registry, and tests:
  - `src/adapters/akshare/market_adapter/`
  - `web/backend/app/api/akshare_market/{sse,szse,stock_info,fund_flow,boards,analysis}.py`
  - `config/data_sources_registry.yaml`
  - `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part{1,2,3}.py`
  - `tests/api/file_tests/test_akshare_market_api.py`
- The capability boundary is still meaningful: this change is the active OpenSpec line for the expanded AkShare market/news/fund-flow/analysis surface, not a stale historical proposal.

## Why It Must Not Be Read As Complete

Current repo truth does not support a full completion reading:

- `tasks.md` is internally contradictory. Sections `1` to `5` are marked complete, then sections `3` to `5` are duplicated later as unchecked items.
- The unchecked tail introduces additional scope such as `stock_hot_follow_xq`, `stock_board_change_em`, `stock_news_main_em`, `stock_zt_pool_em`, `stock_dt_pool_em`, `stock_strong_pool_em`, `stock_weak_pool_em`, `stock_changes_em`, and `stock_new_em`; current repo search does not show matching implementation evidence outside the task text itself.
- The proposal's affected-code note is drifted. It points at `web/backend/app/api/efinance.py`, while current repo truth routes this capability through `web/backend/app/api/akshare_market/`.
- Existing tests demonstrate meaningful coverage presence, but they do not prove full integration, performance, data-quality, or end-to-end closure for the whole advertised surface.

## Current Repo-Truth Reading

- Treat sections `1` to `5` of the task list as "substantially landed with real code evidence", not as a proof that every item has been freshly verified in the current workspace.
- Treat the later unchecked sections as unresolved scope candidates, not as proof that the entire change is still largely unimplemented.
- Treat the current change as the canonical active line for AkShare market-surface expansion, but only within the already evidenced adapter/API/registry slice.

## Relationship To Current Trunks

- This change should be read as an execution line under the existing data-source and market-data trunks, not as a competing source of truth.
- Current repo truth for implementation location is the modular AkShare adapter and `akshare_market` backend API surface.
- Any future closure must respect the migration/debt-governance rules in `architecture/STANDARDS.md`, especially the prohibition on treating drifted task text as authoritative current state.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not mark it completed from the existence of broad adapter and API coverage alone.
- Do not continue the original checklist mechanically.
- If execution resumes, first restate the unresolved current-truth slice:
  - verify whether the unchecked "行情和新闻数据扩充" scope is still desired
  - decide whether `stock_hot_follow_xq` / `stock_board_change_em` belong to this change or to a narrower follow-on line
  - confirm which existing endpoints are covered by real integration tests versus file-level smoke tests
  - require concrete verification before claiming performance, data-quality, or end-to-end completion
