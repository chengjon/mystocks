# ArtDeco SCSS Governance Baseline

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文件是 MyStocks 前端 ArtDeco SCSS 体系的单一治理入口，面向未来 AI 和开发者回答四个问题：

1. 哪些 SCSS 文件是当前有效的基础设施层。
2. 新页面/新组件应该依赖哪套令牌和布局能力。
3. 历史兼容层与当前真值如何区分。
4. 开发和评审时该如何快速自检。

## 1. 结论先行

ArtDeco SCSS 在本项目中不是“页面皮肤”，而是前端样式基础设施。它承担：

- 设计令牌定义：颜色、字体、间距、圆角、过渡、层级。
- 金融语义表达：A 股红涨绿跌、技术指标、风险等级、数据质量、GPU 状态。
- 全局视觉治理：reset、背景、排版、滚动条、全局工具类。
- 响应式布局抽象：统一 Grid mixin、语义化区块类、断点系统。
- 第三方主题适配：Element Plus 与历史终端风格兼容层。

## 2. 单一事实来源

新开发默认只认以下五个文件为 ArtDeco 样式真值：

| 层级 | 文件 | 责任 |
|------|------|------|
| P0 | `web/frontend/src/styles/artdeco-tokens.scss` | 核心设计令牌，颜色/字体/间距/圆角/过渡的唯一真值 |
| P0 | `web/frontend/src/styles/artdeco-grid.scss` | Grid mixin、语义化 Grid 类、断点系统 |
| P0 | `web/frontend/src/styles/artdeco-global.scss` | 全局入口，导入 ArtDeco 基础层并应用 reset/排版/背景 |
| P1 | `web/frontend/src/styles/artdeco-financial.scss` | 金融量化专用语义令牌和 mixin |
| P1 | `web/frontend/src/styles/artdeco-quant-extended.scss` | 量化交易扩展层，提供 dense spacing、数据字体、量化信号和终端化布局令牌 |

这些文件在运行时由 [main.js](/opt/claude/mystocks_spec/web/frontend/src/main.js) 加载，构成 ArtDeco 样式基础设施的当前实现。

补充说明：

- 截至 `2026-03-25`，上述主链在字体语义层已统一到 `Cinzel + Barlow + JetBrains Mono`。
- `artdeco-tokens.scss` 现在同时承担主字体、主 glow 语义和 ArtDeco 基础令牌真值。
- `artdeco-global.scss` 不再重复导入旧字体链路，而是依赖 `artdeco-tokens.scss` 提供字体真值。

## 3. 兼容层与历史层

### 3.1 运行时分层矩阵

“仍在运行链路中” 不等于 “仍是真值层”。当前建议按下表判断：

| 层级 | 文件/入口 | 运行状态 | 新代码策略 |
|------|-----------|----------|------------|
| P0 真值层 | `artdeco-tokens.scss` / `artdeco-global.scss` / `artdeco-grid.scss` / `artdeco-financial.scss` / `artdeco-quant-extended.scss` | 主运行链路有效 | 新 ArtDeco 页面与组件必须优先依赖 |
| P1 活跃兼容层 | `fintech-design-system.scss` / `visual-optimization.scss` / `pro-fintech-optimization.scss` / `bloomberg-terminal-override.scss` / `element-plus-override.scss` | 仍由 `main.js` 加载 | 只做兼容修复，不得升级为新真值 |
| P1 活跃兼容入口 | `artdeco-main.css` / `artdeco-variables.css` | 仍服务于 `main-enhanced.ts` 与旧布局链路 | 保持兼容，不作为新增 ArtDeco 依赖 |
| P2 历史通用主题层 | `theme-tokens.scss` / `design-tokens.scss` | 仍可能被旧页面或旧样式链间接使用 | 新 ArtDeco 页面禁止新增依赖 |

执行原则：

- 兼容层允许修，但只能做最小必要修复。
- 如果兼容层里某个 token 需要被新 ArtDeco 页面复用，先把它提升到 `artdeco-*` 真值层，再视需要向下做兼容映射。
- 不要因为某个文件仍被 `main.js` 导入，就把它视为新的设计系统事实源。

### 3.2 文件级兼容说明

