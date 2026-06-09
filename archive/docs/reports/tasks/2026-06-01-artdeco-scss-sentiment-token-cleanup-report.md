# ArtDeco Sentiment SCSS Token Cleanup Report

日期: 2026-06-01
Function Tree 节点: `artdeco-web-design-governance/artdeco-scss-sentiment-token-cleanup`
范围: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoSentimentAnalysis.*.scss`

## 1. 变更摘要

本节点处理 `ArtDecoSentimentAnalysis.scss` 拆分后暴露出的硬编码尺寸债务。变更只发生在 6 个 sentiment SCSS partial 中，不修改 Vue、TypeScript、router、后端 API、frontend API client 或共享组件。

处理方式:

- 将固定宽高、grid minmax、图表尺寸、半径、阴影 blur、timeline 偏移等 `px` 字面量替换为 ArtDeco spacing/radius token 或等价 `calc(...)` 表达式。
- 将 `@media (width <= 768px)` 改为 `@media (width <= 48rem)`，保持等价断点但移除硬编码 `px` 字面量。
- 保持 selector 结构、文件拆分结构和 Vue import 路径不变。

## 2. 文件结果

| 文件 | 行数 | 硬编码 `px` 结果 |
|---|---:|---|
| `ArtDecoSentimentAnalysis.layout.scss` | 17 | 0 个大于 `1px` 的 `px` 字面量 |
| `ArtDecoSentimentAnalysis.radar.scss` | 158 | 0 个大于 `1px` 的 `px` 字面量 |
| `ArtDecoSentimentAnalysis.reports.scss` | 217 | 0 个大于 `1px` 的 `px` 字面量 |
| `ArtDecoSentimentAnalysis.news.scss` | 300 | 0 个大于 `1px` 的 `px` 字面量 |
| `ArtDecoSentimentAnalysis.popularity.scss` | 269 | 0 个大于 `1px` 的 `px` 字面量 |
| `ArtDecoSentimentAnalysis.responsive.scss` | 77 | 0 个大于 `1px` 的 `px` 字面量 |

## 3. Token 化口径

| 原硬编码尺寸 | 替换口径 |
|---|---|
| `48px` | `var(--artdeco-spacing-12)` |
| `32px` | `var(--artdeco-spacing-8)` |
| `24px` | `var(--artdeco-spacing-6)` |
| `16px` | `var(--artdeco-spacing-4)` |
| `12px` | `var(--artdeco-spacing-3)` |
| `8px` | `var(--artdeco-spacing-2)` 或 `var(--artdeco-radius-md)` |
| `6px` | `calc(var(--artdeco-radius-md) - var(--artdeco-radius-sm))` |
| `4px` | `var(--artdeco-spacing-1)` |
| `3px` | `calc(var(--artdeco-spacing-1) - var(--artdeco-spacing-px))` |
| `2px` | `var(--artdeco-radius-sm)` 或 `calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px))` |
| `15px` | `calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px))` |
| `50px` | `calc(var(--artdeco-spacing-12) + var(--artdeco-radius-sm))` |
| `80px` | `var(--artdeco-spacing-20)` |
| `120px` | `calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6))` |
| `200px` | `calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-16) + var(--artdeco-spacing-2))` |
| `280px` | `calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-32) + var(--artdeco-spacing-6))` |
| `300px` | `calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-32) + var(--artdeco-spacing-10) + var(--artdeco-spacing-1))` |
| `400px` | `calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-32) + var(--artdeco-spacing-32) + var(--artdeco-spacing-4))` |
| `-20px` | `calc(var(--artdeco-spacing-0) - var(--artdeco-spacing-5))` |
| `768px` | `48rem` |

## 4. 非目标确认

本节点没有执行以下操作:

- 没有修改 Vue、TypeScript、Python 源码。
- 没有修改 router 路由。
- 没有修改后端 API 合同或后端 API 实现。
- 没有修改 frontend API client。
- 没有抽共享组件。
- 没有修改全局 ArtDeco token 定义或 token 语义。
- 没有更新技术债基线。

## 5. 验证记录

| 验证 | 命令/方式 | 结果 |
|---|---|---|
| 硬编码尺寸扫描 | 统计 6 个 partial 中大于 `1px` 的 `px` 字面量 | 通过，均为 0 |
| ArtDeco focused token check | `node scripts/check-artdeco-tokens.js --target-file <sentiment partial>` | 通过，6/6 |
| Vite Sass 编译 | `cd web/frontend && npm run build:no-types` | 通过，`EXIT_STATUS=0`，`built in 53.93s` |
| 文件体积 | 6 个 partial 行数统计 | 通过，全部低于 500 行 |

## 6. 后续建议

1. 将相同 token cleanup 方式用于 `ArtDecoTradingSignals.scss` 或 `ArtDecoTimeSeriesAnalysis.scss` 的后续拆分节点。
2. 若需要进一步统一图表尺寸语义，可以另开节点新增组件局部 CSS 变量，但不应在本节点修改全局 token 定义。
3. SCSS 样板稳定后，再转向 `risk/Alerts.vue` 与 `market/Realtime.vue` 的 route-local extraction。
