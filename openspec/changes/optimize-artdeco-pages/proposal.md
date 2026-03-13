# Change: Optimize ArtDeco Pages

## Why
ArtDeco 页面仍存在 mixed/mock 状态、交互不一致、测试覆盖不足的问题，需要作为前端主线治理。

## What Changes
- 优化 ArtDeco 页面实现与状态管理
- 收口页面级 mixed/mock 问题
- 补强页面级类型检查、smoke 和 E2E

## Impact
- Affected specs: frontend pages, page routing, page-level testing
- Affected code: `web/frontend/**`, `tests/e2e/**`, `docs/plans/frontend-page-optimization-list.md`
