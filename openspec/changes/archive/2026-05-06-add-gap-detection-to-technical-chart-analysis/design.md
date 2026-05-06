# Gap Detection In Technical Chart Analysis

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context

当前 reviewed technical pattern route 只覆盖 `double_top`、`double_bottom`、`head_shoulders_top`、`head_shoulders_bottom`。前端自动 overlay 也只会把这类检测结果映射成折线段。缺口识别和图表形态不同：它的主渲染对象不是折线，而是价格区间（zone）；同时它还天然需要表达“是否回补”与“属于哪类缺口”。

因此，这次主线的关键不是“再加一种 pattern name”，而是把现有 reviewed route 扩展到能够稳定表达 gap-specific 结构，同时不破坏已交付的图表形态 contract。

## Goals / Non-Goals

- Goals:
  - 在现有 reviewed route 上新增缺口识别，不制造平行 route
  - 支持 `common / breakaway / runaway / exhaustion` 四类缺口
  - 同时表达 `up/down` 方向和 `open / partially_filled / filled` 回补状态
  - 在现有 K 线 shared overlay surface 上渲染只读缺口区间
  - 保持当前自动 overlay 的 reviewed provenance 约束
- Non-Goals:
  - 不把缺口识别直接升级成交易信号系统
  - 不新增缺口告警、自动下单或回测联动
  - 不新开独立“缺口识别 API”
  - 不在本批次扩展前端自动 overlay 到周线/月线 UI，因为当前 `KLineChart.vue` 主工作台只暴露到日线

## Decisions

### Decision 1: Reuse The Existing Reviewed Pattern Route

缺口识别继续挂在现有 `GET /api/v1/technical/patterns/{symbol}` reviewed route 上，不新增 `/gaps/*` 平行入口。

原因：

- 当前仓库已经把“自动技术结构真相源”收敛到 reviewed pattern route；
- 缺口识别属于同一类自动技术结构，而不是独立业务域；
- 新 route 会迫使前端维护两套自动 overlay 拉取逻辑，并重新引入并行 contract。

### Decision 2: Extend PatternDetection With Typed Gap Fields

现有 `PatternDetection` 需要扩展缺口专用字段，而不是把所有 gap 语义硬塞进 `pattern_name` 文本里。

推荐 contract：

- `pattern_name` 新增：
  - `common_gap`
  - `breakaway_gap`
  - `runaway_gap`
  - `exhaustion_gap`
- 新增 gap-specific typed fields：
  - `gap_side: "up" | "down" | null`
  - `gap_fill_status: "open" | "partially_filled" | "filled" | null`
  - `gap_zone: GapZone | null`
- `GapZone` 应至少包含：
  - `start_timestamp`
  - `end_timestamp`
  - `upper_value`
  - `lower_value`
  - `filled_at: int | null`

对 gap detections，`direction` 在本批次保持兼容字段，但其含义收紧为“缺口方向映射后的 chart bias”：

- `gap_side=up -> direction=bullish`
- `gap_side=down -> direction=bearish`

这只是当前 reviewed overlay contract 的兼容映射，不应被解释为直接交易建议。

Gap detections 对现有字段的固定语义如下：

- `confidence`:
  - 不是固定 `1.0`
  - 是 deterministic heuristic certainty
  - 取值范围固定在 `0.55-0.95`
- `anchor_points`:
  - 对 gap detections 固定返回空数组 `[]`
  - 前端不得尝试用 gap detections 的 `anchor_points` 本地补几何
  - gap 的可渲染几何唯一真相源是 `gap_zone`
- `gap_zone.filled_at`:
  - 总是存在
  - fully filled 时为毫秒级 epoch timestamp
  - 非 fully filled 时显式返回 `null`

这样可以保持 reviewed payload 结构稳定，同时避免前端在 `anchor_points` 和 `gap_zone` 之间自行猜测。

