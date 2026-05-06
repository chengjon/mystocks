## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Finalize the `trade-reconciliation-statement` capability delta for the statement surface and account descriptors.
  - Verified: the delta now defines a dedicated reconciliation surface, explicit account descriptors, and an account-aware internal statement projection separate from the history workbench.
- [x] 1.2 Finalize the `trade-reconciliation-statement` CSV import, deterministic matching, and CSV export requirements.
  - Verified: the delta now encodes `normalized_template`, `miniQMT` raw CSV normalization, deterministic one-to-one matching, and filtered CSV export semantics.
- [x] 1.3 Finalize the `frontend-routing` delta for the reconciliation route and trade navigation labels.
  - Verified: the delta now encodes `/trade/reconciliation` with `对账单` and preserves `/trade/history` as `交易历史`.

## 2. Validation And Closeout
- [x] 2.1 Run `openspec validate add-trade-reconciliation-statement --strict`.
  - Verified: `openspec validate add-trade-reconciliation-statement --strict` passed on `2026-05-07`.
- [x] 2.2 Fix any schema, structure, or requirement-format issues reported by validation.
  - Repo-truth result: no schema, structure, or requirement-format issues remained after strict validation.
- [x] 2.3 Confirm the change files remain limited to `openspec/changes/add-trade-reconciliation-statement/**`.
  - Verified: the finalized change scope remains proposal/design/spec deltas/tasks under `openspec/changes/add-trade-reconciliation-statement/`.
- [x] 2.4 Verify the final spec deltas still encode the approved `normalized_template`, `miniQMT`, and route-label contracts.
  - Verified: the trade-reconciliation delta and frontend-routing delta still encode `normalized_template`, `miniQMT`, `/trade/reconciliation -> 对账单`, and `/trade/history -> 交易历史`.
