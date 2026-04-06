# 审核报告：ARTDECO_WEB_DESIGN_OPTIMIZATION_RECOMMENDATIONS_2026-03-31

- **审核对象**: `docs/reports/ARTDECO_WEB_DESIGN_OPTIMIZATION_RECOMMENDATIONS_2026-03-31.md`
- **审核依据**: ArtDeco 生态系统完整文档体系（2026-02-08）
- **审核日期**: 2026-03-31

---

> 2026-04-01 状态更新
>
> - 本审查报告保留其 2026-03-31 的原始审核结论。
> - 其中指出的主问题已在后续文档治理中部分收敛：路径错误、统一规格缺失、组件分层口径漂移、11级间距表述不准等问题已在建议文档与主规范链中修正。
> - 因此，本文件现在应被理解为“历史审核记录”，不是当前建议文档的最新状态摘要。
> - 下文各节保留了 2026-03-31 审查时的原始用语，因此会继续出现 `Base/UI`、`Domain/业务`、`11级间距` 等旧口径词汇；这些词汇在本文件中仅用于历史追溯，不代表当前规范。

## 一、路径事实性错误（2处）

建议文件第1节列出了6份依据文档，其中2个路径有误：

| 建议文件中的路径 | 实际路径 | 状态 |
|---|---|---|
| `docs/guides/ARTDECO_MASTER_INDEX.md` | `docs/guides/web/ARTDECO_MASTER_INDEX.md` | **缺失 `web/` 子目录** |
| `docs/guides/ARTDECO_COMPONENT_GUIDE.md` | `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` | **缺失 `web/` 子目录** |
| 其余4条路径 | — | 正确 |

**影响**: 按建议文件给出的路径无法定位文档，会误导执行者。

---

## 二、遗漏关键治理文档（3份）

MASTER_INDEX 标注了以下 `[必读]` 或 `[样式真值]` 文档，但建议文件完全未引用：

| 遗漏文档 | 标签 | 重要性 |
|---|---|---|
| `ARTDECO_START_HERE.md` | `[必读]` | MASTER_INDEX 明确要求第一次接手先读此文件 |
| `ARTDECO_SCSS_GOVERNANCE_BASELINE.md` | `[必读][样式真值]` | 活跃的 SCSS 层级/Token 使用/兼容边界规则源 |
| `ARTDECO_FINTECH_UNIFIED_SPEC.md` | `[必读][架构]` | 定义项目如何继承 ArtDeco 风格及金融演化方向 |

此外还遗漏了：

- `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`（`[页面][验证]`）—— 页面级一致性审计基线
- `ARTDECO_GRID_QUICK_REFERENCE.md`（`[样式真值]`）—— Grid 系统使用指南

**影响**: 建议文件仅引用了6份文档中的"架构摘要"和"组件目录"，却跳过了真正定义样式规则和页面骨架的核心治理文档。执行者若仅按建议文件工作，会缺少关键的样式真值参考。

---

## 三、组件分层描述过度简化

**建议文件**（3.3节）将组件分为两层：

- "Base/UI"（原文术语：视觉/通用交互壳）
- "Domain/业务"（原文术语：业务编排）

**实际治理体系**（COMPONENT_GUIDE 第2节）定义了 **7层结构**：

| 层级 | 目录 | 职责 |
|---|---|---|
| base/ | 原子 UI | Button, Card, Input |
| core/ | 框架级能力 | Header, Breadcrumb, Skeleton |
| business/ | 通用业务交互 | FilterBar, DateRange, AlertRule |
| charts/ | 通用图表 | ArtDecoChart, KLineChartContainer |
| trading/ | 交易领域组件 | Ticker, OrderBook, PositionCard |
| advanced/ | 高阶分析 | CapitalFlow, MarketPanorama |
| specialized/ | 高定制专题 | BlockTrading, LongHuBang |

**影响**: 建议的"Base vs Domain"二分法忽略了 `core`、`business`、`charts`、`advanced`、`specialized` 五个重要层级，会导致治理盘点时职责边界模糊。

---

## 四、响应式建议与项目红线冲突

**建议文件**（3.3节）提议为组件增加治理标签"响应式状态"。

**项目 CLAUDE.md 明确规定**：

> 仅支持桌面端 Web（最小分辨率 1280x720）；禁止移动端/平板适配，禁止添加 `@media (max-width: ...)` 等响应式规则。

**影响**: 响应式治理标签在此项目中无意义（或含义需重新定义为"桌面端内断点适配"），否则可能误导执行者添加违反红线的响应式代码。

---

## 五、间距体系数字不精确（继承自上游文档）

