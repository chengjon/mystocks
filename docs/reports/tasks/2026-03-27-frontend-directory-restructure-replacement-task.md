# Frontend Directory Restructure 替代任务说明

## 背景

原 `restructure-frontend-directory` 任务包仍有价值，但不能直接按旧 `7/92` checklist 继续，原因是：

- 当前 `web/frontend/src/views` 结构与目标结构差距仍大
- 但代码已经在多个阶段发生演进，原 checklist 的依赖关系、路径假设、页面数量和迁移顺序都存在漂移
- 如果机械续跑旧清单，极容易对当前已稳定的前端主线造成回退

## 当前现状简述

当前 `src/views` 仍同时包含：

- `artdeco-pages`
- `demo`
- `converted.archive`
- `freqtrade-demo`
- 多个历史域目录与 styles/composables 交叉结构

说明目录治理目标仍然成立，但执行计划必须重建。

## 新任务目标

不是“继续跑旧 92 项”，而是：

> 基于当前真实代码结构，重新完成前端目录现状盘点、活跃页/历史页分类，以及新的分批迁移计划。

## 为什么仍值得继续

- 该目标与当前项目目录治理主题直接一致
- 能持续降低前端结构复杂度
- 只要先做盘点和分批规划，就不会直接引入功能倒退

## 不再沿用的旧口径

- 旧 `7/92` checklist
- 历史页面数和固定迁移顺序
- 对 `src/shared/`、`deprecated/`、域目录数量的旧假设

## 建议新范围

### Stage 1：现状盘点

1. 盘点 `src/views` 当前实际目录树
2. 标记活跃页面、兼容保留页面、历史/示例页面
3. 盘点当前 shared 资产真实位置

### Stage 2：结构分类

1. 划分：
   - 活跃业务页
   - 历史归档页
   - demo/example 页
   - shared 组件/样式/composables
2. 找出“继续存在的合理性”与“可迁移候选”

### Stage 3：新批次设计

1. 设计新的迁移波次
2. 每个波次控制在可验证、可回滚范围
3. 明确每个波次的验证门禁：
   - 路由
   - E2E
   - visual
   - lint/type-check

## 明确不做

- 不直接大规模 `git mv`
- 不一次性改路由与目录
- 不在没有新批次设计的前提下启动迁移

## 建议输出物

- 一份前端目录现状盘点文档
- 一份活跃页/历史页/共享资产分类表
- 一份新的迁移批次计划

当前已完成的第一份输出物：

- [2026-03-27-frontend-directory-current-inventory.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-current-inventory.md)
- [2026-03-27-frontend-directory-restructure-batch-plan.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-restructure-batch-plan.md)
- [2026-03-27-frontend-directory-batch-a-active-route-truth-table.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-a-active-route-truth-table.md)
- [2026-03-27-frontend-directory-batch-b-risk-classification.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-risk-classification.md)
- [2026-03-27-frontend-directory-batch-b-freeze-list.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-freeze-list.md)
- [2026-03-27-frontend-directory-batch-b-migration-white-list.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-b-migration-white-list.md)
- [2026-03-27-frontend-directory-batch-c-pilot-design.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-batch-c-pilot-design.md)

## 建议审批口径

`同意执行 Batch C：白名单试点迁移方案设计`
