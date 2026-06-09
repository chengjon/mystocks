# ArtDeco Trading Signals SCSS Split Report

日期: 2026-06-01
Function Tree 节点: `artdeco-web-design-governance/artdeco-scss-trading-signals-style-split`
范围: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTradingSignals*.scss`

## 1. 变更摘要

本节点按 `docs/reports/tasks/2026-06-01-artdeco-file-size-debt-remediation-plan.md` 的 advanced ArtDeco SCSS 治理顺序，对 `ArtDecoTradingSignals.scss` 做 SCSS facade 拆分。

原入口 `ArtDecoTradingSignals.scss` 保留为 facade，不改变 `ArtDecoTradingSignals.vue` 中的 import 路径:

```scss
@import './ArtDecoTradingSignals.layout';
@import './ArtDecoTradingSignals.active';
@import './ArtDecoTradingSignals.history';
@import './ArtDecoTradingSignals.strategy';
@import './ArtDecoTradingSignals.responsive';
```

## 2. 文件体积结果

| 文件 | 行数 | 结果 |
|---|---:|---|
| `ArtDecoTradingSignals.scss` | 6 | facade，低于 500 行 |
| `ArtDecoTradingSignals.layout.scss` | 34 | 低于 500 行 |
| `ArtDecoTradingSignals.active.scss` | 261 | 低于 500 行 |
| `ArtDecoTradingSignals.history.scss` | 196 | 低于 500 行 |
| `ArtDecoTradingSignals.strategy.scss` | 123 | 低于 500 行 |
| `ArtDecoTradingSignals.responsive.scss` | 86 | 低于 500 行 |

原文件基线为 696 行。本节点后，单个目标 SCSS 文件不再超过 500 行。

## 3. 拆分边界

拆分边界来自原文件已有语义 section，不按行数硬切:

| partial | 来源 section | 职责 |
|---|---|---|
| `layout` | root + `SIGNALS OVERVIEW` | 页面根容器和信号概览布局 |
| `active` | `ACTIVE SIGNALS` | 实时信号列表、信号强度、指标、操作 |
| `history` | `SIGNAL HISTORY` | 历史表格、行状态、强度 mini bar |
| `strategy` | `SIGNAL STRATEGY` | 策略配置、配置项、信号类型说明 |
| `responsive` | `RESPONSIVE DESIGN` | 既有响应式规则，原样迁移 |

拆分后将 5 个 partial 串联，内容与拆分前 `HEAD:ArtDecoTradingSignals.scss` 精确一致。该检查用于证明本节点只改变文件组织，不改变选择器顺序或 CSS 内容。

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
| 内容等价 | 串联 5 个 partial 并与 `git show HEAD:.../ArtDecoTradingSignals.scss` 比较 | 通过，`exact_content_match=true` |
| 行数检查 | 本轮 6 个 SCSS 文件直接统计 | 通过，全部低于 500 行 |
| 硬编码尺寸扫描 | 统计本轮 6 个 SCSS 文件中大于 `1px` 的 `px` 字面量 | 通过，均为 0 |
| ArtDeco focused token check | `node scripts/check-artdeco-tokens.js --target-file <本轮 SCSS 文件>` | 通过，6/6 |
| Vite Sass 编译 | `cd web/frontend && npm run build:no-types` | 通过，`EXIT_STATUS=0`，`built in 37.65s` |
| GitNexus pre-edit | `impact` 尝试定位 `ArtDecoTradingSignals` 符号 | 未找到 Vue component 符号；本节点为 SCSS 文件组织变更 |

## 6. 后续建议

本节点完成第三个 advanced ArtDeco SCSS 样板拆分。下一步建议:

1. 对 `ArtDecoTimeSeriesAnalysis.scss` 复用同一 facade + semantic partial 模式。
2. 若 `ArtDecoTimeSeriesAnalysis.scss` 拆分后暴露 token 债务，再单独开 token cleanup 节点。
3. SCSS 样板线完成后，再转向 `risk/Alerts.vue` 与 `market/Realtime.vue` 的 route-local extraction。