下列文件仍然活跃，但对新 ArtDeco 页面来说属于兼容层，不应作为新增样式的主依赖：

| 文件 | 角色 | 新代码策略 |
|------|------|------------|
| `web/frontend/src/styles/element-plus-override.scss` | Element Plus 变量映射与覆盖 | 只在组件库适配或全局主题修复时修改 |
| `web/frontend/src/styles/fintech-design-system.scss` | 历史 Fintech 终端样式层 | 不作为新 ArtDeco 页面首选令牌源 |
| `web/frontend/src/styles/visual-optimization.scss` | 历史视觉修补层（按钮/卡片/间距） | 只在旧页面兼容修复时修改 |
| `web/frontend/src/styles/pro-fintech-optimization.scss` | 历史专业终端强化层 | 只在旧终端兼容修复时修改 |
| `web/frontend/src/styles/bloomberg-terminal-override.scss` | 历史终端风格强化覆盖 | 仅在兼容旧页面时修改 |
| `web/frontend/src/styles/theme-tokens.scss` | 旧主题令牌体系 | 新 ArtDeco 页面禁止新增依赖 |
| `web/frontend/src/styles/design-tokens.scss` | 更早期的通用令牌体系 | 新 ArtDeco 页面禁止新增依赖 |
| `web/frontend/src/styles/artdeco-main.css` | 旧 ArtDeco 兼容入口 | 仅供 `main-enhanced.ts` 等旧链路使用 |
| `web/frontend/src/styles/artdeco-variables.css` | `artdeco-main.css` 的兼容变量层 | 已对齐主字体真值，但仍视为兼容层 |

判断规则：

- 如果是 `views/artdeco-pages/**`、`components/artdeco/**`、ArtDeco 路由容器或 Tab 页面，新样式必须优先使用 `artdeco-*` 体系。
- 如果是修旧页面且页面已深度绑定 `theme-*` 或 `fintech-*` 变量，可维持原体系，但不要把旧体系再扩散到新代码。
- 如果文件通过 `main.js` 的 `fintech/visual/pro-fintech/bloomberg` 多层样式链路生效，允许做最小兼容修复，但不得把这些层升级为新的 ArtDeco 真值。

## 4. 新代码必须遵守的规则

### 4.1 令牌规则

- 禁止硬编码颜色、间距、圆角、阴影、过渡时长。
- 新代码优先使用规范名，而不是兼容别名。
- 允许继续读取旧别名，但不要在新文档、新组件、新样式中继续推广。

推荐优先级如下：

| 类别 | 规范写法 | 兼容别名 | 规则 |
|------|----------|----------|------|
| 主品牌金色 | `--artdeco-gold-primary` | `--artdeco-accent-gold` | 新代码使用规范写法 |
| 主文本 | `--artdeco-fg-primary` | 无 | 直接使用 |
| 次文本 | `--artdeco-fg-muted` | `--artdeco-silver-dim` | 新代码使用规范写法 |
| 卡片背景 | `--artdeco-bg-card` | 无 | 直接使用 |
| 间距 | `--artdeco-spacing-*` | `--artdeco-spacing-sm/md/lg/xl` | 优先使用数值级令牌 |
| 上涨/盈利 | `--artdeco-rise` / `--artdeco-profit` | 无 | 遵守 A 股红涨绿跌 |
| 下跌/亏损 | `--artdeco-down` / `--artdeco-loss` | 无 | 遵守 A 股红涨绿跌 |

### 4.2 导入规则

新 SCSS 代码默认使用 Sass Module 语法：

```scss
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-grid.scss' as *;
```

说明：

- 现有文件中大量 `@import` 仍然存在，属于历史兼容状态。
- 新增或重写文件时，优先迁移到 `@use`。
- 仅使用 CSS 变量时可只引入 `artdeco-tokens.scss`。
- 需要 Grid mixin 时再引入 `artdeco-grid.scss`。

### 4.3 布局规则

优先级从高到低：

