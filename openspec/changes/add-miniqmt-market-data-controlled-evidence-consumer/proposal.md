# Change: Add miniQMT market-data controlled evidence consumer

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

miniQMT now defines a controlled evidence handoff for Market Data Platform datasets, where miniQMT publishes immutable dataset releases and MyStocks must prove it consumed those releases through real dry-run import evidence. MyStocks needs an explicit consumer-side boundary so development can accelerate without mixing miniQMT market-data promotion evidence with the existing miniQMT broker execution bridge.

## What Changes

- Add a MyStocks market-data consumer contract for miniQMT release datasets that requires explicit `dataset_version` binding and manifest/artifact hash verification.
- Add a dry-run import rehearsal contract that reads release artifacts, maps fields into MyStocks data classifications, and proves the rehearsal did not write formal business tables.
- Add a local PostgreSQL evidence ledger for MyStocks-side controlled evidence metadata, hashes, dry-run result summaries, and miniQMT preview/apply status.
- Add `mystocks_dry_run` `evidence.v1` JSON generation requirements compatible with miniQMT validation and promotion evidence apply.
- Align the generated evidence contract with upstream validator fields such as `related_function_tree_node` and `hash_or_size`, and define bundle mode against the upstream promotion bundle layout instead of an ad-hoc fixture format.
- Add fail-closed rules for implicit `latest`, missing identity fields, hash mismatch, raw/candidate/job usage, template-only evidence, and accidental formal writes.
- Keep miniQMT broker execution runtime specs separate from Market Data Platform dataset consumption.

## Impact

- Affected specs:
  - `market-data`
  - `data-sources`
  - `data-quality-governance`
- Affected code:
  - New miniQMT Market Data Platform adapter/client under `src/adapters/` or `src/services/market_data/`
  - New dry-run controlled evidence service under `src/services/market_data/`
  - New PostgreSQL evidence ledger migration/model
  - New CLI under `scripts/market_data/`
  - Focused tests under `tests/unit/` and `tests/integration/`
- Non-goals:
  - Do not let miniQMT write MyStocks PostgreSQL, TDengine, or Redis formal stores.
  - Do not treat `/api/v1/qmt/market-data/*` as the canonical market-data store.
  - Do not modify miniQMT broker execution submission/reconciliation contracts.
  - Do not automatically promote miniQMT datasets to `authoritative`.