### Decision 3: Use Deterministic Heuristics With Explicit Precedence

本批次仍采用 deterministic reviewed heuristics，而不是引入机器学习或外部 TA 库。

基础缺口成立条件：

- `gap_up`: 当前 bar 的 `low > previous.high`
- `gap_down`: 当前 bar 的 `high < previous.low`
- `raw_gap_size_ratio = gap_height / previous_close`
- 只有 `raw_gap_size_ratio >= 0.005` 时，raw gap 才能进入 reviewed classification

回补状态：

- `filled`:
  - up gap: 任一后续 bar 的 `low <= lower_value`
  - down gap: 任一后续 bar 的 `high >= upper_value`
- `partially_filled`:
  - up gap: 任一后续 bar 的 `low < upper_value` 且 `low > lower_value`
  - down gap: 任一后续 bar 的 `high > lower_value` 且 `high < upper_value`
- `open`: 后续价格未进入 gap zone

分类 precedence：

1. `exhaustion`
2. `breakaway`
3. `runaway`
4. `common`

锁定的 heuristic constants：

- `MIN_GAP_RATIO = 0.005`
- `BREAKAWAY_LOOKBACK_BARS = 10`
- `BREAKAWAY_MAX_PRE_RANGE_RATIO = 0.08`
- `BREAKAWAY_NO_FILL_WINDOW_BARS = 3`
- `RUNAWAY_TREND_LOOKBACK_BARS = 5`
- `RUNAWAY_MIN_TREND_RATIO = 0.04`
- `RUNAWAY_NO_FULL_FILL_WINDOW_BARS = 5`
- `EXHAUSTION_TREND_LOOKBACK_BARS = 5`
- `EXHAUSTION_MIN_TREND_RATIO = 0.06`
- `EXHAUSTION_FILL_CONFIRM_WINDOW_BARS = 3`

- `pre_range_ratio = (max(high[t-10:t-1]) - min(low[t-10:t-1])) / previous_close`
- `trend_strength_ratio = abs(close[t-1] - close[t-5]) / close[t-5]`

锁定的 classification 口径：

- `exhaustion`:
  - 先满足 raw gap
  - 且 gap 方向与 prior 5-bar net move 方向一致
  - 且 `trend_strength_ratio >= 0.06`
  - 且 full fill 在 3 根后续 bar 内发生
- `breakaway`:
  - 先满足 raw gap
  - 且 `pre_range_ratio <= 0.08`
  - 且 gap 后 3 根 bar 内不进入 gap zone
- `runaway`:
  - 先满足 raw gap
  - 且 gap 方向与 prior 5-bar net move 方向一致
  - 且 `trend_strength_ratio >= 0.04`
  - 且 gap 后 5 根 bar 内不发生 full fill
- `common`:
  - 满足 raw gap
  - 但不满足以上 stronger classifications

confidence 采用 deterministic category-aware scoring，而不是固定常量：

- `common_gap`: `0.55-0.70`
- `breakaway_gap`: `0.68-0.88`
- `runaway_gap`: `0.66-0.90`
- `exhaustion_gap`: `0.70-0.92`

测试应断言 reviewed classification、field semantics 和 category band，而不是把 `confidence` 写死成单个 magic number。

- `exhaustion`: 缺口前已有显著单边延伸，且缺口后短窗口内出现快速回补或反向确认
- `breakaway`: 缺口从近端整理区间外部跳出，且短窗口内不快速回补
- `runaway`: 缺口发生在已建立趋势的中段延续区间内，且不是整理突破首跳
- `common`: 满足原始 gap 条件，但不满足以上 stronger classifications

同一 raw gap event 只能输出一个 reviewed classification，不允许一条 gap 同时返回多个类别。

### Decision 3A: Treat Type Expansion As Additive-Only

这次变更对 `PatternName` 和前端 `TechnicalPatternData` 是 additive-only 扩展，不是 breaking rewrite。

