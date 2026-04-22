# ArtDeco Component Layering Draft

> **说明**
> 本文是 ArtDeco 组件 `Base / Domain` 分层规则草案，用于支撑 [`ARTDECO_STANDARDIZATION_P0_TASKS.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_STANDARDIZATION_P0_TASKS.md) 中的组件边界冻结工作。
> 它的作用不是立刻迁移全部组件，而是先建立统一判断标准。

---

## 1. 目标

这份草案要解决三个问题：

1. 什么组件应归入 `Base`
2. 什么组件应归入 `Domain`
3. 出现边界模糊时如何判断

如果这三点不先讲清楚，后续任何组件治理都会反复返工。

---

## 2. 分层定义

### Base 组件

`Base` 组件是平台层的基础表达单元。

它应当：

- 承载通用表现能力
- 承载最小交互能力
- 使用稳定 token
- 不绑定具体业务语义
- 不依赖具体业务域数据模型

典型例子：

- Button
- Input
- Card
- Badge
- Loading Overlay

### Domain 组件

`Domain` 组件是业务语义与组合规则的承载层。

它应当：

- 组合一个或多个 Base 组件
- 暴露业务域清晰的输入输出
- 表达明确的业务语义
- 允许依赖当前业务域的状态、文案和结构约定

典型例子：

- 策略管理卡片
- 交易控制面板
- 系统状态摘要模块
- 风险告警面板

---

## 3. 判定规则

### 判定问题 1：如果去掉业务名词，它还成立吗

如果一个组件去掉业务语义后仍然成立，它更可能属于 `Base`。

如果去掉业务语义后就失去意义，它更可能属于 `Domain`。

例子：

- `ArtDecoButton` 去掉业务名词仍然成立，属于 `Base`
- `ArtDecoStrategyManagementPanel` 去掉业务名词后失去意义，属于 `Domain`

### 判定问题 2：它是否需要理解业务状态

如果组件需要理解：

- 策略状态
- 交易语义
- 风险等级
- 系统健康结果

这类领域语义，它更应归入 `Domain`。

如果组件只需要：

- `variant`
- `size`
- `disabled`
- `loading`

这类通用输入，它更应归入 `Base`。

### 判定问题 3：它是否会被多个业务域复用

如果一个组件能稳定服务多个业务域，且不需要解释业务语义，它更适合 `Base`。

如果组件高度依赖某个业务域的结构和状态，它更适合 `Domain`。

---

## 4. Base 层允许做什么

Base 组件允许：

- 处理通用交互
- 提供统一视觉表现
- 提供可复用的状态外观
- 暴露清晰的通用 props
- 集成稳定 token

Base 组件可以有行为，但这个行为必须是“通用行为”，而不是“业务行为”。

例如：

- hover / focus / active
- loading 展示
- disabled 控制
- 通用 slot 布局

---

## 5. Base 层禁止做什么

Base 组件禁止：

- 沉淀业务域判断逻辑
- 依赖业务接口返回结构
- 内置策略、交易、风控等领域文案
- 通过 props 注入一整套业务对象然后自行解释
- 为了复用而不断吸收业务特殊分支

一旦 Base 组件开始出现大量业务分支，它就已经不再是 Base。

---

## 6. Domain 层允许做什么

Domain 组件允许：

- 组合多个 Base 组件
- 表达业务语义
- 使用业务域命名
- 依赖当前业务域的数据结构
- 封装业务交互组合关系

Domain 组件的价值不在“通用”，而在“明确”。

---

## 7. Domain 层禁止做什么

Domain 组件禁止：

- 反向充当 Base 组件出口
- 为了所谓复用不断抽象到失去语义
- 把样式系统复制成另一套平行体系
- 绕开 token 直接沉淀大量字面量视觉值

---

## 8. 依赖方向

推荐依赖方向：

```text
Base
  -> 不依赖 Domain

Domain
  -> 可以依赖 Base

Page / Feature
  -> 可以依赖 Domain 和 Base
```

明确禁止：

- `Base -> Domain`
- `Base -> 业务接口模型`
- `Base -> 页面级实现`

---

## 9. 命名建议

Base 组件命名建议：

- 使用通用能力命名
- 不携带业务域名词

例如：

- `ArtDecoButton`
- `ArtDecoCard`
- `ArtDecoInput`
- `ArtDecoBadge`

Domain 组件命名建议：

- 使用业务语义命名
- 允许带业务域前缀或上下文词

例如：

- `ArtDecoStrategyManagementPanel`
- `ArtDecoTradingSignalsControls`
- `ArtDecoSystemHealthSummary`

---

## 10. 边界模糊时的处理方式

如果一个组件难以判断，建议按以下顺序处理：

1. 先判断它是否解释业务语义
2. 再判断它是否依赖业务结构
3. 若仍不清楚，优先放入 `Domain`

原因：

- 误把 Domain 放进 Base，污染更严重
- 误把 Base 暂时放进 Domain，后续更容易再抽出来

默认策略：

`宁可保守地留在 Domain，也不要过早提升到 Base`

---

## 11. 首批治理时的使用方式

这份草案在 P0 / P1 阶段的用途应是：

- 盘点现有组件归属
- 标记边界冲突组件
- 选出首批样板组件
- 为后续 CLI 模板固化提供判断口径

它不要求一次性重排全部目录。

---

## 12. 一句话总结

Base 层追求的是“稳定的通用能力”，Domain 层追求的是“清晰的业务表达”。

一旦组件开始解释业务，它就不该继续留在 Base。
