# Change: add portfolio attribution analysis

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
`FUNCTION_TREE` still marks `3.3 回测分析 -> 归因分析` as unfinished. The repository has pseudo-attribution UI and legacy attribution helpers, but it does not yet provide a canonical, shared `Brinson + factor attribution` capability that closes both the strategy/backtest and trade/portfolio shells.

## What Changes
- Add a shared one-period attribution-analysis capability with:
  - `Brinson attribution`
  - `five-factor attribution`
- Lock the first-batch benchmark to `沪深300`.
- Lock the first-batch factor set to:
  - `size`
  - `value`
  - `momentum`
  - `volatility`
  - `quality`
- Add aligned v1 entry points for:
  - selected backtest-result snapshots
  - current portfolio snapshots
  - date-scoped historical portfolio snapshots
- Add one shared frontend attribution presentation/orchestration surface reused by both the strategy and trade shells.
- Keep one canonical attribution engine while preserving domain-specific strategy and trade entry shells.

## Impact
- Affected specs:
  - `portfolio-attribution-analysis`
- Affected code:
  - `web/backend/app/services/attribution/*`
  - `web/backend/app/api/v1/analysis/backtest.py`
  - `web/backend/app/api/v1/trading/positions.py`
  - `src/data_sources/real/composite_business.py`
  - `src/data_sources/mock/business_mock.py`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/*`
  - `web/frontend/src/views/trade/Portfolio.vue`
