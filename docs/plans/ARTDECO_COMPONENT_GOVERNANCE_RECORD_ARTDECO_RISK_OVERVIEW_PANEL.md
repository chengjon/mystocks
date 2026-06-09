# ArtDeco Component Governance Record: ArtDecoRiskOverviewPanel

> **说明**
> 本文基于 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md`](ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md) 产出，是首批样板组件的第四份实战治理记录草案。
> 它同时也是三层模型中的第一份 `Domain` 样板记录。

---

## 1. 组件基本信息

- **组件名称**: `ArtDecoRiskOverviewPanel`
- **组件路径**: [`web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue`](../../web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue)
- **所属层级**: `Domain`
- **所属业务域**: `风险控制`
- **当前状态**: `候选`

---

## 2. 选择该组件的原因

- **高频程度**: `中`
- **选择原因**:
  - 适合作为 Domain 层样板
  - 与 `Core Skeleton` 协作关系清晰
  - 业务语义明确
  - 适合作为业务模块模板来源

### 补充说明

`ArtDecoRiskOverviewPanel` 当前直接挂接在：

- [`web/frontend/src/views/risk/Center.vue`](../../web/frontend/src/views/risk/Center.vue)
- [`web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue`](../../web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue)

它的价值不在“通用程度”，而在于它非常适合回答一个关键问题：

在 `Base` 和 `Core Skeleton` 已经逐步稳定后，真正的业务面板应长什么样。

它已经同时具备以下 Domain 特征：

1. 理解风险预警对象与风险等级
2. 使用风险域文案与风险域动作建议
3. 组合多个 Base 组件形成业务面板
4. 通过 `action` 事件向上回传业务对象

---

## 3. 当前主要问题

勾选项：

- Domain 契约尚未冻结
- token 使用需要持续收敛
- 测试保护不足
- 与 Core Skeleton 的边界需要明确

### 问题摘要

- 该组件显然不属于 Base，因为它直接解释 `riskAlerts`、`riskLevel`、`stopStatus`、`action` 等业务语义。
- 它也不应被提升为 `Core Skeleton`，因为它不是标准壳层，而是一个明确服务于风险域的业务面板。
- 当前组件把领域文案、状态标签、操作建议和结构组织集中在一起，这本身是合理的 Domain 表达，但需要进一步冻结输入输出边界，避免后续继续膨胀成“半页面实现”。
- 它当前依赖 `riskManagementHelpers` 提供领域枚举映射、颜色和集中度数据，说明它已经进入“业务语义组合层”，后续应重点关注契约稳定，而不是盲目追求抽象复用。

---

## 4. token 影响记录

- **涉及的视觉类别**:
  - 风险等级状态色
  - 表格容器视觉
  - 卡片头部结构
  - 进度条与分布条表达

- **现有 token 可复用项**:
  - `ArtDecoCard` / `ArtDecoButton` / `ArtDecoBadge` 已承接部分基础视觉
  - `artdeco-tokens.scss` 中的间距、字体、基础颜色变量已被使用

- **需要新增 token 项**:
  - 当前阶段不建议先为该 Domain 组件新增专属 token
  - 应优先确认风险等级色、止损状态色是否能够映射到更稳定的语义 token 家族

- **需要合并 / 淘汰 token 项**:
  - 后续需核查风险态颜色是否散落在局部样式和 helper 数据中，避免“业务色语义”和“基础视觉色语义”分裂

- **暂不处理项**:
  - 领域图表细节和装饰性动效不作为第一批治理重点

---

## 5. 结构治理记录

- **当前判定**: `维持 Domain`

- **结构治理动作**:
  - 冻结业务输入输出契约
  - 明确与 Core Skeleton 的协作边界
  - 限制领域面板继续吸收页面壳职责
  - 形成业务模块模板样板

### 治理理由

- `ArtDecoRiskOverviewPanel` 去掉风险语义后就不再成立，因此它不应继续被讨论为 Base。
- 它也不是页面壳层，因为它不负责统一 loading / error / empty / trace / tabs。
- 它最适合被固定为 `Domain` 样板：在上层接入 `ArtDecoPageTemplate`，在底层消费 `ArtDecoCard`、`ArtDecoButton`、`ArtDecoBadge` 等 Base 能力。
- 这类组件如果治理得当，可以成为未来业务模块模板的标准样板；如果治理失控，则很容易向“页面实现 + 业务逻辑 + 样式特例”膨胀。

---

## 6. 测试与门禁要求

- **是否需要最小单测**: `是`
- **是否需要视觉回归保护**: `是`
- **是否需要交互测试**: `是`
- **是否需要样式门禁关注**: `是`

### 建议测试项

- 传入 `riskAlerts` 后渲染预警列表
- 风险等级文案映射
- 止损状态文案映射
- 点击操作按钮时触发 `action`
- 预警数量徽标显示逻辑
- 空列表下表格区表现
- 集中度分析区和行业分布区基础渲染

---

## 7. 对 CLI 模板的价值

- **是否适合作为 CLI 模板来源**: `是`

- **适用模板类型**:
  - Domain 业务面板模板
  - 风险类业务模块模板
  - Base + Skeleton 组合样板

### 原因

- `ArtDecoRiskOverviewPanel` 代表的不是一个通用控件，而是一种典型业务面板结构。
- 它很适合被用作未来 CLI 的 Domain 模板样板，向团队说明“业务面板应如何依赖 Base 与 Skeleton，而不是直接从页面复制一坨实现”。
- 这能帮助 ArtDeco CLI 从“组件脚手架”进一步走向“业务模块脚手架”。

---

## 8. 最终结论

本组件建议作为第 1 批 Domain 治理样板。

原因：

- 业务语义足够明确
- 与 `ArtDecoPageTemplate` 的上下层关系清晰
- 与 `ArtDecoCard` / `ArtDecoButton` 的下层关系清晰
- 适合成为三层模型中的 Domain 落地样板

治理重点：

- 冻结 `riskAlerts` 输入与 `action` 输出契约
- 防止领域面板继续吸收页面壳职责
- 确认风险态视觉表达是否应进一步语义化

测试重点：

- 风险列表渲染
- 状态映射
- 动作事件
- 最小视觉回归保护

CLI 价值：

- 可作为 Domain 业务面板模板的第一批样板
- 可帮助未来 CLI 输出“业务模块”，而不只是“基础组件”

---

## 9. 一句话总结

`ArtDecoRiskOverviewPanel` 适合作为第一份 Domain 样板，因为它清楚地展示了业务组件该如何站在 `Base` 与 `Core Skeleton` 之上表达领域语义，而不是回头污染平台层。
