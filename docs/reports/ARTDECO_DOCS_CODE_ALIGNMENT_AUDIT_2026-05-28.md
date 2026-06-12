# ArtDeco 文档体系与代码事实对齐审核报告

> **审核日期**: 2026-05-28
> **审核范围**: 8 份 ArtDeco 文档
> **审核方法**: 逐文档交叉验证，以 `web/frontend/` 源码为唯一事实来源
> **审核结果**: 3 处数量偏差 + 1 处路由例外遗漏 + 4 处未记录目录

---

## 一、审核文件清单

| # | 文件 | 类型 | 行数 |
|---|------|------|------|
| 1 | `docs/guides/web/ARTDECO_MASTER_INDEX.md` | 活跃治理索引 | 232 |
| 2 | `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` | 活跃统一规格 | 281 |
| 3 | `web/frontend/ARTDECO_COMPONENTS_CATALOG.md` | 组件全景目录 | 231 |
| 4 | `docs/api/ArtDeco_System_Architecture_Summary.md` | 运行时架构摘要 | 232 |
| 5 | `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` | 组件开发指南 | 227 |
| 6 | `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md` | 历史基线总结 | 200 |
| 7 | `docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md` | 兼容转发入口 | 22 |
| 8 | `docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md` | 兼容转发入口 | 22 |

---

## 二、总体评估

8 份文档整体质量较高，核心架构描述（三层容器模式、样式真值链、路由与 ArtDeco 边界、组件分层）与代码事实一致。发现的偏差集中在**统计数字**和**清单完整性**两个维度，属于维护滞后而非结构性错误。

---

## 三、逐文档分析

### 3.1 docs/guides/web/ARTDECO_MASTER_INDEX.md

**职责**: ArtDeco 文档体系唯一总目录。

| 检查项 | 结果 |
|--------|------|
| 活跃治理文档列表链接可达 | ✓ 全部可达 |
| 兼容入口指向正确 | ✓ 指向 `docs/guides/web/` 正文 |
| `DESIGN.md` 提升为设计契约主链的描述 | ✓ 与 DESIGN.md 实际内容一致 |
| 引用的治理/运行时/历史文档存在性 | ✓ 均存在 |
| 路由例外清单完整性 (§4.1) | ✗ **遗漏 1 条**: 文档列 4 条，router 实际 5 条（缺 `KLineAnalysis.vue`） |
| 维护规则需同步文档清单 (§6) | ⚠ 缺少 `ARTDECO_COMPONENT_GUIDE.md` |

**证据**（路由路径为审核者注释，非 grep 原文）:

```bash
$ grep -n 'artdeco-pages' web/frontend/src/router/index.ts
35:        component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
147:            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'),
171:            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'),
277:            component: () => import('@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'),
348:            component: () => import('@/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue'),
```

对应路由:
- 行 35 → `/dashboard`
- 行 147 → `/strategy/signals`
- 行 171 → `/strategy/pos`
- 行 277 → `/risk/pnl`
- 行 348 → `/data/graphics/:symbol` ← 文档均未列出

**结论**: 需将第 5 条路由例外补入 §4.1。§6 维护规则需追加 `ARTDECO_COMPONENT_GUIDE.md`。

---

### 3.2 docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md

**职责**: ArtDeco Fintech 统一规格，定义设计身份、目录边界、运行时承载模式。

| 检查项 | 结果 |
|--------|------|
| 5 个样式主链文件存在 | ✓ |
| 字体 Cinzel + Barlow + JetBrains Mono | ✓ `artdeco-tokens.scss` 第 29-31, 108-110 行 |
| 间距 13 级别 | ✓ `artdeco-tokens.scss` 第 344-358 行 |
| `--artdeco-transition-quick = 200ms` / `--artdeco-transition-base = 400ms` | ✓ 第 427-428 行 |
| `--artdeco-glow-profit` / `--artdeco-glow-loss` | ✓ 第 417-418 行 |
| `--ad-*` 状态机 token（`artdeco-tokens.scss` 内 85 处定义） | ✓ |
| ArtDecoBadge 9 种语义变体 | ✓ props: default/active/neutral/gold/profit/loss/holding/pending/warning |
| ArtDecoHeader 品牌 chrome 收敛 (0 处 "MyStocks ArtDeco" 文本) | ✓ |
| ArtDecoCollapsibleSidebar 位于 `trading/` | ✓ |
| 三种容器模式描述 | ✓ 文件均存在 |
| 共享头部摘要 (useHeaderSummary → ArtDecoLayoutEnhanced → useArtDecoDashboard) | ✓ 数据流正确 |
| `pageConfig.ts` 不唯一事实源 | ✓ 描述准确 |
| 路由例外清单 (§2.3) | ✗ 仅 4 条，缺 `KLineAnalysis.vue` |
| E2E 验证基线 (10/10 stable) | ⚠ 2026-04-19 快照，需重验证 |

