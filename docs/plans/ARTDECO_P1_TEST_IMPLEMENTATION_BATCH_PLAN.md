# ArtDeco P1 Test Implementation Batch Plan

> **说明**
> 本文用于把现有测试矩阵收敛成 P1 可执行批次。
> 它服务于以下文档的落地：
>
> - [`ARTDECO_PAGE_TEMPLATE_TEST_MATRIX.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_PAGE_TEMPLATE_TEST_MATRIX.md)
> - [`ARTDECO_RISK_OVERVIEW_PANEL_TEST_MATRIX.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_RISK_OVERVIEW_PANEL_TEST_MATRIX.md)
> - [`ARTDECO_STANDARDIZATION_P1_TASKS.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_STANDARDIZATION_P1_TASKS.md)

---

## 1. 目标

P1 测试实施批次要解决的不是“把所有组件都测完”，而是先建立第一条真正可复制的测试推进路径。

这条路径应满足：

1. 先保护 `Core Skeleton`
2. 再保护 `Domain`
3. 最后补最小视觉回归
4. 全程不脱离三层模型的依赖方向

---

## 2. 为什么先测 Skeleton，再测 Domain

当前最合理的顺序不是随机挑组件写测试，而是按结构依赖推进：

```text
Base
  -> Core Skeleton
    -> Domain
```

对当前 P1 来说：

- `ArtDecoPageTemplate` 是 `Core Skeleton` 样板
- `ArtDecoRiskOverviewPanel` 是 `Domain` 样板

如果先写 Domain 测试，而 Skeleton 契约还没有稳定，后续一旦 Skeleton 变动，Domain 测试很容易反复重写。

所以测试顺序应是：

1. 先冻结页面骨架
2. 再冻结业务面板
3. 最后补视觉回归样板

---

## 3. P1 推荐实施批次

### 批次 1：Core Skeleton 最小单测

目标：

- 先给 `ArtDecoPageTemplate` 建立最小稳定契约

范围：

- 标题与默认刷新按钮
- loading / error / empty / permission
- `data-loaded` / `data-error`
- `request_id`
- `tab-change`

建议优先用例：

- `A1`
- `A2`
- `A3`
- `B1`
- `B2`
- `B3`
- `B4`
- `B6`
- `C3`
- `C4`
- `D1`
- `E4`

来源：

- [`ARTDECO_PAGE_TEMPLATE_TEST_MATRIX.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_PAGE_TEMPLATE_TEST_MATRIX.md)

退出标准：

- Skeleton 关键状态切换已有自动化保护
- 关键 emit 已有自动化保护
- `trace id` 展示链路已有自动化保护

### 批次 2：Domain 最小单测

目标：

- 在 Skeleton 稳定后，为 `ArtDecoRiskOverviewPanel` 建立第一层业务面板保护

范围：

- 风险列表渲染
- 风险等级 / 止损状态文案映射
- `action` 事件
- `tabpanel` 语义连接点

建议优先用例：

- `A1`
- `A2`
- `A3`
- `B1`
- `B5`
- `C1`
- `C4`
- `D1`
- `D2`
- `F3`

来源：

- [`ARTDECO_RISK_OVERVIEW_PANEL_TEST_MATRIX.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_RISK_OVERVIEW_PANEL_TEST_MATRIX.md)

退出标准：

- Domain 面板的输入输出契约已有自动化保护
- 关键领域文案映射已有自动化保护
- 与上层 tab 骨架的协作语义已有自动化保护

### 批次 3：Skeleton 组件集成补强

目标：

- 在单测之外，验证 `ArtDecoPageTemplate` 对 API 返回形态的兼容性

范围：

- 顶层 `request_id`
- 嵌套 `data.request_id`
- `success: false`
- 空数组 / 空对象
- `cacheTime`

建议优先用例：

- `C1`
- `C2`
- `C5`
- `C6`
- `D2`
- `D3`
- `D4`
- `E1`
- `E2`
- `E3`

退出标准：

- Skeleton 对主流响应结构的兼容行为已被保护
- tabs 和 trace id 开关行为已被保护

### 批次 4：Domain 组件集成补强

目标：

- 补齐 `ArtDecoRiskOverviewPanel` 的静态领域区与样式挂载点保护

范围：

- 行业分布区
- 集中度分析区
- 风险态 class
- 止损态 class

建议优先用例：

- `E1`
- `E2`
- `E3`
- `F1`
- `F2`
- `F4`

退出标准：

- Domain 面板的主要静态领域区已有基础保护
- 风险态视觉挂载点未丢失

### 批次 5：最小视觉回归

目标：

- 补上两类样板的最小视觉护栏

建议场景：

- `ArtDecoPageTemplate`：
  - 默认内容态
  - 错误态
  - 带 tabs 的内容态

- `ArtDecoRiskOverviewPanel`：
  - 标准内容态
  - 空列表内容态

退出标准：

- Skeleton 至少有 1 条视觉样板
- Domain 至少有 1 条视觉样板

---

## 4. 推荐文件落位策略

为了避免测试组织继续混乱，建议：

- `Core Skeleton` 测试与模板目录保持近邻
- `Domain` 测试与业务模块目录保持近邻
- 视觉样板文件按组件样板归档，不与页面级 E2E 混写

当前不建议：

- 把所有 ArtDeco 测试先堆到一个超大目录
- 把视觉回归和组件单测混成单一入口

---

## 5. 建议的执行节奏

建议每一批只做一个明确目标，不并发扩散：

1. 先完成 `批次 1`
2. 再完成 `批次 2`
3. 再决定是否进入 `批次 3` 或 `批次 5`

原因：

- 当前最重要的是先形成第一条可复制的成功样板
- 如果一开始同时开 Skeleton、Domain、视觉回归三条线，很容易再次进入“范围扩散”

---

## 6. 与 P1 主任务的关系

这份批次清单应被视为 [`ARTDECO_STANDARDIZATION_P1_TASKS.md`](/opt/claude/mystocks_spec/docs/plans/ARTDECO_STANDARDIZATION_P1_TASKS.md) 中“工作包 C：为样板组件补最小测试保护”的执行细化。

它的价值在于把“补测试”从抽象要求变成分批次、可排序、可停顿的任务流。

---

## 7. 当前最优起手式

如果下一步开始写测试代码，当前最优起手式不是随机选一个组件，而是：

1. 先为 `ArtDecoPageTemplate` 实现批次 1
2. 再为 `ArtDecoRiskOverviewPanel` 实现批次 2

这样可以先稳住平台骨架，再稳住业务面板，符合 MyStocks 当前“先骨架、后血肉”的治理路线。

---

## 8. 一句话总结

P1 测试实施不该按“哪个组件顺手就先测哪个”推进，而应按 `Core Skeleton -> Domain -> 最小视觉回归` 的顺序分批落地，先把第一条可复制的样板路径走通。
