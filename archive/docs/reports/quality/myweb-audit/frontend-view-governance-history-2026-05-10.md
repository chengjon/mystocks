# 前端 Vue 页面清理/治理历史文档索引

> **用途**: 本文件汇总本项目历次前端 Vue 页面清理和治理工作的关键文档、执行结果与当前状态，供后续治理批次参考。
>
> **注意**: 文内统计值、完成状态和结论均为历史快照，不得直接当作当前事实。执行前应重新盘点。

**生成日期**: 2026-05-10
**Branch observed**: `wip/root-dirty-20260403`

---

## 时间线总览

| 轮次 | 时间 | 主题 | 核心文档 |
|------|------|------|----------|
| 第一轮 | 2026-01 | 页面重新编排 | `docs/reports/PAGES_REORGANIZATION_PROPOSAL.md` |
| 第二轮 | 2026-01 | ArtDeco 设计系统清理 | `docs/reports/ARTDECO_COMPLETE_CLEANUP_COMPLETION.md` |
| 第三轮 | 2026-03 ~ 04 | 前端目录重构 + 死代码清除 | 见下方详细列表 |
| 第四轮 | 2026-04 ~ 05 | myweb-audit 页面逐个审计 | `docs/reports/quality/myweb-audit/audit-20260426-02/` |
| 当前 | 2026-05 | View Governance 设计 spec | `docs/superpowers/specs/2026-05-10-frontend-view-governance-design.md` |

---

## 第一轮：页面重新编排（2026-01）

**文档**: `docs/reports/PAGES_REORGANIZATION_PROPOSAL.md`

- 覆盖 31 个前端页面
- 核心问题：MainLayout 承载 61.3%（19 个）页面，功能混杂
- 方案：按业务场景分组（DashboardLayout / MarketLayout / DataLayout / StrategyLayout / RiskLayout）

---

## 第二轮：ArtDeco 清理（2026-01）

**文档**: `docs/reports/ARTDECO_COMPLETE_CLEANUP_COMPLETION.md`

- 日期：2026-01-07
- 状态：已完成
- 清理范围：
  - CSS 类名：737 → 0
  - 样式导入：74 → 0
  - 组件引用：41 → 0
  - klinechart K 线图功能完整保留
  - 前端服务正常运行

---

## 第三轮：前端目录重构 + 死代码清除（2026-03 ~ 04）

### 核心文档链

| 文档 | 日期 | 内容 |
|------|------|------|
| `docs/reports/tasks/2026-03-27-frontend-directory-current-inventory.md` | 03-27 | **基线盘点**：25 个顶层目录、44 个根层 `.vue` 文件，活跃路由仅 34 个落点 |
| `docs/reports/tasks/2026-03-27-frontend-directory-restructure-batch-plan.md` | 03-27 | 目录重构批计划 |
| `docs/plans/2026-03-02-frontend-navigation-ssot-refactor-implementation-plan.md` | 03-02 | 前端导航 SSOT 重构实施计划 |
| `docs/reports/FRONTEND_STRUCTURE_REPO_TRUTH_STATUS_2026-04-06.md` | 04-06 | **阶段总结**：Phase 0-5 已关闭，通过路由/布局账本对齐和 Playwright 验证矩阵完成 |
| `docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md` | 04-07 | **结构审计**：确认入口真相 `index.html → main-standard.ts → router/index.ts`，逐目录判定 |
| `docs/reports/2026-04-07-duplicate-page-functional-status.md` | 04-07 | **双分叉页面审计**：`Phase4Dashboard` 和 `TechnicalAnalysis` 各有两个版本并存 |
| `docs/reports/2026-04-07-views-composables-status.md` | 04-07 | **composables 状态**：15 个文件逐个判定 |
| `docs/reports/cleanup/DELETION-CANDIDATES.md` | 04-07 | **删除候选清单**：5 个后端模块（已执行完毕） |
| `docs/reports/2026-04-07-phase3-execution-preconditions.md` | 04-07 | Phase 3 执行前置条件 |
| `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md` | 04-07 | 项目状态与技术债优先级 |

