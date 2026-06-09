# ArtDeco Batch Analysis SCSS Split Report

日期: 2026-06-01
Function Tree 节点: `artdeco-web-design-governance/artdeco-scss-batch-analysis-style-split`
范围: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView*.scss`

## 1. 变更摘要

本节点按 `docs/reports/tasks/2026-06-01-artdeco-file-size-debt-remediation-plan.md` 的第一批样板建议，对 `ArtDecoBatchAnalysisView.scss` 做 SCSS facade 拆分。

原入口 `ArtDecoBatchAnalysisView.scss` 保留为 facade，不改变 `ArtDecoBatchAnalysisView.vue` 中的 import 路径:

```scss
@import './ArtDecoBatchAnalysisView.layout';
@import './ArtDecoBatchAnalysisView.progress';
@import './ArtDecoBatchAnalysisView.results';
@import './ArtDecoBatchAnalysisView.report';
@import './ArtDecoBatchAnalysisView.responsive';
```

## 2. 文件体积结果

| 文件 | 行数 | 结果 |
|---|---:|---|
| `ArtDecoBatchAnalysisView.scss` | 6 | facade，低于 500 行 |
| `ArtDecoBatchAnalysisView.layout.scss` | 33 | 低于 500 行 |
| `ArtDecoBatchAnalysisView.progress.scss` | 311 | 低于 500 行 |
| `ArtDecoBatchAnalysisView.results.scss` | 243 | 低于 500 行 |
| `ArtDecoBatchAnalysisView.report.scss` | 198 | 低于 500 行 |
| `ArtDecoBatchAnalysisView.responsive.scss` | 112 | 低于 500 行 |

原文件基线为 893 行。本节点后，单个目标 SCSS 文件不再超过 500 行。

## 3. 拆分边界

拆分边界来自原文件已有语义 section，不按行数硬切:

| partial | 来源 section | 职责 |
|---|---|---|
| `layout` | root + `BATCH OVERVIEW` | 页面根容器和批量概览布局 |
| `progress` | `BATCH PROGRESS` | 批量进度、gauge、status pie、type bar |
| `results` | `BATCH RESULTS` | 结果摘要、结果列表、表格 row/cell |
| `report` | `BATCH REPORT` | 报告摘要、洞察列表、报告操作 |
| `responsive` | `RESPONSIVE DESIGN` | 既有响应式规则，原样迁移 |

拆分后将 5 个 partial 串联，内容与拆分前 `HEAD:ArtDecoBatchAnalysisView.scss` 精确一致。该检查用于证明本节点只改变文件组织，不改变选择器顺序或 CSS 内容。

## 4. 非目标确认

本节点没有执行以下操作:

- 没有修改 Vue、TypeScript、Python 源码。
- 没有修改 router 路由。
- 没有修改后端 API 合同或后端 API 实现。
- 没有修改 frontend API client。
- 没有抽共享组件。
- 没有修改设计 token 或全局 ArtDeco token 语义。
- 没有更新技术债基线。

## 5. 验证记录

| 验证 | 命令/方式 | 结果 |
|---|---|---|
| 内容等价 | 串联 5 个 partial 并与 `git show HEAD:.../ArtDecoBatchAnalysisView.scss` 比较 | 通过，`exact_content_match=true` |
| 行数检查 | 本轮 6 个 SCSS 文件直接统计 | 通过，全部低于 500 行 |
| ArtDeco focused token check | `node scripts/check-artdeco-tokens.js --target-file <本轮 SCSS 文件>` | 通过，6/6 |
| Vite Sass 编译 | `cd web/frontend && npm run build:no-types` | 通过，`EXIT_STATUS=0`，`built in 26.62s` |
| GitNexus pre-edit | `impact` 尝试定位 `ArtDecoBatchAnalysisView` 符号 | 未找到 Vue component 符号；本节点为 SCSS 文件组织变更 |

补充说明: `npm run lint:artdeco:changed` 当前失败在仓库已有的 `src/views/advanced-analysis/*View.vue` token 债务上，例如 `MarketPanoramaView.vue`、`SentimentAnalysisView.vue`、`TradingSignalsView.vue`。本轮改动的 6 个 SCSS 文件已通过 focused token check。

## 6. 后续建议

本节点建立了 advanced ArtDeco SCSS 拆分样板。下一步建议按以下顺序推进:

1. 对 `ArtDecoSentimentAnalysis.scss` 复用同一 facade + semantic partial 模式。
2. 对 `risk/Alerts.vue` 做 route-local 提取，降低 Vue 视图层文件体积。
3. 对 `market/Realtime.vue` 做数据密集页面 local extraction，再继续页面 polish。
