# ArtDeco Base Component Test Matrix

> **说明**
> 本文用于把当前 `Base` 样板组件的测试要求收敛成统一入口。
> 它主要承接以下治理记录：
>
> - [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_CARD.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_CARD.md)
> - [`ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_BUTTON.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_BUTTON.md)

---

## 1. 目标

这份矩阵聚焦三件事：

1. 冻结 `Base` 样板的最小输入输出契约
2. 防止 `Card` 与 `Button` 的高频回归扩散到 `Core Skeleton` 与 `Domain`
3. 为未来 ArtDeco CLI 的基础组件模板提供测试样板

---

## 2. 为什么 Base 层也必须先补测试

当前 P1 的测试批次已经先把 `Core Skeleton -> Domain` 顺序明确下来，但这不意味着 `Base` 可以长期缺席。

原因很直接：

- `Core Skeleton` 会大量消费 `Button` / `Card`
- `Domain` 组件也直接建立在这些基础组件上
- 如果 `Base` 契约漂移，后两层会同步被污染

因此，`Base` 测试的作用不是和 Skeleton / Domain 抢优先级，而是补齐平台底座。

---

## 3. 测试分层建议

建议采用三层保护：

- **单元测试**: 验证 props、slots、class 映射、事件触发
- **组件集成测试**: 验证高频组合行为与兼容别名
- **最小视觉回归**: 验证高频基础外观没有结构性破坏

当前优先顺序：

1. 单元测试
2. 组件集成测试
3. 最小视觉回归

---

## 4. ArtDecoCard 最小必测用例

### A. 基础渲染契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| C-A1 | 传入 `title` 时渲染 header | 冻结基础标题契约 | P0 |
| C-A2 | 传入 `subtitle` 时渲染副标题 | 冻结副标题契约 | P0 |
| C-A3 | 未传 `title` 且无 `header` slot 时不渲染 header 容器 | 防止空 header 壳层 | P0 |
| C-A4 | 传入默认 slot 时渲染 body 内容 | 冻结主体内容插槽 | P0 |
| C-A5 | 传入 `footer` slot 时渲染 footer 容器 | 冻结 footer 扩展位 | P1 |

### B. 交互与 class 映射

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| C-B1 | `clickable=true` 时挂载 `artdeco-card--clickable` | 冻结点击态样式挂载点 | P0 |
| C-B2 | `hoverable=true` 时挂载 `artdeco-card--hoverable` | 冻结悬停态样式挂载点 | P0 |
| C-B3 | 传入 `variant=\"stat\"` 时挂载对应 class | 冻结 variant 映射 | P0 |
| C-B4 | 传入 `aspectRatio=\"16/9\"` 时挂载 `artdeco-card--aspect-16-9` | 冻结宽高比 class 映射 | P0 |
| C-B5 | `clickable=false` 时点击不触发 `click` emit | 冻结点击门禁 | P0 |
| C-B6 | `clickable=true` 时点击触发 `click` emit | 冻结点击出口 | P0 |

### C. 兼容与风险治理

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| C-C1 | 历史非法 props 不应影响基础渲染 | 防止未知属性污染基础行为 | P1 |
| C-C2 | `variant` 在常用分支下都能正确挂载 class | 冻结高频变体契约 | P1 |

---

## 5. ArtDecoButton 最小必测用例

### A. 基础渲染契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| B-A1 | 默认 slot 正常渲染按钮文本 | 冻结基础文本契约 | P0 |
| B-A2 | 传入 `icon` slot 时渲染图标容器 | 冻结 icon 扩展位 | P0 |
| B-A3 | `loading=true` 时显示 spinner | 冻结加载态基础结构 | P0 |
| B-A4 | `loading=true` 时按钮具有 `aria-busy=\"true\"` | 冻结无障碍语义 | P0 |

### B. 变体与尺寸契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| B-B1 | 默认 `variant` 映射为 `artdeco-button--default` | 冻结默认变体 | P0 |
| B-B2 | `variant=\"solid\"` 时挂载对应 class | 冻结核心主按钮变体 | P0 |
| B-B3 | `variant=\"outline\"` 时挂载对应 class | 冻结次按钮变体 | P0 |
| B-B4 | `variant=\"primary\"` 归一为 `solid` | 冻结兼容别名策略 | P0 |
| B-B5 | `variant=\"gold\"` 归一为 `solid` | 冻结兼容别名策略 | P0 |
| B-B6 | `size=\"sm\"` / `md` / `lg` 时挂载对应 class | 冻结尺寸契约 | P0 |

### C. 状态与事件契约

| 编号 | 用例 | 目标 | 优先级 |
|------|------|------|--------|
| B-C1 | `disabled=true` 时按钮被禁用 | 冻结禁用态 | P0 |
| B-C2 | `loading=true` 时按钮被禁用 | 冻结加载态禁用逻辑 | P0 |
| B-C3 | 非禁用态点击触发 `click` emit | 冻结点击出口 | P0 |
| B-C4 | `disabled=true` 时点击不触发 `click` emit | 冻结禁用门禁 | P0 |
| B-C5 | `loading=true` 时点击不触发 `click` emit | 冻结加载门禁 | P0 |
| B-C6 | `block=true` 时挂载 `artdeco-button--block` | 冻结整行按钮模式 | P1 |
| B-C7 | `priority` 非 `auto` 时挂载优先级 class | 冻结优先级挂载点 | P1 |
| B-C8 | `motion` 非 `auto` 时挂载动效 class | 冻结 motion 挂载点 | P1 |

---

## 6. 最小视觉回归清单

当前不追求完整视觉黄金图库，只建议保留最小样板：

### ArtDecoCard

建议场景：

1. 默认卡片
2. `stat` 变体
3. 带 header + footer 的卡片

### ArtDecoButton

建议场景：

1. 默认按钮
2. `solid` / `outline` 主次动作按钮
3. `loading` 按钮

若资源有限，可先各保留 1 条高频样板。

---

## 7. 建议的首批实现范围

如果只做第一批最小保护，建议先实现以下用例：

### Card 首批

- `C-A1`
- `C-A2`
- `C-A4`
- `C-B1`
- `C-B3`
- `C-B4`
- `C-B6`

### Button 首批

- `B-A1`
- `B-A3`
- `B-A4`
- `B-B1`
- `B-B4`
- `B-B5`
- `B-C1`
- `B-C2`
- `B-C3`
- `B-C4`

这些用例已经能覆盖：

- `Card` 的结构与 click 契约
- `Button` 的变体归一与禁用逻辑
- Skeleton / Domain 对 Base 的高频依赖点

---

## 8. 不建议当前就扩展的测试

当前阶段不建议优先投入：

- 对每个 SCSS 细节逐项断言
- 对所有 `variant` 做全量像素快照
- 对所有过渡动画做时序测试
- 为未知历史非法 props 建立大量兼容测试

原因：

- 当前目标是冻结 Base 契约，不是把样式实现细节全部锁死
- 过早扩张会拖慢三层样板的整体推进节奏

---

## 9. 与 P1 批次计划的关系

这份矩阵不替代 [`ARTDECO_P1_TEST_IMPLEMENTATION_BATCH_PLAN.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_P1_TEST_IMPLEMENTATION_BATCH_PLAN.md)，而是补上其中尚未展开的 `Base` 测试入口。

合理顺序仍然是：

1. 先做 `Core Skeleton`
2. 再做 `Domain`
3. 并行或随后补 `Base` 底座

但一旦进入 Base 批次，这份矩阵可以直接作为实施入口。

---

## 10. 退出标准

当以下条件同时成立时，可判定 `Base` 样板组件具备进入 P1 的最小测试基础：

- `ArtDecoCard` 的结构与 click 契约已有自动化保护
- `ArtDecoButton` 的变体归一与禁用逻辑已有自动化保护
- 至少各有 1 条最小视觉回归样板
- `Core Skeleton` 与 `Domain` 的高频依赖点不再完全裸奔

---

## 11. 一句话总结

`Base` 测试的价值不在于“最先写”，而在于给整个 ArtDeco 平台补底座；`Card` 和 `Button` 一旦稳定，后面的 Skeleton 与 Domain 才不会持续被基础契约漂移反复牵连。