### 关键结论（04-07 审计）

**前端入口真相**:

```
index.html → /src/main-standard.ts → /src/router/index.ts
```

**目录状态判定（04-07 快照）**:

| 目录 | 判定 | 备注 |
|------|------|------|
| `views/market` / `data` / `watchlist` / `strategy` / `trade` / `risk` / `system` | 有效 | router 直接导入 |
| `views/artdeco-pages` | 有效，非唯一真相源 | router 仍导入多个 tab/page |
| `views/announcement` | 有效 | router 306 行直接导入 |
| `views/stocks` | 失效主路由层，兼容保留 | watchlist/Screener 包装引用 |
| `views/monitoring` | 历史路由目标 + 测试守护 | router 未导入 |
| `views/composables` | root-level legacy view support | 9 个 legacy support，2 个 duplicate-candidate |
| `views/demo` / `freqtrade-demo` / `tdxpy-demo` | 实验/演示 | 不在主路由 |

**双分叉页面**:

| 对象 | root 版状态 | demo 版状态 |
|------|------------|------------|
| `Phase4Dashboard` | 失效但兼容/历史保留 | 实验/示例资产 |
| `TechnicalAnalysis` | duplicate-candidate + test-guarded | 与 `views/technical/` 版并存 |

### 目录重构执行状态（04-06 总结）

- Phase 0-5 已在本地仓库关闭
- Phase 4 通过路由/布局账本对齐完成（非二次 router 重写）
- Phase 5 通过 Playwright 验证矩阵 + real-read 证据关闭
- Phase 6-9 仍 open（依赖正式 review、merge、deploy 等外部门禁）

---

## 第四轮：myweb-audit 页面逐个审计（2026-04 ~ 05）

**目录**: `docs/reports/quality/myweb-audit/audit-20260426-02/`

- 按页面逐个审计，覆盖 market / data / strategy / trade / risk / system 全域
- 包含 secondary line 批次审计（batch 30-49+）
- 覆盖静态 shell truth、payload normalization、runtime status 等多维度
- 相关进度总结：`docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`

---

## 当前状态：View Governance Spec（2026-05）

**设计 spec**: `docs/superpowers/specs/2026-05-10-frontend-view-governance-design.md`
**Review**: `docs/superpowers/specs/2026-05-10-frontend-view-governance-design-review.md`
**Inventory**: `docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`

### 2026-05-10 代码库实测数据

| 指标 | 数值 |
|------|------|
| 总 Vue 文件数（views/） | 271 |
| 路由动态导入（canonical views） | 42 |
| 顶层子目录数 | 28 |
| 无路由引用的目录 | `advanced-analysis`, `demo`, `freqtrade-demo`, `tdxpy-demo`, `trading`, `trading-decision`, `trade-management`, `monitoring`, `stocks`, `technical`, `settings`, `examples`, `errors`, `components` |
| 菜单域（MenuConfig.ts） | 7 个 |
| 菜单叶子项 | 36+ |
| archive 目录 | 尚未创建 |
| `import.meta.glob` 模式 | 0（不存在） |

### 与历史数据的对比

| 指标 | 03-27 盘点 | 05-10 实测 | 变化 |
|------|-----------|-----------|------|
| 顶层目录数 | 25 | 28 | +3 |
| 根层 .vue 文件 | 44 | 未单独统计 | — |
| 活跃路由落点 | 34 | 42 | +8（新增页面） |

---

## 可直接复用的历史结论

1. **入口真相已锁定**：`index.html → main-standard.ts → router/index.ts`，无需重新确认
2. **MenuConfig.ts 已确认为菜单 SSOT**：7 域 36+ 叶子项
3. **composables 状态表可继承**：04-07 逐文件判定仍有参考价值，但需重新验证消费关系
4. **双分叉页面已知**：`Phase4Dashboard` 和 `TechnicalAnalysis` 仍需处理
5. **后端死代码已清除**：`DELETION-CANDIDATES.md` 中 5 个目标目录已不存在
