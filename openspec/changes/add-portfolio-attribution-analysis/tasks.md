## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add the `add-portfolio-attribution-analysis` proposal, design notes, tasks list, and `portfolio-attribution-analysis` capability delta
- [x] 1.2 Validate `add-portfolio-attribution-analysis` with `openspec validate --strict`

## 2. Backend Shared Attribution Engine

- [x] 2.1 Add shared attribution models, errors, and one canonical engine
- [x] 2.2 Add benchmark, industry, price, and factor-enrichment dependencies
- [x] 2.3 Add deterministic engine tests for Brinson breakdown, factor sections, and contributor ordering

## 3. Backend Domain Adapters And Routes

- [x] 3.1 Add backtest snapshot normalization into the shared attribution inputs
- [x] 3.2 Add trade portfolio snapshot normalization for current and date-scoped attribution
- [x] 3.3 Add `GET /api/v1/backtest/{backtest_id}/attribution`
- [x] 3.4 Add `GET /api/v1/positions/attribution` with optional `date=YYYY-MM-DD`
- [x] 3.5 Add contract tests for strategy hard-fail and trade stale/date semantics

## 4. Legacy Compatibility Alignment

- [ ] 4.1 Reconcile `perform_attribution_analysis(...)` as a legacy compatibility surface
- [ ] 4.2 Delegate current real and mock attribution helpers to the shared engine or mark them explicit legacy/demo fallback

## 5. Frontend Shared Attribution Surface

- [x] 5.1 Add shared attribution API client and canonical frontend types
- [x] 5.2 Add canonical attribution composable for loading, stale handling, and request-id capture
- [x] 5.3 Add shared attribution overview, Brinson, industry, factor, contributor, empty-state, and error-state components
- [x] 5.4 Add targeted frontend unit tests for shared attribution rendering and orchestration

## 6. Frontend Domain Shells

- [ ] 6.1 Wire attribution into the strategy/backtest shell for selected backtest-result snapshots
- [x] 6.2 Replace trade pseudo-attribution cards with the shared attribution surface in `Portfolio.vue`
- [ ] 6.3 Add current-vs-date-scoped trade attribution controls and shell-specific tests

## 7. Verification And Governance

- [x] 7.1 Run targeted backend attribution tests
- [x] 7.2 Run targeted frontend attribution unit tests
- [ ] 7.3 Run attribution E2E smoke for strategy and trade shells
- [ ] 7.4 Update `docs/FUNCTION_TREE.md` after both shells and both attribution types are verified