已核实的当前影响面：

- backend `PatternName` 目前只在 `_technical_patterns_models.py` 中用 `Literal[...]` 固定 4 个值
- frontend 本地强类型主要集中在 `web/frontend/src/api/index.ts`
- `useKLinePatternOverlays.ts` 当前对 `pattern_name` 只按字符串透传，没有 exhaustive switch

因此，这次类型影响应被收紧为：

- 扩展 backend `PatternName` union
- 扩展 frontend API-side local type definitions
- 不要求本批次新增 discriminated union router
- 但必须验证没有下游 consumer 仍假设只有 4 种 reviewed pattern name

### Decision 4: Render Gaps As Read-Only Zones On The Shared Overlay Surface

前端不把 gap detections 画成线段，而是画成 read-only zone overlays。

推荐做法：

- 在 `useKLinePatternOverlays.ts` 中新增 `mvpGapZone` custom overlay
- automatic gap overlays 与 existing manual drawings 继续复用同一 chart surface
- 视觉上通过 `AUTO` provenance 和 gap category label 区分
- 自动缺口区间默认只读，不允许转换为可拖拽的手动画线

命名约束：

- custom overlay 名称继续沿用当前 `mvp*` 前缀约定
- 本批次使用 `mvpGapZone` 与现有 `mvpRectangle` 保持同一命名语法

这次不新增独立“缺口列表页面”；如需展示文本提示，只允许在当前 K 线工作台内做轻量标签/提示态。

### Decision 5: Keep Frontend Automatic Gap Rendering Daily-Only In This Batch

后端 reviewed route 仍可继续接受 `daily / weekly / monthly`，但前端自动缺口渲染本批次保持当前 `1day` 主工作台边界，不顺手扩范围到尚未暴露的周线/月线 UI。

原因：

- 当前 `KLineChart.vue` 的周期切换只到分钟线和日线；
- 这条主线的目标是补齐缺口识别，不是重开周期体系主线；
- 若同时扩周线/月线 UI，会把本批次扩散成新的交互范围变更。

### Decision 6: Lock The Frontend Type Changes Explicitly

前端实现不应在 overlay composable 内继续使用“无 contract 的匿名结构”去推断 gap 字段。

本批次应显式扩展：

- `web/frontend/src/api/index.ts`
  - `TechnicalPatternName`
  - `TechnicalGapSide`
  - `TechnicalGapFillStatus`
  - `TechnicalGapZone`
  - `TechnicalPatternDetection`
  - `TechnicalPatternData`
- `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`
  - 使用上述 API-side reviewed types
  - 对 `gap_zone !== null` 的 detections 走 zone overlay 分支
  - 对 `gap_zone === null` 的 legacy reviewed shape 保持现有 line-segment path

这样可以把类型影响限定在 reviewed technical API surface，而不是把 gap semantics 散落进多个局部匿名类型。

## Risks / Trade-offs

- `exhaustion` 与 `runaway` 的边界天然比双顶/头肩顶更模糊，本批次只能做到 deterministic reviewed heuristic，不应夸大为行业标准 TA truth
- 扩展 `PatternDetection` 会增加 router contract 和 frontend overlay 分支复杂度，但比平行 route 的长期成本更低
- gap zones 的前端渲染需要 custom overlay，而不是复用现有 segment mapping；实现正确性依赖 targeted frontend tests

## Migration Plan

1. 先扩 `technical-chart-analysis` spec 和 OpenSpec change
2. 先写 backend contract / detector failing tests
3. 再实现 gap detection 和 route payload
4. 再写 frontend automatic gap overlay failing tests
5. 最后实现 zone overlay 和 UI 提示态
6. 验证通过后，再更新 `FUNCTION_TREE` 中 `缺口识别`

## Open Questions

- 无。当前主线范围已固定为：existing reviewed route、四类缺口、共享 overlay、日线 UI 边界。
