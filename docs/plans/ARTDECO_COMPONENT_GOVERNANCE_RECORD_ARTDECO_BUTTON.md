# ArtDeco Component Governance Record: ArtDecoButton

> **说明**
> 本文基于 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md) 产出，是首批样板组件的第二份实战治理记录草案。

---

## 1. 组件基本信息

- **组件名称**: `ArtDecoButton`
- **组件路径**: [`web/frontend/src/components/artdeco/base/ArtDecoButton.vue`](/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/base/ArtDecoButton.vue)
- **所属层级**: `Base`
- **所属业务域**: `通用`
- **当前状态**: `候选`

---

## 2. 选择该组件的原因

- **高频程度**: `高`
- **选择原因**:
  - 高频复用
  - 适合作为 CLI 模板来源
  - token 收敛价值高
  - Base 契约代表性强

### 补充说明

抽样统计中，`ArtDecoButton` 的引用文件数约为 `71`，属于当前 ArtDeco 基础组件中的核心交互入口之一。

它的治理价值主要体现在：

1. 它是 Base 层最典型的动作触发组件
2. 它的 `variant / size / loading / disabled` 契约会影响大量页面和业务组件
3. 它非常适合作为未来 CLI 中 `Base 组件模板` 和 `页面动作区模板` 的来源

---

## 3. 当前主要问题

勾选项：

- token 使用需要确认
- Base / Domain 边界需要确认
- 测试保护不足
- 变体语义需要收敛

### 问题摘要

- `ArtDecoButton` 明确属于 Base 层，但当前 `variant` 语义带有一定历史别名包袱，例如 `primary` / `gold` 会被归一到 `solid`。
- 这种做法短期有兼容价值，但长期如果不冻结，会让按钮语义继续漂移。
- 当前组件已承载较多状态与表现组合，包括 `variant`、`size`、`priority`、`motion`、`block`、`loading`、`disabled`，说明它已经接近平台级基础契约，需要尽早稳定。
- 相比 `ArtDecoCard`，按钮的主要风险不在旧属性残留，而在“变体不断扩张、语义边界变模糊”。

---

## 4. token 影响记录

- **涉及的视觉类别**:
  - 颜色
  - 边框
  - 阴影
  - 间距
  - 状态语义

- **现有 token 可复用项**:
  - `--artdeco-gold-*`
  - `--artdeco-rise`
  - `--artdeco-down`
  - `--artdeco-radius-none`
  - `--artdeco-transition-*`
  - `--ad-btn-*`

- **需要新增 token 项**:
  - 当前记录中未发现必须立刻新增的 token，但需核查 `ad-btn-*` 是否已经完整覆盖按钮状态语义

- **需要合并 / 淘汰 token 项**:
  - 需后续核查按钮状态色与金融语义色是否存在命名重叠或近义别名

- **暂不处理项**:
  - 动效微调不应成为首批 token 治理重点

---

## 5. 结构治理记录

- **当前判定**: `维持 Base`

- **结构治理动作**:
  - 调整 props 设计
  - 冻结变体语义
  - 调整依赖方式

### 治理理由

- `ArtDecoButton` 去掉业务语义后仍然完全成立，明确属于 Base。
- 当前治理重点不是迁层，而是冻结其“平台动作组件”契约。
- `variant` 别名兼容 (`primary` / `gold` -> `solid`) 表明它已经承受了历史接口兼容压力，需要明确未来是否继续保留这些别名。
- 若按钮语义不稳定，后续 Domain 组件和 CLI 生成模板都会继承这种不稳定性。

---

## 6. 测试与门禁要求

- **是否需要最小单测**: `是`
- **是否需要视觉回归保护**: `是`
- **是否需要交互测试**: `是`
- **是否需要样式门禁关注**: `是`

### 建议测试项

- 基础渲染
- `variant` 切换
- `size` 切换
- `disabled` / `loading` 状态
- `click` 事件在禁用和加载状态下的行为
- `block` 模式
- 兼容别名 `primary` / `gold` 的处理策略

---

## 7. 对 CLI 模板的价值

- **是否适合作为 CLI 模板来源**: `是`

- **适用模板类型**:
  - Base 组件模板
  - 页面动作区模板
  - 测试模板

### 原因

- `ArtDecoButton` 是高频基础交互组件，非常适合作为 Base 组件模板样板。
- 几乎所有页面骨架和业务域操作区都需要按钮，因此它也会影响 CLI 对动作区的默认输出。
- 它的最小测试骨架也适合成为未来模板的一部分。

---

## 8. 最终结论

本组件建议作为第 1 批治理对象。

原因：

- 高频复用
- Base 层代表性强
- 直接影响动作语义、交互状态和 CLI 模板输出

治理重点：

- 冻结 `variant` 语义与兼容别名策略
- 确认按钮状态 token 的表达稳定性
- 形成稳定的 Base 按钮测试样板

测试重点：

- 变体与尺寸组合
- 加载与禁用状态
- 事件触发约束
- 视觉快照或最小视觉回归保护

CLI 价值：

- 可作为 Base 按钮模板的核心样板
- 可作为页面动作区默认生成模板的重要来源

---

## 9. 一句话总结

`ArtDecoButton` 适合成为第二个 Base 样板，因为它代表的是 ArtDeco 平台里的“动作契约”；如果按钮变体和状态语义不稳定，整个组件平台的交互语言就不会稳定。
