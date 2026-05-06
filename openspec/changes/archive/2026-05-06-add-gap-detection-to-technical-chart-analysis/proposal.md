# Change: Add Gap Detection To Technical Chart Analysis

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

`FUNCTION_TREE` 仍将 `2.3 缺口识别` 标记为未闭环能力。当前 `technical-chart-analysis` capability 已经具备：

- 前端共享 K 线 overlay 层；
- reviewed backend technical pattern route；
- 结构化图表形态检测与只读自动叠加。

但它仍缺少“价格缺口”这一类高频技术结构。如果现在把缺口识别单独做成新 route、前端本地推断，或只做静态文案标签，会重新制造一套与 reviewed pattern route 平行的真相源，后续难以稳定复用到分析、告警和策略链路。

## What Changes

- 在现有 `technical-chart-analysis` capability 内新增 reviewed gap detection，而不是创建平行 capability。
- 继续复用现有 reviewed route `GET /api/v1/technical/patterns/{symbol}`，在同一 payload 里返回缺口检测结果。
- 新增四类缺口分类：`common`、`breakaway`、`runaway`、`exhaustion`，并同时覆盖 `up/down` 两个方向。
- 为缺口检测补充结构化字段：分类、方向、回补状态、可渲染的缺口区间，以及与现有 `confidence` / `anchor_points` 字段兼容的明确语义。
- 在现有 K 线共享 overlay 层上新增只读缺口区间渲染，不新开独立图层或平行前端真相源。
- 以 additive-only 方式扩展 `PatternName` 和前端 `TechnicalPatternData` 类型，不重写现有图表形态 payload。
- 保持本批次聚焦：不新增策略告警联动、不新增独立 AI/分析工作台、不扩展到新的自动交易语义。

## Impact

- Affected specs: `technical-chart-analysis`
- Affected code:
  - backend contract and route:
    - `web/backend/app/api/_technical_patterns_models.py`
    - `web/backend/app/api/_technical_patterns_router.py`
  - backend detection pipeline:
    - `web/backend/app/services/technical_pattern_detection_service.py`
    - `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py`
  - frontend automatic overlay pipeline:
    - `web/frontend/src/api/index.ts`
    - `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`
    - `web/frontend/src/components/technical/KLineChart.vue`
  - verification and governance:
    - `web/backend/tests/test_technical_patterns_router_regressions.py`
    - `web/backend/tests/test_technical_pattern_detection_service.py`
    - `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`
    - `docs/FUNCTION_TREE.md`
