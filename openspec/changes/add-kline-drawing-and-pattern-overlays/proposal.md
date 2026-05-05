# Change: Add K-line Drawing and Pattern Overlays

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

`FUNCTION_TREE` 当前将 `2.2 画线工具` 与 `2.3 图表形态` 标记为未闭环能力。现状存在两个明显缺口：

- 前端 [KLineChart.vue](/opt/claude/mystocks_spec/web/frontend/src/components/technical/KLineChart.vue) 已具备 K 线渲染、指标叠加、缩放和平移，但没有交互式画线工具；
- 后端现有技术形态链路仍以占位或推断标签为主，尚未提供可审计的真实图表形态识别结果。

如果继续以“前端先拼交互、后端先回占位标签”的方式推进，这两个能力会各自演化成新的平行真相源：手动画线只存在于前端，自动形态只是一组并不可信的字符串标签，后续无法稳定复用到分析、告警或策略链路中。

## What Changes

- 新增 `technical-chart-analysis` capability，定义 K 线画线工具与自动图表形态识别的统一能力边界。
- 该 capability 的当前提案锚点位于 `openspec/changes/add-kline-drawing-and-pattern-overlays/specs/technical-chart-analysis/spec.md`，批准归档后进入 `openspec/specs/technical-chart-analysis/spec.md` 作为长期规范。
- 规定画线工具 MVP 由前端负责，最小工具集固定为：`趋势线`、`水平线`、`矩形`。
- 规定自动图表形态 MVP 由后端负责，最小形态集固定为：`双顶`、`双底`、`头肩顶`、`头肩底`。
- 规定手动画线与自动形态必须复用同一张 K 线 overlay 渲染层，但在 UI 上显式区分来源。
- 规定自动图表形态结果必须包含结构化锚点与置信度，不能再由 symbol/period 规则推断出“伪识别结果”冒充真实检测。
- 规定自动图表形态在前端默认只读展示，不允许被当作手动画线直接拖拽修改。

## Impact

- Affected specs: `technical-chart-analysis`
- Affected code:
  - frontend K-line surfaces under `web/frontend/src/components/technical/` and related analysis views
  - frontend overlay orchestration under `web/frontend/src/components/technical/composables/useChartOverlays.ts`
  - backend technical pattern route at `web/backend/app/api/_technical_patterns_router.py`, mounted by `web/backend/app/api/technical_analysis.py`
  - backend analyzers under `src/advanced_analysis/`
  - future FUNCTION_TREE status updates for `2.2` and `2.3`
