# TASK.md

## Goal
盘点数据源、数据库、缓存和运行依赖，做清理与必要优化。

## Branch
`dev-data-db-audit-claude`

## Scope
- `src/adapters/**`
- `src/data_access/**`
- `src/storage/**`
- `src/core/**` 中与数据路由/存储直接相关部分
- `config/**`
- `scripts/database/**`
- `docs/architecture/**`
- `docs/deployment/**`
- `docs/operations/**`

## Do Not Touch
- `web/frontend/src/views/**`
- `.github/pull_request_template.md`

## Required Reading
- `architecture/STANDARDS.md`
- `docs/FUNCTION_TREE.md`
- `docs/guides/AI_QUICK_START.md`
- `docs/architecture/README.md`
- `docs/deployment/README.md`
- `docs/operations/README.md`

## Deliverables
- 数据源/数据库现状矩阵
- 冗余/失效/兼容保留项清单
- 必要清理或优化修复
- 验证结果
- `TASK-REPORT.md`

## Acceptance
- 明确区分“可删”“兼容保留”“待判定”
- 不顺手改前端页面
- 任何清理动作都要写清依据

## Report Back
- 资产盘点结果
- 清理建议
- 已实施修复
- 风险与回滚
- 验证命令与结果
