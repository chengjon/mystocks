# ArtDeco Web 设计优化建议（供审核）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


- 日期：2026-03-31
- 状态：2026-04-01 已按当前代码与文档链复核
- 项目：`/opt/claude/mystocks_spec`
- 依据：当前 ArtDeco 文档体系与运行时代码

---

## 1. 审核范围与依据文档

本建议严格以以下文档体系为基线，不另立风格。

> 路径口径说明：本文统一使用 `docs/guides/web/*` 作为 canonical 文档路径；兼容入口（如 `docs/guides/*`）仅用于历史链接兼容，不作为主引用。

1. 上手入口：`docs/guides/web/ARTDECO_START_HERE.md`
2. 总目录：`docs/guides/web/ARTDECO_MASTER_INDEX.md`
3. 统一规格：`docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
4. 开发指南：`docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
5. 样式真值：`docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
6. 全景目录：`web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
7. 系统架构：`docs/api/ArtDeco_System_Architecture_Summary.md`
8. 设计令牌：`web/frontend/src/styles/artdeco-tokens.scss`
9. 实施基准：`docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

> 目标：在不偏离当前 ArtDeco Fintech 风格与架构约束的前提下，提升一致性、可维护性、可读性与可交付性。

---

## 2. 总体判断

当前阶段最优策略不是“推翻重做 UI”，而是执行 **治理一致性强化**：

1. 视觉一致性：Token、字体、间距、语义色落地率
2. 运行时架构一致性：模板化工作台、直接 Tab 容器、总控容器边界清晰
3. 组件一致性：reusable assets、page-level shared fragments、domain tab blocks 分层清晰
4. 页面一致性：关键页面的信息层级、工作台节奏与可观测性一致

---

## 3. 优化建议（按优先级）

### 3.1 P0：规范入口与执行口径统一

**建议**
- 将 `ARTDECO_MASTER_INDEX` 与 `ARTDECO_FINTECH_UNIFIED_SPEC` 作为规范入口组合。
- 在需求评审、PR 模板、变更说明中强制引用 canonical 文档路径。
- 明确旧文档“可参考，但不能覆盖当前治理文档和源码”。

**收益**
- 防止团队成员引用过时碎片文档导致实现偏移。
- 降低评审歧义与返工成本。

---

### 3.2 P0：Token 治理攻坚

**建议**
- 颜色、间距、字体、边框、阴影全面 token 化。
- 禁止新增硬编码视觉值（含颜色、间距、字号等）。
- 统一字体语义层级：
  - 标题：`Cinzel`
  - 正文：`Barlow`
  - 数字：`JetBrains Mono`
- 将当前 **13 级编号间距体系** 映射为可复用样式策略：
  - `1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32`
  - 另含 `sm/md/lg/xl` 语义别名与 `compact-*` 紧凑变量

**收益**
- 页面视觉一致，避免“局部看起来像不同产品”。
- 大幅降低后续迭代中的样式漂移风险。

---

### 3.3 P1：组件治理

**建议**
- 基于 `ARTDECO_COMPONENTS_CATALOG` 做组件治理盘点。
- 为组件或页面块增加治理标签：
  - Token 合规
  - A 股涨跌语义合规（红涨绿跌）
  - 桌面端断点适配状态
  - 可访问性状态
  - 页面引用状态
- 明确三层边界：
  - `src/components/artdeco/**`：reusable assets
  - `views/artdeco-pages/components/`：page-level shared fragments
  - `views/artdeco-pages/*-tabs/`：domain tab blocks
- Domain 组件或页面块禁止绕过 token 与共享样式体系写散装视觉样式。

**收益**
- 降低重复组件和职责混乱。
- 提升组件复用率与长期可维护性。

---

### 3.4 P1：架构约束落地

**建议**
- 按 `ArtDeco_System_Architecture_Summary` 做一次结构审计：
  - 模板化工作台：检查 `pageConfig + slots` 壳层是否统一
  - 直接 Tab 容器：检查 tab rail 与 content shell 是否清晰
  - 功能树驱动总控容器：检查 orchestration 是否只留在顶层
- 明确目录边界（以下为**当前代码实态**，非仅目标架构）：
  - `views/artdeco-pages/`：页面容器与工作台入口
  - `views/artdeco-pages/components/`：页面系统共享片段
  - `views/artdeco-pages/*-tabs/`：域内工作台块
  - `src/components/artdeco/`：沉淀可复用资产（base/business/charts/core/advanced/specialized/trading）
- 对 `pageConfig.ts` 的要求改为：
  - 页面元信息与壳层编排可配置化
  - 不再假设它是所有 tabs 的唯一事实源
  - 域内 tab 逻辑以对应 domain block 为准
  - 页面内仍禁止散落 endpoint 字面量
- 若后续发生目录迁移/重命名，需在同一变更内同步更新：
  - `ARTDECO_MASTER_INDEX`
  - `ArtDeco_System_Architecture_Summary`
  - 本文档对应章节

**收益**
- 形成稳定边界，降低跨层耦合。
- 后续页面演进更可控。

---

### 3.5 P1：工程红线自动化

**建议**
- 将 `ARTDECO_COMPONENT_GUIDE` 的目录规则固化为 CI 检查项。
- 对以下问题建立自动化检查：
  - 页面块误入 reusable assets 目录
  - `*-tabs` 误被当成跨域复用组件
  - 新增样式继续扩散 `@import` 或硬编码视觉值
- 组件命名策略只保留为“建议约束”，不要机械推动全量改名；优先保证目录和职责边界正确。

**收益**
- 防止目录持续“技术债回流”。
- 保证多人协作下的结构稳定性。

---

### 3.6 P2：关键页面体验一致性强化

**建议**
- 重点页面（Trading / Market / Risk / Strategy）统一信息层级：
  1. 全局摘要
  2. 核心操作
  3. 细节数据
- 统一动效语气（hover、切换、状态反馈时长与曲线）。
- 表格和指标卡优先可读性，减少装饰干扰。
- 保留工作台气质，不回退成普通后台页。

**收益**
- 保留 ArtDeco 气质同时提升金融场景可用性。
- 减少页面间“手感不一致”。

---

## 4. 验收建议

建议将以下指标纳入优化验收清单：

1. Token 使用率 ≥ 95%
2. 新增硬编码视觉值 = 0
3. A 股红涨绿跌语义一致性 = 100%
4. 核心页面 reusable assets 复用率持续提升
5. Tab / 工作台切换交互反馈一致
6. 桌面端断点下的信息密度与可读性稳定
7. 关键页面焦点可见性、对比度满足团队标准

**统计口径说明（建议固化到执行脚本）**
- 统计范围：`web/frontend/src/**`（不含第三方依赖与构建产物）
- 统计对象：颜色、间距、字号、阴影、边框等视觉属性
- 统计方式：基于关键词与样式规则扫描（硬编码色值、像素值、直接字体名等）并输出差异报告

---

## 5. 建议执行分段

### 阶段 P0
- 规范入口统一
- Token 合规扫描
- Trading 先完成视觉语法统一

### 阶段 P1
- 组件治理台账
- 页面承载模式与目录边界修正
- 自动化检查补齐

### 阶段 P2
- 四大域一致性打磨
- 可访问性与性能微调
- 输出与 `ARTDECO_V3_COMPLETE_SUMMARY` 对齐的增量验收报告

---

## 6. 风险与控制

**主要风险**
- 在视觉优化过程中误触既有业务逻辑。
- 目录调整引发导入路径变更导致回归问题。
- 组件替换造成局部交互行为变化。

**控制措施**
- 先做“样式与结构分离”的小步提交。
- 每次仅处理一个 Domain，避免跨域并行改动。
- 对 Trading / Market 等核心页面建立最小回归清单。

**最小回归集合（建议）**
- Tab 切换与工作台区块切换可用
- 实时数据渲染与涨跌语义颜色正确
- 关键操作按钮（查询/刷新/下单入口）状态与反馈正常
- 关键表格（若页面存在）渲染、排序/筛选与高亮状态正常

---

## 7. 审核结论（建议）

建议立项为“ArtDeco 一致性治理优化”，而非“全面重设计”。
在不破坏既有 ArtDeco 资产前提下，优先推进 Token、页面承载边界与组件分层治理，能够以最稳定的方式持续提升一致性与可维护性。