1. 先复用语义化 Grid 类：`.charts-section`、`.summary-section`、`.heatmap-section`、`.flow-section`、`.pool-section`、`.nav-section`
2. 再使用基础工具类：`.artdeco-grid-2`、`.artdeco-grid-3`、`.artdeco-grid-4`、`.artdeco-grid-auto`、`.artdeco-grid-cards`
3. 最后才写局部自定义 Grid，并复用现有 mixin：`artdeco-grid-container`、`artdeco-grid-2-cols`、`artdeco-grid-3-cols`、`artdeco-grid-4-cols`、`artdeco-grid-auto`、`artdeco-grid-cards`

禁止再写不存在的伪 API，例如 `@include artdeco-grid(4)`。

### 4.4 金融语义规则

涉及交易、行情、回测、风控、监控时，不要自行定义颜色语义：

- 技术指标颜色走 `artdeco-financial.scss`
- 风险等级颜色走 `artdeco-financial.scss`
- 数据质量/新鲜度颜色走 `artdeco-financial.scss`
- 高密度交易布局、数据字体、dense spacing 走 `artdeco-quant-extended.scss`
- A 股涨跌永远遵守“红涨绿跌”

### 4.5 全局修改边界

按改动意图选择文件：

| 需求 | 应修改文件 |
|------|-----------|
| 调整品牌色、字体、间距、圆角、过渡 | `artdeco-tokens.scss` |
| 调整 Grid 模式、断点、语义布局类 | `artdeco-grid.scss` |
| 调整全局 reset、背景、排版、滚动条 | `artdeco-global.scss` |
| 调整技术指标/风险/回测/监控视觉语义 | `artdeco-financial.scss` |
| 调整高密度交易终端布局、数据字体、dense gap | `artdeco-quant-extended.scss` |
| 调整 Element Plus 与 ArtDeco 对齐 | `element-plus-override.scss` |

## 5. 推荐开发模板

### 5.1 纯令牌组件

```vue
<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.panel {
  background: var(--artdeco-bg-card);
  color: var(--artdeco-fg-primary);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
}
</style>
```

### 5.2 使用 Grid mixin 的组件

```vue
<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-grid.scss' as *;

.stats-grid {
  display: grid;
  @include artdeco-grid-4-cols;
  gap: var(--artdeco-spacing-6);
}
</style>
```

## 6. 评审与自检清单

提交前至少确认：

- 是否新增了硬编码颜色、间距、圆角、阴影或断点。
- 是否错误地把新 ArtDeco 页面建立在 `theme-*` 或 `fintech-*` 令牌上。
- 是否使用了规范 token 名，而不是继续扩散兼容别名。
- 是否优先复用了现有语义化 Grid 类或 Grid mixin。
- 是否遵守 A 股红涨绿跌。
- 是否把第三方组件修补写进了正确的兼容层文件，而不是散落到页面里。

## 7. 后续 AI/开发者的最短阅读路径

如果你是第一次接手 ArtDeco 样式，请按这个顺序读取：

1. 本文档
2. [artdeco-tokens.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-tokens.scss)
3. [artdeco-grid.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-grid.scss)
4. [artdeco-global.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-global.scss)
5. [artdeco-financial.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-financial.scss)
6. [artdeco-quant-extended.scss](/opt/claude/mystocks_spec/web/frontend/src/styles/artdeco-quant-extended.scss)
7. [ARTDECO_COMPONENT_GUIDE.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_COMPONENT_GUIDE.md)
8. [ARTDECO_GRID_QUICK_REFERENCE.md](/opt/claude/mystocks_spec/docs/guides/web/ARTDECO_GRID_QUICK_REFERENCE.md)

## 8. 当前已知限制

- 仓库中仍有较多历史文档使用旧字体、旧 token 名和旧 `@import` 示例。
- 兼容别名如 `--artdeco-accent-gold` 仍大量存在于现有代码，短期内不能机械删除。
- `main.js` 仍同时加载 ArtDeco、Fintech、Visual Optimization、Bloomberg 等多层样式；这些兼容层可以继续运行，但不应被误判为新的 ArtDeco 真值。
- `main-enhanced.ts` 仍通过 `artdeco-main.css` 链路保留旧兼容入口；`ArtDecoLayoutEnhanced.vue` 已切回主 token 链。

---

**维护原则**:

- 若 SCSS 真值发生变化，先更新本文件，再更新索引和示例文档。
- 若示例文档与本文件冲突，以本文件和源码为准。
