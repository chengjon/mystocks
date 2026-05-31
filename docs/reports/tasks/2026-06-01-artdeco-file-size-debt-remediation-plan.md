# ArtDeco Web File Size Debt Remediation Plan

日期: 2026-06-01
状态: 计划文档
Function Tree 节点: `artdeco-web-design-governance/artdeco-file-size-debt-triage`
证据来源: `reports/analysis/file-size-guard-report-2026-06-01.md`

## 1. 目标

本计划用于在继续 Web 端 ArtDeco route header shell 迁移和页面设计提升前，先处理文件体积债务的执行顺序与门禁策略。

本轮目标是先形成可审批的治理计划，不改 SCSS、Vue、路由、后端 API 合同或 frontend API client。后续进入代码实施时，应按本文的优先级逐项打开独立 Function Tree 节点，并在每个节点内保持小范围、可验证、可回退。

## 2. 实测问题

以下数字来自 `reports/analysis/file-size-guard-report-2026-06-01.md`，属于实测值。

| 指标 | 实测值 | 说明 |
|---|---:|---|
| 扫描文件总数 | 2,781 | 当前仓库扫描范围内文件 |
| 超限文件总数 | 52 | Python 800 行、Vue/TS/JS/SCSS 500 行、测试 1000 行 |
| Critical | 8 | 超过 1000 行或超过 200% |
| High | 15 | 700-999 行或 140%-200% |
| Medium | 29 | 500-699 行或 100%-140% |
| SCSS 超限 | 19 | 当前最集中的类型，约占 37% |
| Vue 超限 | 21 | 多数为视图层页面 |

## 3. 分类结论

| 类别 | 数量 | 代表文件 | 治理判断 |
|---|---:|---|---|
| SCSS advanced ArtDeco | 6 | `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.scss`、`ArtDecoBatchAnalysisView.scss` | 最高优先级。按视觉职责拆分，保留原入口 facade。 |
| SCSS global/view styles | 13 | `artdeco-tokens.scss`、`element-plus-artdeco.scss`、`bloomberg-terminal-override.scss` | 需要分阶段治理。token 和全局覆盖层风险较高，不作为第一刀。 |
| Vue active routed views | 11 | `trade/Center.vue`、`trade/Signals.vue`、`risk/Alerts.vue`、`market/Realtime.vue` | 第二优先级。优先 route-local 提取，避免立即抽全局共享组件。 |
| Vue legacy/artdeco/archive | 5 | `views/artdeco-pages/*`、`layouts/archive/*` | 先判定是否仍承担兼容或嵌入职责，不按“未出现在当前路由”直接删除。 |
| Vue shared components | 4 | `ArtDecoButton.vue`、`ArtDecoFilterBar.vue`、SSE 组件 | 需要更高测试门槛。共享组件变更要先做调用面影响分析。 |
| Generated/type monoliths | 1 | `web/frontend/src/api/types/common/all.ts` | 先找生成器和导入面，不手工拆生成产物。 |
| Test monoliths | 12 | Python/Vitest 单测大文件 | 按场景和 fixture 边界拆，不按行号硬切。 |
| TS/JS implementation | 7 | `useTradingDashboard.ts`、`TradingApiManager.ts` | 跟随相关页面或服务重构，不抢在 SCSS/Vue 之前做。 |
| Python implementation | 2 | `web/backend/app/main.py`、`technical_analysis_service.py` | 与本 ArtDeco 设计线无直接耦合，纳入独立后端治理线。 |

## 4. 执行原则

1. 禁止机械拆分。不得使用 `part1`、`part2`、`section-a` 一类按行数硬切的长期结构。
2. 文件拆分必须按职责、语义边界和依赖边界完成，并保留可解释的模块命名。
3. 不在本治理线中修改 router 路由、后端 API 合同、后端 API 实现或 frontend API client。
4. 不在第一阶段抽全局共享组件。单页面独用结构放在 route-local `components/`、`composables/`、`types.ts` 或 `formatters.ts`。
5. 只有 2 个以上活跃页面复用，且调用边界稳定时，才允许单独开节点抽到 `src/components` 或 `src/composables`。
6. 对超过 500 行的活跃路由页面，后续 route header shell 迁移必须满足债务中性：不能让文件继续增长，必要时先做 route-local 提取。
7. 任何删除、归档、兼容层退役都不属于本计划第一阶段，必须另开清理治理节点并做隐藏引用检查。
8. `artdeco-tokens.scss` 是设计系统真相层，不能作为第一批样板拆分对象。它需要单独方案确认 token 分层、兼容变量和导入稳定性。