**结论**: 核心规格声明准确。需补入第 5 条路由例外。E2E 基线建议标注为历史快照。

---

### 3.3 web/frontend/ARTDECO_COMPONENTS_CATALOG.md

**职责**: ArtDeco 生态组件全景目录，记录所有 Vue 组件数量与分布。

| 检查项 | 文档声称 | 实际值 | 偏差 |
|--------|----------|--------|------|
| `base/` | 14 | 14 | — |
| `core/` | 14 | 14 | — |
| `business/` | 11 | 11 | — |
| `charts/` | 9 | 9 | — |
| `trading/` | 13 | 13 | — |
| `advanced/` | 10 | 10 | — |
| `specialized/` | 2 | 2 | — |
| **Reusable assets 合计** | **73** | **73** | — |
| `views/artdeco-pages/components/` | **23** | **24** | **−1** ⚠ |
| 各 `*-tabs/` 及 settings 数量 | 全部准确 | 全部准确 | — |
| 域块合计 (§5.8) | 54 | 54 | — |
| 顶层容器与模板 | 12 | 12 | — |
| **ArtDeco 生态 Vue 总计 (§7)** | **162** | **163** (73+90) | **−1** ⚠ |
| `views/artdeco-pages/` 总数 | **89** | **90** | **−1** ⚠ |
| 路由例外清单 (§6.3) | 4 条 | 5 条 | **−1** ⚠ |
| `ml-tabs/` 目录 | 未提及 | 存在（空目录） | 遗漏 |

**根因**: 目录遗漏了 `DashboardMarketPanorama.vue`（位于 `views/artdeco-pages/components/`）。该文件导致 `components/` 数量从 23 → 24，进而导致总数从 162 → 163。

**证据**:

```bash
$ find web/frontend/src/components/artdeco -name '*.vue' | wc -l     # → 73  ✓
$ find web/frontend/src/views/artdeco-pages -name '*.vue' | wc -l   # → 90  ✗ (声称 89)
$ ls views/artdeco-pages/components/*.vue | wc -l                    # → 24  ✗ (声称 23)
```

**结论**: 4 处数量需修正，追加 `DashboardMarketPanorama`，补入第 5 条路由例外。

---

### 3.4 docs/api/ArtDeco_System_Architecture_Summary.md

**职责**: 运行时角度总结 ArtDeco 前端体系六层架构。

| 检查项 | 结果 |
|--------|------|
| 六层架构描述 | ✓ 与代码结构一致 |
| 三种容器模式 + Layout 共享摘要模式 | ✓ 文件均存在 |
| 设计令牌事实点 (§5) | ✓ `artdeco-tokens.scss` 全部确认 |
| 组件边界 7 层分层 | ✓ |
| 代表性页面映射 6 个 | ✓ 文件均存在 |
| `/trade/terminal` 例外确认 | ✓ TradingDashboard.vue |
| 路由例外清单 (§3.3) | ✗ 仅 4 条，缺 `KLineAnalysis.vue` |
| `pageConfig.ts` 不是唯一真源 | ✓ 描述准确 |

**结论**: 架构描述准确。§3.3 需补入第 5 条路由例外。

---

### 3.5 docs/guides/web/ARTDECO_COMPONENT_GUIDE.md

**职责**: ArtDeco 组件放置规则、命名边界和开发准入标准。

| 检查项 | 结果 |
|--------|------|
| 6 条铁律 | ✓ 与代码结构一致 |
| 目录治理矩阵 10 个目录 | ✓ |
| `*-tabs` 规则 | ✓ |
| 决策树 5 问 | ✓ 逻辑完整 |
| ArtDecoBadge 9 种语义变体 | ✓ props 确认 |
| ArtDecoStatus dot-status 专责 | ✓ |
| 桌面端约束 | ✓ |
| 提交前检查清单 | ✓ |
| §10 与其他文档关系 | ⚠ `ARTDECO_SCSS_GOVERNANCE_BASELINE.md` 缺 `docs/guides/web/` 前缀 |

**结论**: 组件治理规则与代码完全对齐。仅 §10 路径前缀需统一。

---

### 3.6 docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md

**职责**: V3 升级历史基线 + 当前口径汇总。

| 检查项 | 结果 |
|--------|------|
| Reusable assets: 73 | ✓ |
| Page-level assets: **89** | ✗ 实际 **90** (−1) |
| 设计身份/字体/颜色/间距基线 | ✓ 与代码一致 |
| 兼容入口 4 个 | ✓ 均存在且为转发 |
| 里程碑时间线 | ✓ 历史记录合理 |
| E2E 基线 (10/10) | ⚠ 历史快照 |

