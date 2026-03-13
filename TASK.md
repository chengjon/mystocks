# TASK.md

## Goal
对 ArtDeco 相关页面做页面优化、状态收口和测试补强。

## Branch
`dev-artdeco-pages-codex`

## Scope
- `web/frontend/src/views/**`
- `web/frontend/src/components/**`
- `web/frontend/src/composables/**`
- `web/frontend/src/router/**`
- `web/frontend/src/config/**`
- `web/frontend/tests/**`
- `tests/e2e/**`
- `docs/plans/frontend-page-optimization-list.md`

## Do Not Touch
- `web/backend/app/api/**`
- `src/adapters/**`
- `src/data_access/**`
- `src/storage/**`

## Required Reading
- `architecture/STANDARDS.md`
- `docs/FUNCTION_TREE.md`
- `docs/guides/AI_QUICK_START.md`
- `docs/plans/frontend-page-optimization-list.md`

## Deliverables
- 页面优化实现
- `real/mixed/mock` 状态收口建议或修复
- E2E / smoke / type-check 结果
- `TASK-REPORT.md`

## Acceptance
- 明确报告实际执行的前端测试与 E2E 结果
- 不越界修改后端契约
- 若 API 真值不明，记录阻塞并交给 API 分支

## Report Back
- 已完成项
- 阻塞项
- 风险项
- 验证命令与结果
