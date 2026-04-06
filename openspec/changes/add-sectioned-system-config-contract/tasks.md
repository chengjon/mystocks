## 1. Proposal Validation

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。

- [x] 1.1 Validate the mixed-boundary scope in proposal and design documents
- [x] 1.2 Define the `system-settings-contract` capability delta
- [x] 1.3 Run `openspec validate add-sectioned-system-config-contract --strict`

## 2. Future Implementation Plan
- [x] 2.1 Add canonical system-scoped read/write contracts for `general`
- [x] 2.2 Reuse the existing datasource config endpoints as the only datasource truth
- [x] 2.3 Reuse the existing user notification preferences endpoints as the only notification truth
- [x] 2.4 Add canonical system-scoped read/write contracts for `security`
- [x] 2.5 Update frontend composition services to expose section ownership and evidence metadata
- [x] 2.6 Remove page-level local-storage persistence only after section exit criteria are met

## 3. Governance Gates
- [x] 3.1 Verify no duplicate storage layer, shim persistence path, or `*_new` compatibility branch is introduced
- [x] 3.2 Verify deletion/retirement decisions include both code-path and function-tree judgments
- [x] 3.3 Verify metrics and UI labels separate `measured`, `inferred`, and `historical-baseline`
- [x] 3.4 Verify migration completion is evaluated per section, not by a vague page-level claim
