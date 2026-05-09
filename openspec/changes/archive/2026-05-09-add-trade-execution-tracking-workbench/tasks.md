## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add proposal, design, and delta specs for execution tracking.
- [x] 1.2 Validate `add-trade-execution-tracking-workbench` with `--strict`.

## 2. Backend
- [x] 2.1 Add execution tracking list/detail/trigger route tests.
- [x] 2.2 Implement additive canonical execution tracking endpoints.
- [x] 2.3 Preserve bridge-only terminal results as `review_required`.

## 3. Frontend
- [x] 3.1 Add trade execution tracking API normalization.
- [x] 3.2 Add `/trade/execution` route and navigation entry.
- [x] 3.3 Add execution tracking workbench with filters, trigger form, evidence detail, and reconciliation jump.
- [x] 3.4 Add reconciliation reverse context link.

## 4. Verification
- [x] 4.1 Run backend route tests.
- [x] 4.2 Run frontend page tests.
- [x] 4.3 Run focused frontend lint/type/build or report existing blockers.
- [x] 4.4 Run GitNexus staged change detection before completion.
- [x] 4.5 Run Chromium E2E smoke for `/trade/execution` external trigger observation.