**建议文件**（3.2节）引用"11 级间距体系（Spacing 1-32）"。

**实际 artdeco-tokens.scss** 包含 13 个编号间距级别：

```
spacing-1(4px), 2(8px), 3(12px), 4(16px), 5(20px), 6(24px),
8(32px), 10(40px), 12(48px), 16(64px), 20(80px), 24(96px), 32(128px)
```

外加 4 个语义别名（sm/md/lg/xl）和 4 个紧凑间距变量。

**溯源**: "11级"来自 System Architecture Summary 的描述，该描述本身与实际 Token 文件不一致。建议文件直接引用了这一不精确数字。

**建议**: 应以 `artdeco-tokens.scss` 为真值来源，修正为"13 级编号间距 + 4 级语义别名 + 4 级紧凑间距"。

---

## 六、命名规则建议与现状脱节

**建议文件**（3.5节）提议统一命名为 `ArtDeco[Domain][Role].vue`。

**现有组件实例**（来自 Catalog）：

- `ArtDecoKLineChartContainer` — 不符合 `[Domain][Role]` 模式
- `ArtDecoFilterBar` — 无 Domain 前缀
- `ArtDecoCodeEditor` — 无 Domain 前缀
- `ArtDecoDataSourceTable` — 无 Domain 前缀
- `HeatmapCard` — 缺少 `ArtDeco` 前缀
- `DepthChart` — 缺少 `ArtDeco` 前缀
- `TimeSeriesChart` — 缺少 `ArtDeco` 前缀

**影响**: 建议的命名规则与80+现有组件的大量实例冲突。如要推行，需提供明确的迁移策略（而非仅作为"建议"），否则会造成新旧命名共存混乱。COMPONENT_GUIDE 本身并未规定命名规则，仅规定了目录放置规则。

---

## 七、tabs/components 铁律描述不完整

**建议文件**（3.4节）提到 `views/artdeco-pages/components/` "承载业务领域展示组件"。

**COMPONENT_GUIDE 第1节"铁律"** 明确区分：

- `[domain]-tabs/`：页面级、页签块、**不可复用**、**禁止外导**
- `components/[domain]/`：通用业务、**可复用**、**无页面逻辑**

建议文件未提及 `tabs/` 与 `components/` 的职责铁律，也未提及 `[domain]-tabs/` 目录及其"严禁被该页面以外 import"的硬规则。

---

## 八、验证方案缺少关键项

**建议文件**（第4节验收建议）列出6项指标。

**COMPONENT_GUIDE 第7节 DoD** 还要求以下验证项但未被纳入：

- `npx vue-tsc --noEmit` 编译验证
- PM2 冒烟测试（`bash scripts/run_e2e_pm2.sh`）
- `@use` vs `@import` 合规检查（COMPONENT_GUIDE 5.1 要求新代码用 `@use`）

---

## 九、时间预估违反项目规范

**建议文件**（第5节路线图）给出了"P0（1-2天）、P1（2-4天）、P2（3-5天）"的时间预估。

**CLAUDE.md 明确要求**：

> 避免给时间预估或预测

---

## 十、总体评价

| 维度 | 评价 |
|---|---|
| **方向判断** | **正确**。"治理一致性强化"而非"推翻重做"的定位与 MASTER_INDEX 的治理口径一致 |
| **P0 Token 治理** | **方向正确，细节需补充**。应引用 SCSS_GOVERNANCE_BASELINE 作为真值源 |
| **P1 组件治理** | **分层简化过度**。需对齐7层结构而非二分法 |
| **P1 架构落地** | **方向正确，缺铁律细节**。需补充 tabs/components 不可外导规则 |
| **P2 页面体验** | **合理**，但响应式相关建议需修正为桌面端语义 |
| **文档引用** | **不完整**。6/11+ 核心文档被引用，3份 `[必读]` 文档遗漏 |
| **可操作性** | **中等**。路径错误和遗漏文档降低了执行可靠性 |

---

## 十一、建议处置清单

1. **修正路径**: 补充 `web/` 子目录
2. **补充引用**: 至少加入 `ARTDECO_START_HERE`、`SCSS_GOVERNANCE_BASELINE`、`FINTECH_UNIFIED_SPEC` 三份必读文档
3. **对齐组件分层**: 从二分法改为7层结构
4. **移除响应式标签**: 改为"桌面端断点适配"或直接移除
5. **补充 tabs 铁律**: 明确 `tabs/` 不可外导的硬规则
6. **移除时间预估**
7. **修正间距数字**: 引用 tokens 文件实际值
8. **命名规则降级为"探索项"**或提供迁移策略
