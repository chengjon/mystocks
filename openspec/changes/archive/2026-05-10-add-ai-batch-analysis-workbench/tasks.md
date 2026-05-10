## 1. OpenSpec
> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

- [x] 1.1 Add batch analysis capability deltas.
- [x] 1.2 Validate the change with `openspec validate add-ai-batch-analysis-workbench --strict`.

## 2. Backend
- [x] 2.1 Add canonical v1 batch analysis runtime/status/submit/detail/list routes.
- [x] 2.2 Add backend contract tests for route registration, runtime status, task creation, detail lookup, and safety semantics.

## 3. Frontend
- [x] 3.1 Add typed API client for batch analysis routes.
- [x] 3.2 Add `/ai/batch` workbench with runtime status, submit form, task table, and result summary.
- [x] 3.3 Add route/menu registration and unit/E2E tests.

## 4. Governance
- [x] 4.1 Update `FUNCTION_TREE.md` evidence for `7.2 批量分析`.
- [x] 4.2 Archive the OpenSpec change after implementation.
- [x] 4.3 Run targeted backend/frontend/E2E verification and GitNexus staged scope check.