## 5. SCSS 治理路线

### 5.1 为什么 SCSS 先行

SCSS 是本次报告中违规最多的类别，且集中在 `web/frontend/src/components/artdeco/advanced/styles/`。这些文件多是复杂业务组件样式，拆分可以降低单文件维护成本，同时对 router、API、状态管理的行为影响最小。

### 5.2 第一批样板

建议第一批选择 `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.scss`。

理由:

| 维度 | 判断 |
|---|---|
| 当前规模 | 892 行，属于 High，但低于 1000 行 Critical，适合做第一批样板 |
| 业务关联 | 与近期 `/ai/batch` ArtDeco route header 工作相关，便于复用已有上下文 |
| 风险控制 | 比 `CapitalFlow`、`ChipDistribution`、`SentimentAnalysis` 等 Critical 文件更适合作为拆分试点 |
| 目标产物 | 建立 advanced style split 的命名、导入、验证模式 |

### 5.3 拆分方式

保留原文件作为 facade，不改变现有 import 路径。拆出的文件按视觉职责命名，例如:

| 拆分候选 | 职责 |
|---|---|
| `ArtDecoBatchAnalysisView.structure.scss` | 页面骨架、section、grid、布局容器 |
| `ArtDecoBatchAnalysisView.controls.scss` | control row、filter、button group、表单控件 |
| `ArtDecoBatchAnalysisView.panels.scss` | data panel、metric panel、summary card |
| `ArtDecoBatchAnalysisView.tables.scss` | table、row、cell、density rules |
| `ArtDecoBatchAnalysisView.states.scss` | loading、empty、error、stale、disabled 状态 |

注意: 这只是候选边界。实施前必须先读取原文件结构，按真实 selector 关系决定最终拆分，不允许为了凑文件数而拆。

### 5.4 后续 SCSS 顺序

| 优先级 | 文件 | 原因 |
|---|---|---|
| P1 | `ArtDecoBatchAnalysisView.scss` | 样板拆分，风险适中 |
| P2 | `ArtDecoSentimentAnalysis.scss` | Critical，且与已完成 AI sentiment 工作相关 |
| P3 | `ArtDecoTradingSignals.scss` | 与交易信号页面治理相关 |
| P4 | `ArtDecoTimeSeriesAnalysis.scss` | 高复杂度图表样式 |
| P5 | `ArtDecoCapitalFlow.scss`、`ArtDecoChipDistribution.scss` | Critical 最高，但应等待样板成熟后处理 |
| P6 | `artdeco-tokens.scss`、`element-plus-artdeco.scss`、`artdeco-global.scss` | 设计系统基础层，需单独方案和更宽验证 |

## 6. Vue 页面治理路线

### 6.1 活跃路由页面优先

Vue 超限文件中，优先处理活跃 routed views，而不是先处理 legacy/artdeco/archive。活跃页面直接影响当前用户体验，也会影响 route header shell 后续迁移质量。

建议优先序:

| 优先级 | 文件 | 治理方式 |
|---|---|---|
| P1 | `web/frontend/src/views/risk/Alerts.vue` | 已完成 ArtDeco header 迁移，下一步适合 route-local 提取状态、列表、过滤区 |
| P2 | `web/frontend/src/views/market/Realtime.vue` | 数据密集高价值页面，适合作为信息密度和状态反馈样板 |
| P3 | `web/frontend/src/views/trade/Signals.vue` | 交易信号复杂页，适合提取 formatter、status、signal list |
| P4 | `web/frontend/src/views/trade/Center.vue` | 846 行，交易工作台复杂度高，需先做 shape/readiness |
| P5 | `web/frontend/src/views/data/Advanced.vue`、`data/FundFlow.vue` | 数据域页面，适合按筛选、结果、状态拆 |
| P6 | `web/frontend/src/views/market/LHB.vue`、`trade/History.vue` | 在 route header shell 迁移前先做债务中性约束 |

### 6.2 route-local 提取边界

对于单个页面内的超限问题，默认使用下列本地边界:

| 目标文件 | 使用时机 |
|---|---|
| `./components/<PageName>HeaderTools.vue` | 页面头部附属按钮、状态 chip、操作控件较多 |
| `./components/<PageName>FilterBar.vue` | 筛选区复杂且不跨页面复用 |
| `./components/<PageName>DataPanel.vue` | 主数据表、图表或列表区域可独立阅读 |
| `./components/<PageName>StatusStrip.vue` | loading、stale、partial、error 状态有统一展示逻辑 |
| `./composables/use<PageName>State.ts` | 页面状态、刷新、筛选、派生值明显混杂在 SFC 中 |
| `./formatters.ts` | 数字、百分比、状态文案、风险等级映射 |
| `./types.ts` | 页面私有 DTO、UI 状态枚举、表格 row 类型 |

