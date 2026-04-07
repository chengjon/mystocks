# Change: Optimize ArtDeco Pages

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
ArtDeco 页面仍存在 mixed/mock 状态、交互不一致、测试覆盖不足的问题，需要作为前端主线治理。

## What Changes
- 优化 ArtDeco 页面实现与状态管理
- 收口页面级 mixed/mock 问题
- 补强页面级类型检查、smoke 和 E2E

## Impact
- Affected specs: frontend pages, page routing, page-level testing
- Affected code: `web/frontend/**`, `tests/e2e/**`, `docs/plans/frontend-page-optimization-list.md`
