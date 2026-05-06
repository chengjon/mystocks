## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [ ] 1.1 Finalize the `trade-reconciliation-statement` capability delta for the statement surface and account descriptors.
- [ ] 1.2 Finalize the `trade-reconciliation-statement` CSV import, deterministic matching, and CSV export requirements.
- [ ] 1.3 Finalize the `frontend-routing` delta for the reconciliation route and trade navigation labels.

## 2. Validation And Closeout
- [ ] 2.1 Run `openspec validate add-trade-reconciliation-statement --strict`.
- [ ] 2.2 Fix any schema, structure, or requirement-format issues reported by validation.
- [ ] 2.3 Confirm the change files remain limited to `openspec/changes/add-trade-reconciliation-statement/**`.
- [ ] 2.4 Verify the final spec deltas still encode the approved `normalized_template`, `miniQMT`, and route-label contracts.
