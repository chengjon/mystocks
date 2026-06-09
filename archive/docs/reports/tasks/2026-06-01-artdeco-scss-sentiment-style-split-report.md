# ArtDeco Sentiment Analysis SCSS Split Report

日期: 2026-06-01
Function Tree 节点: `artdeco-web-design-governance/artdeco-scss-sentiment-style-split`
范围: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoSentimentAnalysis*.scss`

## 1. 变更摘要

本节点按 `docs/reports/tasks/2026-06-01-artdeco-file-size-debt-remediation-plan.md` 的第二批建议，对 `ArtDecoSentimentAnalysis.scss` 做 SCSS facade 拆分。

原入口 `ArtDecoSentimentAnalysis.scss` 保留为 facade，不改变 `ArtDecoSentimentAnalysis.vue` 中的 import 路径:

```scss
@import './ArtDecoSentimentAnalysis.layout';
@import './ArtDecoSentimentAnalysis.radar';
@import './ArtDecoSentimentAnalysis.reports';
@import './ArtDecoSentimentAnalysis.news';
@import './ArtDecoSentimentAnalysis.popularity';
@import './ArtDecoSentimentAnalysis.responsive';
```

## 2. 文件体积结果

| 文件 | 行数 | 结果 |
|---|---:|---|
| `ArtDecoSentimentAnalysis.scss` | 7 | facade，低于 500 行 |
| `ArtDecoSentimentAnalysis.layout.scss` | 17 | 低于 500 行 |
| `ArtDecoSentimentAnalysis.radar.scss` | 158 | 低于 500 行 |
| `ArtDecoSentimentAnalysis.reports.scss` | 217 | 低于 500 行 |
| `ArtDecoSentimentAnalysis.news.scss` | 300 | 低于 500 行 |
| `ArtDecoSentimentAnalysis.popularity.scss` | 269 | 低于 500 行 |
| `ArtDecoSentimentAnalysis.responsive.scss` | 77 | 低于 500 行 |

原文件基线为 1,033 行。本节点后，单个目标 SCSS 文件不再超过 500 行。

## 3. 拆分边界

拆分边界来自原文件已有语义 section，不按行数硬切:

| partial | 来源 section | 职责 |
|---|---|---|
| `layout` | root + `SENTIMENT OVERVIEW` | 页面根容器和情绪概览布局 |
| `radar` | `SENTIMENT RADAR` | 情绪雷达图、图例、中心值 |
| `reports` | `RESEARCH REPORTS` | 研报摘要、研报表格、评级/目标价样式 |
| `news` | `NEWS SENTIMENT` | 新闻情绪分布、饼图、时间线 |
| `popularity` | `POPULARITY INDICATORS` | 人气指标、gauge、讨论条、洞察卡 |
| `responsive` | `RESPONSIVE DESIGN` | 既有响应式规则，原样迁移 |

拆分后将 6 个 partial 串联，内容与拆分前 `HEAD:ArtDecoSentimentAnalysis.scss` 精确一致。该检查用于证明本节点只改变文件组织，不改变选择器顺序或 CSS 内容。

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
| 内容等价 | 串联 6 个 partial 并与 `git show HEAD:.../ArtDecoSentimentAnalysis.scss` 比较 | 通过，`exact_content_match=true` |
| 行数检查 | 本轮 7 个 SCSS 文件直接统计 | 通过，全部低于 500 行 |
| Vite Sass 编译 | `cd web/frontend && npm run build:no-types` | 通过，`EXIT_STATUS=0`，`built in 28.04s` |
| ArtDeco focused token check | `node scripts/check-artdeco-tokens.js --target-file <本轮 SCSS 文件>` | 未通过，见下方说明 |
| GitNexus pre-edit | `impact` 尝试定位 `ArtDecoSentimentAnalysis` 符号 | 未找到 Vue component 符号；本节点为 SCSS 文件组织变更 |

ArtDeco focused token check 暴露了该原 SCSS 中既有硬编码值。由于本节点的授权目标是“facade 拆分且内容等价”，未在本节点内顺手 token 化这些值。代表性失败包括:

- `layout.scss`: `280px`
- `radar.scss`: `48px`、`24px`、`400px`
- `reports.scss`: `48px`、`24px`、`200px`
- `news.scss`: `6px`、`15px`
- `popularity.scss`: `50px`、`300px`、`32px`
- `responsive.scss`: `768px`

这些值来自拆分前原文件，不是本节点新增的视觉 token 债务。后续应单独开 token 化节点处理，以免混入本次“内容等价拆分”的验证口径。

## 6. 后续建议

本节点完成了第二个 advanced ArtDeco SCSS 样板拆分。下一步建议按以下顺序推进:

1. 单独创建 `artdeco-scss-sentiment-token-cleanup`，对本报告列出的硬编码尺寸做 ArtDeco token 化。
2. 对 `ArtDecoTradingSignals.scss` 或 `ArtDecoTimeSeriesAnalysis.scss` 复用 facade + semantic partial 模式。
3. 在 SCSS 样板稳定后，再转向 `risk/Alerts.vue` 和 `market/Realtime.vue` 的 route-local extraction。
