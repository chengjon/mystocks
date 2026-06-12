# PRODUCT.md & DESIGN.md 审计报告

> 审计日期: 2026-05-10
> 审计范围: PRODUCT.md、DESIGN.md、.impeccable/design.json 对照代码库实际实现
> 审计依据: `artdeco-tokens.scss`、`artdeco-quant-extended.scss`、`fintech-design-system.scss`、全局搜索

---

## 一、总体判定

| 文件 | 判定 | 问题数 |
|------|------|--------|
| PRODUCT.md | 基本准确，1处口径不一致 | 1 |
| DESIGN.md | 大体准确，4处需要修正 | 4 |

未发现虚构情节。所有描述均可追溯到代码库中的实际实现，但存在遗漏和不一致。

---

## 二、PRODUCT.md 逐项核实

### 准确项（无需修改）

| 声明 | 代码库证据 |
|------|-----------|
| 面向A股个人量化投资者/小团队 | CLAUDE.md 明确"个人/小型量化投资者"，多处 A 股组件 |
| 本地部署，非 SaaS | CLAUDE.md "个体本地化部署（单用户/小团队），非 SaaS" |
| 桌面端最低 1280x720 | `artdeco-tokens.scss` 有 `--artdeco-breakpoint-lg: 1280px`，`artdeco-quant-extended.scss` 有 `@media (width >= 1280px)` |
| WCAG AA 对比度 | `artdeco-tokens.scss` 注释标注 WCAG AA，存在 `accessibility-focus-enhancement.scss` |
| `prefers-reduced-motion` 降级 | 12+ 组件和全局样式包含该媒体查询 |
| 红涨绿跌 A 股惯例 | `--artdeco-rise: #FF5252`，`--artdeco-down: #00E676` |
| `font-variant-numeric: tabular-nums` | `artdeco-tokens.scss` 和 `artdeco-quant-extended.scss` 均使用 |
| 品牌性格"精确、权威、克制" | 与代码中金色光晕的克制使用、数据优先的设计一致 |
| 反参考（禁止通用 SaaS/消费金融/过度装饰金融） | 代码中确实未见 Tailwind-blue、渐变英雄区、圆角粉彩等 |

### 需修正项

#### P-1: "禁止移动端/平板适配"与代码现实矛盾

**PRODUCT.md 原文 (Accessibility & Inclusion):**
> Desktop-only platform (minimum 1280x720); no mobile or tablet adaptation required

**代码库事实:**

以下文件包含 `@media (width <= 768px)` 响应式规则：

