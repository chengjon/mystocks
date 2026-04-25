# Batching Rules

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use these rules to split the audit into lightweight, repairable batches.

## Batch Size

Default batch size:

- 3 to 5 pages per batch

Do not create large batches that delay repair and verification.

If a module has fewer than 3 relevant pages, it may be merged with the nearest related route family or layout family.

If a module has more than 5 pages, split it into multiple batches using one of these dimensions:

- route family
- layout family
- interaction density
- shared component family

Core business modules may remain a standalone batch even when they contain only 1 or 2 pages if they are critical entry points or high-risk workbench surfaces.

## Grouping Priority

Group pages in this order:

1. same business module
2. same route family
3. same layout family
4. same component pattern family

Examples:

- `/market/*`
- `/risk/*`
- `/trade/*`
- `/watchlist/*`

Prefer grouping pages that share filters, tables, charts, cards, or detail layouts.

## Special Routes

Special routes must be handled explicitly:

- 404 pages
- redirect-only routes
- compatibility wrappers
- embedded shell routes
- ArtDeco route exceptions declared directly in router

Do not mix these blindly into a normal business-page batch. Mark them as special-case pages and batch them only when they are part of the requested scope.

Default handling:

- process them after canonical business-page batches
- prioritize them earlier only if the user explicitly requests them or they block a core navigation path
- when a special route only wraps a canonical page, audit the canonical page first

## Priority Rules

Treat these as higher priority when no user preference is given:

1. pages reachable from primary navigation
2. pages that serve as canonical entry points for a business domain
3. pages with dense user interaction or high operational risk
4. pages with tables, charts, filters, or forms that dominate the workflow
5. pages with known inconsistency or recent churn

When priority signals conflict, resolve in this order:

1. blocking or high-severity operational risk
2. primary navigation importance
3. canonical-entry importance
4. interaction density
5. recent churn or known inconsistency

## Canonical Page Rules

Before batching, verify the canonical page entry:

- prefer router truth and current active page entry
- do not assume wrapper or compatibility pages are the canonical source
- when in doubt, resolve via router definitions and current frontend structure guidance

## Global Batch Order

Unless the user specifies a different scope, run batches in this order:

1. primary navigation entry pages
2. core business workbench pages
3. dense analysis/detail pages
4. supporting settings and utility pages
5. special-case routes and compatibility pages

When route truth and ArtDeco page truth diverge, prioritize the canonical routed page first.

## Batch Naming

Use this naming pattern:

- `batch-id = [module]-batch-[nn]`

Examples:

- `market-batch-01`
- `trade-batch-02`
- `risk-batch-03`

Keep numbering stable within the current audit run.

## Batch Completion Standard

A batch is complete only when:

- all pages in the batch were audited
- findings were merged and deduplicated
- in-scope fixes were applied
- focused regression verification was recorded
- a batch report was produced

## Defer Rules

Defer an issue instead of forcing a fix when:

- it requires backend contract changes
- it requires product requirement clarification
- it implies architecture-level rework
- it conflicts with current project standards
- it touches unrelated page families outside the current batch

Deferred items must include:

- affected page
- severity
- reason for deferral
- dependency or blocking condition
- recommended next batch or owner

Deferred items should be reintroduced when the blocking dependency is resolved or when the next relevant page family batch begins.
