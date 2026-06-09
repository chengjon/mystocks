# 2026-03-27 Frontend Directory Restructure 新批次计划

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> 基线来源：
> - [2026-03-27-frontend-directory-current-inventory.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-current-inventory.md)
> - [2026-03-27-frontend-directory-restructure-replacement-task.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-restructure-replacement-task.md)
>
> 目标：不沿用旧 `7/92` checklist，基于当前真实代码结构重建一套可验证、可回滚、不会破坏现有主线的目录治理批次计划。

## 0. 当前进度

截至 2026-03-27，已完成：

- Batch A：活跃页真值清单
- Batch B：风险分级 / 冻结列表 / 迁移白名单
- Batch C：`market/data` 试点方案设计
- Batch D：共享资产盘点
- 试点实施：
  - `market` 3 页入口已切到 `views/market/*`
  - `data` 4 页入口已切到 `views/data/*`

当前未完成的关键问题已不再是“能不能继续改路由”，而是：

- 是否值得继续把主体实现从 `artdeco-pages` 内迁到目标域目录
- 是否应停在“主线路由入口归位”这一层

## 1. 计划原则

### 1.1 先分类，后迁移

- 先确认“活跃页 / 历史页 / demo 页 / 共享资产”
- 再决定是否迁移
- 禁止把文件移动本身当成进度

### 1.2 活跃路由优先保护

- 当前活跃路由组件 34 个中，31 个仍位于 `artdeco-pages`
- 因此 `artdeco-pages` 目前是主线真值容器，不是待直接清空的历史目录
- 所有批次都以“不破坏现有活跃路由”为前提

### 1.3 小批次、强验证

每个批次都必须满足：

- 改动面可控
- 可单独验证
- 出问题可快速回退

### 1.4 不直接执行旧目标结构

以下旧目标不能直接当成现状假设：

- “8 个域目录 + deprecated”
- “共享资产已准备迁移到 `src/shared/`”
- “可以直接逐条执行旧 92 项迁移清单”

## 2. 当前真实约束

### 2.1 现有活跃路由分布

当前活跃路由 import 分布：

- `artdeco-pages`: 31
- `Login.vue`: 1
- `NotFound.vue`: 1
- `TradingDashboard.vue`: 1
- `announcement`: 1
- `stocks`: 1
- `strategy`: 1

### 2.2 当前高风险区

- `src/views` 根层仍有 44 个 `.vue` 文件
- `artdeco-pages` 下有 89 个 `.vue` 文件
- `demo` / `converted.archive` / `freqtrade-demo` 仍与活跃结构并存
- `views/components` / `views/composables` / `views/styles` 与 `src/components` 并存，边界不清

### 2.3 当前不应立即做的事

- 不做全量 `git mv`
- 不一次性改路由
- 不先提取所有 shared 资产
- 不先删除 `artdeco-pages`

## 3. 新批次设计

## Batch A：活跃页真值清单

### 目标

建立“当前真正在用的页面清单”，作为后续一切迁移的保护边界。

### 内容

1. 从 `router/index.ts` 提取全部活跃路由组件
2. 输出“活跃路由 -> 当前文件路径 -> 目标域归属”映射表
3. 标记这些页面中：
   - 已在目标域目录内
   - 仍在 `artdeco-pages`
   - 仍在根层或旧目录

### 输出物

- `活跃路由真值表`
- `活跃页面保护名单`

### 验证

- 活跃路由总数与 `router/index.ts` 一致
- 不遗漏 `Login.vue` / `NotFound.vue` / `TradingDashboard.vue` / `Screener.vue` / `BacktestGPU.vue`

---

## Batch B：历史/示例页隔离清单

### 目标

不直接迁移历史页，只先建立“可隔离候选”清单。

### 内容

1. 分类以下目录中的页面：
   - `demo`
   - `examples`
   - `converted.archive`
   - `freqtrade-demo`
   - `tdxpy-demo`
2. 标记：
   - 历史保留
   - demo 资产
   - 待隔离
   - 仍被引用（禁止移动）

### 输出物

- `历史/示例页分类表`
- `可进入 deprecated 候选名单`

### 验证

- 对每个候选页至少确认一次引用路径/路由/字符串引用
- 不因为“看起来没用”就直接判定可删

---

## Batch C：根层视图清理清单

### 目标

先解释 44 个根层 `.vue` 文件为何仍存在，而不是立刻移动。

### 内容

1. 对根层 `.vue` 文件做分类：
   - 活跃入口
   - 历史兼容页
   - demo/test 页
   - 迁移候选
2. 明确哪些文件必须保留在根层
3. 明确哪些文件可进入后续迁移波次

### 输出物

- `根层视图文件分类表`

### 验证

- `Login.vue` / `NotFound.vue` 不被误判迁移
- 所有仍被路由直接使用的根层页面都被标记为活跃入口或兼容保留

---

## Batch D：共享资产盘点

### 目标

建立 shared 资产迁移前的依赖地图，不立即移动文件。

### 内容

1. 盘点：
   - `src/views/components`
   - `src/views/composables`
   - `src/views/styles`
   - `src/components/...`
2. 标记哪些是：
   - 真实共享
   - 页面私有
   - 历史残留
3. 输出依赖关系

### 输出物

- `共享组件清单`
- `共享 composables 清单`
- `共享 styles 清单`
- `共享资产候选迁移地图`

### 验证

- 不在未识别依赖前做 `src/shared/` 提取

---

## Batch E：试点迁移域

### 目标

只选择一个域作为迁移试点，验证新方法是否安全。

### 推荐候选

优先顺序：

1. `market`
2. `strategy`

### 原因

- `market` 当前已有独立域目录基础，最适合做试点
- `strategy` 业务重要，但链路复杂，更适合作为第二个试点

### 内容

1. 为选定域建立“目标结构图”
2. 仅迁移少量明确页面
3. 保持路由兼容
4. 先验证 lint / type-check / E2E / visual

### 输出物

- `试点域迁移方案`
- `试点域验证清单`

---

## 4. 建议执行顺序

### 推荐顺序

1. Batch A：活跃页真值清单
2. Batch B：历史/示例页隔离清单
3. Batch C：根层视图清理清单
4. Batch D：共享资产盘点
5. Batch E：试点迁移域

### 不建议跳步

- 如果没有完成 Batch A，就不要动路由
- 如果没有完成 Batch D，就不要动 `src/shared`
- 如果没有完成试点迁移，就不要启动全域目录重构

## 5. 每批次门禁

每个批次结束至少要满足：

1. `git diff --check`
2. 相关范围 `lint`
3. 相关范围 `type-check`
4. 相关 E2E / smoke / visual（若涉及页面）
5. 变更说明文档更新

## 6. 建议下一步审批口径

基于当前进度，建议下一步批准为：

`同意执行 market/data 主体实现内迁 M1：先迁 5 个单依赖页面`

当前评估结论已形成：

- 5 个页面适合继续内迁
- 1 个页面建议延后
- 1 个页面建议止步于入口归位

参考文档：

- [2026-03-27-frontend-directory-market-data-body-migration-assessment.md](/opt/claude/mystocks_spec/docs/reports/tasks/2026-03-27-frontend-directory-market-data-body-migration-assessment.md)