- `web/frontend/src/styles/artdeco-grid.scss`
- `web/frontend/src/styles/artdeco-layout-fix.scss`
- `web/frontend/src/styles/theme-apply.scss`
- `web/frontend/src/styles/app-core-styles.scss`
- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`
- `web/frontend/src/views/stocks/Screener.vue`
- `web/frontend/src/views/trade/Reconciliation.vue`
- 以及其他 10+ 组件

**建议:** 在 Accessibility 节补充说明：

> Desktop-only (minimum 1280x720). Some 768px breakpoint rules exist in legacy code but are not a supported target.

或者，如果 768px 断点是有意维护的，则修正为：

> Primary target: desktop 1280x720+. Layout degrades gracefully at 768px but mobile is not supported.

---

## 三、DESIGN.md 逐项核实

### 颜色（18 色 YAML frontmatter）

全部 18 色与 `artdeco-tokens.scss` + `artdeco-quant-extended.scss` 逐一比对：

| YAML 颜色名 | HEX | 代码对应 | 判定 |
|-------------|-----|---------|------|
| classical-gold | #D4AF37 | `--artdeco-gold-primary: #D4AF37` | 准确 |
| champagne | #F0E68C | `--artdeco-gold-light: #F0E68C` | 准确但见 D-1 |
| dim-gold | #8B7355 | `--artdeco-gold-dim: #8B7355` | 准确 |
| bronze | #CD7F32 | `--artdeco-bronze: #CD7F32` | 准确 |
| obsidian-black | #0A0A0A | `--artdeco-bg-global: #0A0A0A` | 准确 |
| rich-charcoal | #141414 | `--artdeco-bg-base: #141414` | 准确 |
| warm-charcoal | #1A1A1A | `--artdeco-bg-elevated: #1a1a1a` | 准确 |
| deep-navy-black | #111118 | `--artdeco-bg-header: #111118` | 准确 |
| champagne-cream | #F2F0E4 | `--artdeco-fg-primary: #F2F0E4` | 准确 |
| anchor-gray | #A0A0A0 | `--artdeco-fg-muted: #A0A0A0` | 准确 |
| ghost-white | rgba(255,255,255,0.6) | `--artdeco-fg-subtle: rgb(255 255 255 / 60%)` | 准确 |
| a-share-red | #FF5252 | `--artdeco-rise: #FF5252` | 准确 |
| a-share-green | #00E676 | `--artdeco-down: #00E676` | 准确 |
| neutral-gray | #B0B3B8 | `--artdeco-flat: #B0B3B8` | 准确 |
| sky-blue | #4FC3F7 | `--artdeco-info: #4FC3F7` | 准确 |
| deep-red | #D50000 | `--quant-signal-strong-buy: #D50000` | 准确 |
| deep-green | #00C853 | `--quant-signal-strong-sell: #00C853` | 准确 |
| signal-gray | #888888 | `--quant-signal-neutral: #888` | 准确 |

### 量化指标色（DESIGN.md body 第 189-208 行）

全部与 `artdeco-quant-extended.scss` 匹配：MACD Fast/Slow、KDJ-K/D/J、RSI、BOLL Upper/Middle/Lower、DOM Bid/Ask/Spread、Risk Low/Medium/High/Extreme。

### 字体

| 声明 | 代码验证 | 判定 |
|------|---------|------|
| Display: Cinzel + Playfair Display fallback | `--font-display: 'Cinzel', 'Playfair Display', serif` | 准确 |
| Body: Barlow + Inter fallback | `--font-body: 'Barlow', 'Inter', sans-serif` | 准确 |
| Data: JetBrains Mono + Consolas fallback | `--font-mono: 'JetBrains Mono', 'Consolas', monospace` | 准确 |
| Technical: IBM Plex Sans + Helvetica Neue fallback | `--artdeco-font-technical: 'IBM Plex Sans', 'Helvetica Neue'...` | 准确 |

### 圆角系统（6 步）

| YAML | 代码 | 判定 |
|------|------|------|
| none: 0px | `--artdeco-radius-none: 0px` | 准确 |
| sm: 2px | `--artdeco-radius-sm: 2px` | 准确 |
| md: 8px | `--artdeco-radius-md: 8px` | 准确 |
| lg: 12px | `--artdeco-radius-lg: 12px` | 准确 |
| xl: 16px | `--artdeco-radius-xl: 16px` | 准确 |
| full: 9999px | `--artdeco-radius-full: 9999px` | 准确 |

### 间距系统（13 步标准 + 4 步紧凑）

全部与 `artdeco-tokens.scss` 匹配。

### 阴影/光晕系统

6 个 token（none/sm/md/lg/xl + glow subtle/medium/intense/max + profit/loss）全部匹配。

### 动画系统

200ms/400ms/600ms 三档与 `--artdeco-transition-quick/base/slow` 匹配。

### 组件状态机

Button/Input/Card/Chip/Table/Tooltip 各状态 token 在 `artdeco-tokens.scss` 第 444-554 行全部存在。

### 导航侧边栏

260px 展开 + 68px 折叠与 `--artdeco-sidebar-width: 260px` + `--artdeco-sidebar-collapsed-width: 68px` 匹配。

---

## 四、需要修正的问题

### D-1: Champagne 颜色遗漏

