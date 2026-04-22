# ArtDeco Component Governance Record: ArtDecoCard

> **说明**
> 本文基于 [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_TEMPLATE.md) 产出，是首批样板组件的第一份实战治理记录草案。

---

## 1. 组件基本信息

- **组件名称**: `ArtDecoCard`
- **组件路径**: [`web/frontend/src/components/artdeco/base/ArtDecoCard.vue`](/opt/claude/mystocks_spec/web/frontend/src/components/artdeco/base/ArtDecoCard.vue)
- **所属层级**: `Base`
- **所属业务域**: `通用`
- **当前状态**: `候选`

---

## 2. 选择该组件的原因

- **高频程度**: `高`
- **选择原因**:
  - 高频复用
  - 页面骨架影响大
  - 适合作为 CLI 模板来源
  - token 收敛价值高

### 补充说明

抽样统计中，`ArtDecoCard` 的引用文件数约为 `103`，是当前 ArtDeco 基础组件中最明显的高频容器之一。

它同时具备三种平台价值：

1. 是 Base 层的典型容器组件
2. 大量页面与业务组件都依赖它表达结构和层次
3. 它的 token、变体和 props 设计会直接影响后续组件模板与页面骨架模板

---

## 3. 当前主要问题

勾选项：

- token 使用不统一
- Base / Domain 边界需要确认
- 测试保护不足
- 页面依赖方式不稳定

### 问题摘要

- 组件本身应属于 Base，但它承载了较多风格表达，适合作为 Base 层规则样板来冻结，而不是继续自由演化。
- 组件当前定义的 props 包括 `title`、`subtitle`、`hoverable`、`clickable`、`variant`、`aspectRatio`，结构较清晰，但周边调用存在历史接口漂移。
- 已发现部分页面仍传入 `:decorated="true"` 之类当前组件未声明的属性，说明调用侧与组件真实接口之间存在历史残留或兼容漂移。
- 组件高度依赖 token、mixin 和样式系统，是 token 治理最适合的第一批承载点。

---

## 4. token 影响记录

- **涉及的视觉类别**:
  - 颜色
  - 边框
  - 阴影
  - 间距
  - 状态语义

- **现有 token 可复用项**:
  - `--artdeco-radius-none`
  - `--artdeco-spacing-*`
  - `--artdeco-gold-*`
  - `--ad-card-border-*`
  - `--ad-card-bg-*`
  - `--ad-card-shadow-*`

- **需要新增 token 项**:
  - 当前记录中未发现必须立刻新增的新 token，但需要确认 `ad-card-*` 家族是否已经覆盖所有高频卡片语义

- **需要合并 / 淘汰 token 项**:
  - 需后续核查 `card` 相关 token 是否存在近义重复或命名漂移

- **暂不处理项**:
  - 装饰性 hover 微调不作为第一批 token 治理重点

---

## 5. 结构治理记录

- **当前判定**: `维持 Base`

- **结构治理动作**:
  - 调整 props 设计
  - 调整依赖方式
  - 明确组件契约边界

### 治理理由

- `ArtDecoCard` 去掉业务语义后仍然成立，明显属于 Base 层。
- 当前重点不是把它迁到 Domain，而是把它的通用容器职责进一步冻结。
- 需要优先处理调用侧对旧属性的依赖问题，例如 `decorated` 这类与当前组件声明不一致的历史调用。
- 若 Base 容器组件的 props 契约不稳定，后续 CLI 和样板组件都会传播不稳定接口。

---

## 6. 测试与门禁要求

- **是否需要最小单测**: `是`
- **是否需要视觉回归保护**: `是`
- **是否需要交互测试**: `是`
- **是否需要样式门禁关注**: `是`

### 建议测试项

- 基础渲染
- `title` / `subtitle` 显示
- `hoverable` / `clickable` 状态
- `variant` 切换
- `aspectRatio` 类名映射
- 历史调用兼容性或非法 props 清理策略

---

## 7. 对 CLI 模板的价值

- **是否适合作为 CLI 模板来源**: `是`

- **适用模板类型**:
  - Base 组件模板
  - 页面骨架模板

### 原因

- `ArtDecoCard` 是高频基础容器，极适合成为 Base 组件模板的代表样板。
- 多数页面骨架都需要卡片容器，因此它也会影响页面模板的默认结构。
- 它的 props 设计、样式组织方式和 token 用法都应在进入 CLI 前被稳定下来。

---

## 8. 最终结论

本组件建议作为第 1 批治理对象。

原因：

- 高频复用
- Base 层代表性强
- 对 token 收敛、页面骨架和 CLI 模板都有直接影响

治理重点：

- 冻结 `ArtDecoCard` 的 Base 组件契约
- 清理调用侧与真实 props 的漂移
- 确认 `card` 相关 token 的稳定性与命名一致性

测试重点：

- 基础渲染与变体行为
- hover / clickable 交互表现
- 视觉快照或最小视觉回归保护

CLI 价值：

- 可作为 Base 组件模板的第一批核心样板
- 可影响页面骨架模板中的容器默认实现

---

## 9. 一句话总结

`ArtDecoCard` 不是因为“简单”才适合先治理，而是因为它是当前 ArtDeco 平台里最典型、最高频、最值得先冻结契约的 Base 容器组件。
