## 1. Governance Setup

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Confirm proposal scope against `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- [x] 1.2 Apply accepted suggestions from `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- [x] 1.3 Confirm single-CLI staged execution as the default closure model
- [x] 1.4 Validate OpenSpec change with `openspec validate plan-q2-optimization-closure-program --strict`

## 2. Phase A: Realtime Truth Audit
- [x] 2.1 Inventory realtime entrypoints, websocket routes, streaming services, and push paths
- [x] 2.2 Decide the canonical realtime transport selection policy
- [x] 2.3 Define the realtime delivery truth registry and closure evidence

## 3. Phase B: Backend Composition Closure
- [x] 3.1 Audit composition responsibilities between `web/backend/app/main.py` and `web/backend/app/app_factory.py`
- [x] 3.2 Select the canonical backend composition source-of-truth
- [x] 3.3 Define compatibility, migration, and retirement gates for duplicate composition paths

## 4. Phase C: Data Quality Unification
- [x] 4.1 Inventory current validators, monitors, and governance surfaces
- [x] 4.2 Define the canonical data quality model and component boundaries
- [x] 4.3 Define storage-specific quality concerns for dual-engine or multi-engine paths
- [x] 4.4 Define closure evidence for completeness, anomaly handling, and repair paths

## 5. Phase D: Trading Safety Contract
- [x] 5.1 Inventory current trading execution path, safeguards, and audit gaps
- [x] 5.2 Define idempotent submission, confirmation, durable audit storage, and retention rules
- [x] 5.3 Define pre-execution risk gates for configured capital or exposure thresholds
- [x] 5.4 Define what must be blocked before any production-grade trading claim

## 6. Phase E: Function Tree And Evidence Hardening
- [x] 6.1 Add criteria-backed completion semantics for function-tree governance
- [x] 6.2 Define the rule for safety-sensitive capability classification
- [x] 6.3 Bind completion claims to tests, docs, runtime verification, and safety evidence
- [x] 6.4 Normalize closure-wave evidence expectations in quality governance

## 7. Delivery Discipline
- [x] 7.1 Execute core closure work in a single CLI sequence
- [x] 7.2 Reassess whether multi-CLI work is safe only after core truths are locked
- [x] 7.3 Keep deferred items explicitly tagged as follow-up, not hidden inside Q2 closure claims