**现状:** DESIGN.md YAML 只列了 `champagne: "#F0E68C"`，描述为 hover 高亮。

**代码事实:** `artdeco-tokens.scss` 存在两个相关值：

```scss
--artdeco-gold-light: #F0E68C;    // hover 高亮
--artdeco-champagne: #F7E7CE;     // 柔和背景
```

**建议:** 在 YAML `colors` 中添加 `champagne-soft: "#F7E7CE"`，并在 Neutral 颜色章节补充描述。

### D-2: 断点表不完整

**现状:** DESIGN.md 和 `.impeccable/design.json` 只记录了 desktop-min (1280px) 和 desktop-large (1920px)。

**代码事实:** `artdeco-tokens.scss` 定义了 5 个断点：

```scss
--artdeco-breakpoint-xs: 480px;
--artdeco-breakpoint-sm: 640px;
--artdeco-breakpoint-md: 1024px;
--artdeco-breakpoint-lg: 1280px;
--artdeco-breakpoint-xl: 1536px;
```

**建议:** 在 DESIGN.md Overview 节的 Key Characteristics 中补充完整断点列表，或至少注明"内部断点覆盖 480-1536px 五档，其中 1280px 为最低支持分辨率"。

### D-3: "三种密度模式"缺乏代码证据

**现状:** DESIGN.md Overview 声称"Three density modes: comfortable, compact, micro-density"。

**代码事实:** 代码中只有两套间距系统：

1. 标准 13 步间距 (`--artdeco-spacing-1` 到 `--artdeco-spacing-32`)
2. 紧凑 4 步间距 (`--artdeco-spacing-compact-xs/sm/md/lg`)

搜索 `density`、`density-mode`、`comfortable`、`micro-density` 均未找到密度切换机制或用户可选的密度模式。

**建议:** 改为：

> Two spacing systems: standard scale (13 steps, 4px-128px) for comfortable views and compact scale (4 steps, 4px-16px) for data-dense panels.

或，如果 planned 有密度切换功能，标注为 planned。

### D-4: fintech-design-system.scss 并行系统未被提及

**现状:** DESIGN.md 只描述 ArtDeco 系统。

**代码事实:** `web/frontend/src/styles/fintech-design-system.scss` 是一个完全独立的设计系统（431 次引用），特征：

- 深蓝黑主背景 `#0a0e27`（非 obsidian black `#0A0A0A`）
- 科技蓝强调 `#1890ff`（非 classical gold `#D4AF37`）
- 字体: `Noto Sans SC` + `Roboto Mono`（非 Cinzel + Barlow + JetBrains Mono）
- 独立的圆角、间距、阴影 token 体系
- 主要用于监控面板组件（`MonitoringStatCard`、`MonitoringDataTable`、`MonitoringAlertPanel` 等）

**建议:** 在 DESIGN.md Overview 节末尾添加：

> **Parallel system note:** A `fintech-design-system.scss` exists alongside the ArtDeco system, serving monitoring components. It uses a blue-black + tech-blue palette. Its tokens are independent and should not be mixed with ArtDeco tokens on the same surface.

---

## 五、建议的修正汇总

| 编号 | 文件 | 修正内容 | 优先级 |
|------|------|---------|--------|
| P-1 | PRODUCT.md | 移动端禁令措辞：补充 768px 遗留代码的说明 | 中 |
| D-1 | DESIGN.md | 添加 `champagne-soft: #F7E7CE` 到 YAML 和颜色章节 | 低 |
| D-2 | DESIGN.md | 补充完整断点列表或说明 | 低 |
| D-3 | DESIGN.md | "三种密度模式"改为"双间距系统" | 中 |
| D-4 | DESIGN.md | 添加 fintech 并行系统说明 | 高 |

---

*审计完成于 2026-05-10 | 审计人: Claude Opus 4.7 | 对照源: artdeco-tokens.scss v3.0 + artdeco-quant-extended.scss v1.0 + fintech-design-system.scss v2.0*