**结论**: §2 当前基线表 Page-level assets 从 89 修正为 90。

---

### 3.7 docs/guides/ARTDECO_FINTECH_UNIFIED_SPEC.md (兼容入口)

| 检查项 | 结果 |
|--------|------|
| 转发目标正确 | ✓ |
| 声明为历史兼容入口 | ✓ |

**结论**: 无问题。

---

### 3.8 docs/api/ARTDECO_SYSTEM_ARCHITECTURE_SUMMARY.md (兼容入口)

| 检查项 | 结果 |
|--------|------|
| 转发目标正确 | ✓ |
| 声明为历史兼容入口 | ✓ |

**结论**: 无问题。

---

## 四、跨文档一致性问题

### 4.1 路由例外清单不同步（影响 4 份文档）

| 文档 | 章节 | 列出的例外 |
|------|------|-----------|
| `ARTDECO_MASTER_INDEX.md` | §4.1 | 4 条 |
| `ARTDECO_FINTECH_UNIFIED_SPEC.md` | §2.3 | 4 条 |
| `ARTDECO_COMPONENTS_CATALOG.md` | §6.3 | 4 条 |
| `ArtDeco_System_Architecture_Summary.md` | §3.3 | 4 条 |

**缺失的第 5 条例外**:

```
路径: /data/graphics/:symbol
名称: stock-graphics
组件: views/artdeco-pages/analysis-tabs/KLineAnalysis.vue
```

### 4.2 组件总数不同步（影响 2 份文档）

| 指标 | CATALOG | V3_SUMMARY | 实际 |
|------|---------|------------|------|
| `views/artdeco-pages/` Vue 文件 | 89 | 89 | **90** |
| ArtDeco 生态 Vue 总数 | 162 | — | **163** |
| `components/` 数量 | 23 | — | **24** |

根因: 目录遗漏了 `DashboardMarketPanorama.vue`。

### 4.3 未记录的目录

| 目录 | 状态 |
|------|------|
| `views/artdeco-pages/ml-tabs/` | 空目录 (0 个 .vue 文件) |
| `views/artdeco-pages/market/` | 空目录 |
| `views/artdeco-pages/risk/` | 空目录 |
| `views/artdeco-pages/trade/` | 空目录 |

---

## 五、修订建议汇总

### 必须修正（P0/P1）

| 优先级 | 文档 | 修正内容 |
|--------|------|----------|
| **P0** | `ARTDECO_COMPONENTS_CATALOG.md` §4 | `components/` 数量 23 → 24，追加 `DashboardMarketPanorama` |
| **P0** | `ARTDECO_COMPONENTS_CATALOG.md` §7 | 总览表: `views/artdeco-pages` 89 → 90，合计 162 → 163 |
| **P0** | `ARTDECO_V3_COMPLETE_SUMMARY.md` §2 | Page-level assets 89 → 90 |
| **P1** | `ARTDECO_MASTER_INDEX.md` §4.1 | 路由例外追加 `KLineAnalysis.vue` |
| **P1** | `ARTDECO_FINTECH_UNIFIED_SPEC.md` §2.3 | 路由例外追加 `KLineAnalysis.vue` |
| **P1** | `ARTDECO_COMPONENTS_CATALOG.md` §6.3 | 路由例外追加 `KLineAnalysis.vue` |
| **P1** | `ArtDeco_System_Architecture_Summary.md` §3.3 | 路由例外追加 `KLineAnalysis.vue` |

### 建议修正（P2/P3）

| 优先级 | 文档 | 修正内容 |
|--------|------|----------|
| **P2** | `ARTDECO_MASTER_INDEX.md` §6 | 维护规则需同步文档追加 `ARTDECO_COMPONENT_GUIDE.md` |
| **P2** | `ARTDECO_COMPONENT_GUIDE.md` §10 | `ARTDECO_SCSS_GOVERNANCE_BASELINE.md` 补全 `docs/guides/web/` 前缀 |
| **P2** | `ARTDECO_FINTECH_UNIFIED_SPEC.md` §6.1 | E2E 基线标注"基于 2026-04-19 快照"；下次 ArtDeco 文档更新前重新执行 E2E 验证 |
| **P3** | 全部 | 对 4 个空目录做统一处置决策（删除或补充说明） |

---

## 六、未覆盖的文档

以下 ArtDeco 文档在 MASTER_INDEX 中被引用，但不在此次 8 文件审核范围内：

- `docs/guides/web/ARTDECO_START_HERE.md`
- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
- `docs/guides/web/ARTDECO_PAGE_TEMPLATE_GUIDE.md`
- `docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`
- `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
- `docs/guides/frontend-structure.md`
- `DESIGN.md`

以上文件均经验证存在且可读，建议后续一并审核以形成完整的 ArtDeco 文档体系对齐闭环。
