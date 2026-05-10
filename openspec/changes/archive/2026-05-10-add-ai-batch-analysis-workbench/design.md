## Context
> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

The 7.2 function-tree node is already represented by batch backtest, stock screening, and automation modules, but those capabilities are split across strategy and watchlist surfaces. The first batch should provide a canonical AI observation layer that summarizes batch work without claiming production automation or replacing existing engines.

## Goals
- Expose runtime readiness and supported batch operation types.
- Allow a user to submit a bounded batch analysis request and receive task evidence, per-symbol results, summary metrics, warnings, and safety semantics.
- Provide an AI-domain route `/ai/batch` that can be tested independently.

## Non-Goals
- No production scheduler mutation.
- No live streaming progress.
- No broker/trade execution.
- No replacement of existing backtest, screener, or strategy executor modules.

## Decisions
- Use in-memory runtime registration for first-batch task evidence, matching the 7.1 runtime registry pattern.
- Keep the canonical API under the existing v1 strategy router prefix as `/api/v1/strategies/batch-analysis/*`.
- Return deterministic synthetic summaries when external data or heavy engines are unavailable, while clearly labeling the output as analytical evidence.
