# ArtDeco High-Frequency Candidate List

> **说明**
> 本文用于承接 [`ARTDECO_STANDARDIZATION_P0_TASKS.md`](ARTDECO_STANDARDIZATION_P0_TASKS.md) 中“选定首批高频组件样板”的工作。
> 它不是全量组件 inventory，而是首批 P1 样板治理候选清单。

---

## 1. 选择方法

本轮候选选择基于以下标准：

- 在当前仓库中出现频次较高
- 位于 Base / Core / 高频业务组合层
- 对页面骨架或跨页面视觉一致性影响大
- 适合作为后续 CLI 模板固化基础

这份清单优先追求“样板代表性”，不是“覆盖所有组件”。

---

## 2. 当前高频信号

本轮抽样统计到的组件引用频次如下：

| 组件 | 粗略引用文件数 | 备注 |
|------|----------------|------|
| `ArtDecoCard` | 103 | 高复用基础容器 |
| `ArtDecoButton` | 71 | 高复用基础交互 |
| `ArtDecoStatCard` | 66 | 高复用状态展示 |
| `ArtDecoBadge` | 42 | 高频状态标签 |
| `ArtDecoTable` | 23 | 高频数据展示骨架 |
| `ArtDecoInput` | 18 | 基础输入能力 |
| `ArtDecoBreadcrumb` | 8 | 页面骨架导航 |
| `ArtDecoStatus` | 8 | 业务状态表达 |
| `ArtDecoSkeleton` | 6 | 加载占位骨架 |
| `ArtDecoLoadingOverlay` | 3 | 加载遮罩骨架 |

补充观察：

- 页面骨架模板 `ArtDecoPageTemplate` 已存在，但引用还不高，更适合作为骨架标准化样板，而不是高频基础组件样板。
- 业务域组合组件中，`strategy`、`system`、`risk`、`trading` 几个域已经具备较好的样板潜力。

---

## 3. 首批样板候选

### 批次 A：Base 层核心样板

建议优先：

1. `ArtDecoCard`
2. `ArtDecoButton`
3. `ArtDecoStatCard`
4. `ArtDecoBadge`
5. `ArtDecoInput`

理由：

- 这些组件处在高频复用区
- 它们直接决定 ArtDeco 基础视觉语言是否一致
- 它们适合作为 token 收敛的第一批承载对象
- 后续 CLI 几乎一定需要依赖这些基础组件模板

### 批次 B：Core / 骨架层样板

建议优先：

1. `ArtDecoBreadcrumb`
2. `ArtDecoLoadingOverlay`
3. `ArtDecoSkeleton`
4. `ArtDecoPageTemplate`

理由：

- 这批组件影响页面骨架一致性
- 它们决定页面级生成模板是否稳定
- 对后续“页面骨架 CLI”影响很大

### 批次 C：Domain 层样板

建议优先：

1. `ArtDecoStatus`
2. `ArtDecoTradingSignalsControls`
3. `ArtDecoRiskOverviewPanel`
4. `ArtDecoSystemSettings`
5. `ArtDecoStrategyManagement`

理由：

- 这批组件适合验证 Domain 层的边界规则
- 覆盖了 `trading`、`risk`、`system`、`strategy` 四类典型业务语义
- 能为后续 Domain 组件模板提供真实样板

---

## 4. 推荐首批治理顺序

建议顺序如下：

### 第 1 组：基础平台表达

- `ArtDecoCard`
- `ArtDecoButton`
- `ArtDecoStatCard`
- `ArtDecoBadge`

目标：

- 先稳住最常见的视觉和交互表达

### 第 2 组：页面骨架表达

- `ArtDecoBreadcrumb`
- `ArtDecoLoadingOverlay`
- `ArtDecoSkeleton`
- `ArtDecoPageTemplate`

目标：

- 先稳住页面级结构和骨架语言

### 第 3 组：业务域样板表达

- `ArtDecoStatus`
- `ArtDecoTradingSignalsControls`
- `ArtDecoRiskOverviewPanel`
- `ArtDecoSystemSettings`
- `ArtDecoStrategyManagement`

目标：

- 用真实业务组件验证 Base / Domain 分层规则

---

## 5. 当前建议暂缓的类型

以下组件不建议进入第一批治理：

- 高频度不足但复杂度很高的特殊图表组件
- 高度实验性的 advanced 分析组件
- 强绑定单个页面、缺乏复用价值的边缘组件
- 仍处于快速变化中的临时业务组件

原因：

- 第一批治理更需要稳定样板，不适合拿高度波动组件做平台模板

---

## 6. 建议输出到 P1 的内容

这份候选清单建议向 P1 输出两类信息：

### A. 样板组件治理名单

- Base 样板
- 骨架样板
- Domain 样板

### B. 每个样板组件的治理目标摘要

建议至少记录：

- 所属层级
- 主要问题类型
- 需要关注的 token 范围
- 是否需要视觉回归保护
- 是否适合作为 CLI 模板来源

---

## 7. 一句话总结

首批 ArtDeco 样板组件不应追求“覆盖最多功能”，而应优先覆盖“最能代表平台基础能力、页面骨架能力和 Domain 边界能力”的组件。
