# ArtDeco Three-Layer Component Model

> **说明**
> 本文是在 [`ARTDECO_COMPONENT_LAYERING_DRAFT.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_LAYERING_DRAFT.md) 基础上的补充草案。
> 它不推翻现有 `Base / Domain` 规则，而是为当前已经出现的页面骨架类组件正式补上 `Core Skeleton` 层定义。

---

## 1. 为什么要从两层升级为三层

当前 `Base / Domain` 两层模型已经能覆盖很多组件，但它解释不了一类越来越重要的资产：

- 它们不是最小视觉积木
- 它们也不是业务域组件
- 它们承载的是页面级结构、状态壳层、统一交互骨架和脚手架能力

`ArtDecoPageTemplate` 就是最典型的例子。

如果继续强行把这类组件塞进 `Base`，会污染 Base；
如果直接把它们放进 `Domain`，又会掩盖它们的平台级复用价值。

因此，MyStocks 更合适的模型不是纯 `Base / Domain`，而是：

```text
Base
  -> Core Skeleton
    -> Domain
      -> Page / Feature
```

---

## 2. 三层定义

### Base

`Base` 是最小平台表达单元。

它负责：

- 最小视觉原语
- 最小交互原语
- 稳定 token 消费
- 通用 props / slots / 状态

典型例子：

- `ArtDecoButton`
- `ArtDecoCard`
- `ArtDecoInput`
- `ArtDecoBadge`
- `ArtDecoStatCard`

### Core Skeleton

`Core Skeleton` 是页面或模块级标准壳层。

它负责：

- 组织多个 Base / Core 组件
- 提供页面级结构骨架
- 提供统一的 loading / error / empty / trace / tabs 等状态容器
- 形成脚手架可复用模板
- 暴露稳定但非业务化的骨架契约

典型例子：

- `ArtDecoPageTemplate`
- 后续若存在稳定的 `Shell`、`SectionLayout`、`TabsLayout`、`PanelScaffold`，也应优先归入该层

### Domain

`Domain` 是业务语义组件层。

它负责：

- 组合 Base 与 Core Skeleton
- 表达业务域语义
- 对接业务模型、业务文案和业务交互
- 形成对业务页有意义的模块

典型例子：

- 风险告警面板
- 策略管理面板
- 系统健康摘要模块
- 交易控制面板

---

## 3. 三层最关键的差异

### Base 与 Core Skeleton 的差异

`Base` 的重点是“最小可复用能力”。

`Core Skeleton` 的重点是“结构化复用壳层”。

判断标准：

- 如果它主要解决一个按钮、卡片、输入框、徽标该怎么表达，它更接近 `Base`
- 如果它主要解决一个页面、一个区块、一个标准内容壳层该怎么组织，它更接近 `Core Skeleton`

### Core Skeleton 与 Domain 的差异

`Core Skeleton` 的重点是“标准骨架，不解释业务”。

`Domain` 的重点是“解释业务，服务业务”。

判断标准：

- 如果去掉业务语义后仍然成立，并且仍能作为多业务域的标准壳层复用，它更接近 `Core Skeleton`
- 如果去掉业务语义后就失去意义，它更接近 `Domain`

---

## 4. 每一层允许做什么

### Base 允许

- 使用 token
- 暴露通用 props
- 处理最小交互
- 提供通用 slot
- 提供纯通用样式状态

### Core Skeleton 允许

- 组合多个 Base 组件
- 统一页面级或模块级布局结构
- 承载 loading / error / empty / trace id / tabs 等标准壳层能力
- 提供稳定骨架 slots / emits / config
- 作为 CLI / 脚手架模板来源

### Domain 允许

- 组合 Base 与 Core Skeleton
- 理解业务状态和业务对象
- 对接具体业务域文案、数据结构和交互动作
- 承载具体业务工作流

---

## 5. 每一层禁止做什么

### Base 禁止

- 理解业务模型
- 承载页面级状态壳层
- 内置业务域文案
- 依赖页面级实现

### Core Skeleton 禁止

- 沉淀具体业务域判断逻辑
- 直接内置策略、交易、风控等专用对象语义
- 为单一页面定制一整套不可复用分支
- 退化成“半业务、半骨架”的灰色层

### Domain 禁止

- 伪装成平台通用组件出口
- 为了复用不断抽走业务语义
- 绕过 Base / Core Skeleton 重新造平行样式体系

---

## 6. 依赖方向

推荐依赖方向：

```text
Base
  -> 不依赖 Core Skeleton / Domain

Core Skeleton
  -> 可以依赖 Base
  -> 不依赖 Domain

Domain
  -> 可以依赖 Base
  -> 可以依赖 Core Skeleton

Page / Feature
  -> 可以依赖 Domain / Core Skeleton / Base
```

明确禁止：

- `Base -> Core Skeleton`
- `Base -> Domain`
- `Core Skeleton -> Domain`

原因：

- 一旦 `Core Skeleton` 反向依赖 `Domain`，骨架层就会被业务污染
- 一旦 `Base` 反向依赖上层，平台层就失去稳定性

---

## 7. 首批样板归类建议

### Base 样板

- `ArtDecoCard`
- `ArtDecoButton`

### Core Skeleton 样板

- `ArtDecoPageTemplate`

### Domain 样板

建议后续从高频业务面板中再选 1 个样板，但不应在当前批次仓促指定。

原因：

- 当前更紧迫的问题不是 Domain 不够多，而是 `Core Skeleton` 尚未被正式定义

---

## 8. 对 ArtDeco CLI 的意义

三层模型会直接影响未来 CLI 的输出边界：

- `Base` 层适合输出基础组件模板
- `Core Skeleton` 层适合输出页面壳层模板
- `Domain` 层适合输出业务模块模板

如果没有 `Core Skeleton` 这层，CLI 会出现两个问题：

1. 只能生成零散基础组件，生成不了真正可运行的页面骨架
2. 容易把半通用、半业务的壳层错误固化到 Base 或 Domain

因此，三层模型不是抽象优化，而是 CLI 平台化的必要前提。

---

## 9. 与当前治理路线的关系

这份草案对当前路线的影响应当是：

1. 不推翻 `Base / Domain` 既有讨论
2. 先把 `Core Skeleton` 作为补充层引入
3. 用首批样板验证三层模型是否稳定
4. 验证通过后，再决定是否更新更上层的组件治理主文档

这符合 MyStocks 当前“门禁守住增量、分批迁移收敛存量”的路径，不需要一次性大改全部目录。

---

## 10. 退出标准

当以下条件成立时，可认为三层模型已经具备进入 P1 的基础：

- `ArtDecoPageTemplate` 已被明确视为 `Core Skeleton`
- `Base / Core Skeleton / Domain` 的依赖方向已形成统一口径
- 首批样板组件已有明确归类
- 测试矩阵已能映射到不同层级的门禁重点
- CLI 规划已开始按三层模型理解输出边界

---

## 11. 一句话总结

对 MyStocks 而言，`Base / Domain` 仍然成立，但已经不够；真正适合当前阶段的平台模型，是在两者之间补上 `Core Skeleton`，让页面骨架第一次拥有合法、稳定、可治理的层级位置。