这些文件必须位于页面邻近目录，直到出现真实的多页面复用证据。不得为了“组件化”提前推到全局设计系统。

## 7. route header shell 后续约束

当前 route header shell 迁移没有改 router、API 合同或 frontend API client，这是正确边界。后续继续迁移时应新增一条文件体积约束:

| 页面状态 | 允许动作 |
|---|---|
| 页面低于 500 行 | 可继续做 route header shell 迁移，但保持小 diff |
| 页面已经超过 500 行 | 先做 route-local 提取，或在同一节点内证明净行数不增长 |
| 页面处于 Critical 超限 | 不直接叠加视觉迁移，先做拆分 brief 和验证门禁 |
| 页面有未清楚的 legacy/compat 职责 | 先做生命周期判定，不做删除或替换 |

这意味着 `market/Technical.vue` 这类未在报告中列为超限的页面，可以继续按原 route header shell 路线推进；`risk/Alerts.vue`、`market/Realtime.vue`、`trade/Signals.vue` 等超限页面，应先纳入本文件的债务中性策略。

## 8. 验证门禁

每个后续代码实施节点至少需要通过以下门禁:

| 门禁 | 要求 |
|---|---|
| Function Tree | 独立节点、证据、授权范围、closeout 完整 |
| GitNexus | 修改符号前做 impact；提交前做 staged detect_changes |
| file-size guard | 本节点目标文件行数下降；不得新增超限文件 |
| 结构语法 | Vue/TS/SCSS 结构性语法错误为 0 |
| lint | 运行相关 frontend lint 或更小范围静态检查 |
| ArtDeco token | 新增样式不得引入硬编码主题值，继续使用既有 ArtDeco token |
| E2E/visual | 影响活跃路由时运行对应页面的 focused E2E 或 screenshot 检查 |
| OpenSpec | 若引入新的设计系统能力、共享组件模式或架构模式，必须创建或更新 OpenSpec；纯 facade 拆分不需要新增 OpenSpec |
| staged diff | 只包含授权范围内文件，且不夹带已有 dirty worktree 改动 |

## 9. 下一步任务计划

| 顺序 | 建议节点 | 目标 | 产物 |
|---:|---|---|---|
| 1 | `artdeco-scss-batch-analysis-style-split` | 对 `ArtDecoBatchAnalysisView.scss` 做样板拆分 | facade + route/component scoped partials + 验证记录 |
| 2 | `artdeco-scss-sentiment-style-split` | 处理 Critical 的 `ArtDecoSentimentAnalysis.scss` | 复用样板拆分规则 |
| 3 | `artdeco-risk-alerts-local-extraction` | 对 `risk/Alerts.vue` 做 route-local 提取 | 页面行数下降，保留已完成 header shell 行为 |
| 4 | `artdeco-market-realtime-local-extraction` | 对 `market/Realtime.vue` 做数据密集页面拆分 | 为后续 route header/polish 提供干净结构 |
| 5 | `artdeco-token-foundation-split-proposal` | 规划 `artdeco-tokens.scss` 和全局覆盖层 | OpenSpec 或设计治理 brief |
| 6 | `artdeco-file-size-guard-baseline-gate` | 将大文件指标纳入可追踪观察或硬门禁 | 基线/例外/CI 口径，不在本节点直接更新 |

## 10. 本节点不做事项

本节点只输出计划文档和 Function Tree closeout，不执行以下事项:

- 不改任何 SCSS、Vue、TypeScript、Python 源码。
- 不改 router 路由。
- 不改后端 API 合同或后端 API 实现。
- 不改 frontend API client。
- 不抽共享组件。
- 不删除、归档或移动 legacy 文件。
- 不更新 `reports/analysis/tech-debt-baseline.json`。
- 不新增 OpenSpec change。

## 11. 建议结论

进入下一步前，应先批准一个小型样板拆分节点，优先处理 `ArtDecoBatchAnalysisView.scss`。该节点风险低于直接拆 Critical SCSS，也不会改变运行时路由或 API 合同。样板验证通过后，再把同一拆分规则推广到 `ArtDecoSentimentAnalysis.scss` 和活跃路由 Vue 页面。

若用户希望继续 route header shell 迁移，应优先选择未超限页面，或对超限页面同时满足“净行数不增长、局部提取可回退、无 API/router/client 改动”的约束。
