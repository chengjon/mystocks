# ArtDeco Start Here

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文件是 MyStocks 前端 ArtDeco / ArtDeco Fintech 体系的单页入口文档。

如果你是第一次接手这个体系，先看这份，再决定是否进入更细的治理文档。

## 0. 本文档的职责

`ARTDECO_START_HERE.md` 只负责 3 件事：

1. 用最短路径解释“当前 ArtDeco 到底是什么”。
2. 告诉你“先看哪几份文档、先跑哪些命令”。
3. 把你路由到正确的治理文档和源码目录。

它不是完整目录。

如果你需要：

- **完整目录** -> 看 `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- **统一规格** -> 看 `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- **设计契约** -> 看 `DESIGN.md`
- **详细组件目录** -> 看 `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- **页面治理结论** -> 看 `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
- **详细样式真值和兼容边界** -> 看 `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`

## 1. 先记住这 9 句话

1. 当前项目的活跃风格是 `ArtDeco Fintech`，不是原始 ArtDeco 的机械复刻。
2. 新代码只认 `artdeco-*` 主链，不认历史 `theme-*` / `fintech-*` 为真值。
3. 字体真值是 `Cinzel + Barlow + JetBrains Mono`。
4. 间距真值是 `13` 个编号级别：`1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32`。
5. A 股语义强制执行“红涨绿跌”。
6. `DESIGN.md` 是当前动效、密度、glow 和交易面板主操作层级的设计契约。
7. 页面不能只做黑金配色，必须有明确的舞台层和内容节奏。
8. 涉及 Layout、路由或菜单结构时，必须跑 `bash scripts/run_e2e_pm2.sh`。
9. 菜单结构、UI/UX 风格、核心架构变更，先回到 `architecture/STANDARDS.md` 走审批门禁，再实施。

## 2. 当前设计身份

当前项目应被理解为：

`Original ArtDeco` + `A 股金融语义` + `高密度量化工作台` = `ArtDeco Fintech`

核心气质：

- 黑金高对比
- 几何优先于圆润
- 标题 uppercase + tracking
- glow 优先于普通阴影
- `JetBrains Mono` 承载数值、状态与元信息
- A 股红涨绿跌

## 3. 认哪套真值

### 3.1 文档真值链

当前活跃文档链路：

1. `ARTDECO_START_HERE.md`
2. `ARTDECO_MASTER_INDEX.md`
3. `ARTDECO_FINTECH_UNIFIED_SPEC.md`
4. `DESIGN.md`
5. `ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
6. `ARTDECO_COMPONENT_GUIDE.md`
7. `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
8. `docs/api/ArtDeco_System_Architecture_Summary.md`
9. `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

### 3.2 样式真值层

新开发默认只认这 5 个文件：

- `web/frontend/src/styles/artdeco-tokens.scss`
- `web/frontend/src/styles/artdeco-grid.scss`
- `web/frontend/src/styles/artdeco-global.scss`
- `web/frontend/src/styles/artdeco-financial.scss`
- `web/frontend/src/styles/artdeco-quant-extended.scss`

职责分工：

- `artdeco-tokens.scss`
  颜色、字体、间距、圆角、过渡、glow 的唯一真值
- `artdeco-grid.scss`
  Grid mixin、语义化布局类、断点系统
- `artdeco-global.scss`
  全局背景、排版、reset、滚动条、基础交互
- `artdeco-financial.scss`
  金融语义色、风险/指标/监控语义
- `artdeco-quant-extended.scss`
  高密度交易工作台扩展、dense spacing、数据字体

### 3.3 兼容层

这些文件仍可能在运行链路里出现，但不再是新真值：

- `web/frontend/src/styles/fintech-design-system.scss`
- `web/frontend/src/styles/visual-optimization.scss`
- `web/frontend/src/styles/pro-fintech-optimization.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.scss`
- `web/frontend/src/styles/element-plus-override.scss`
- `web/frontend/src/styles/artdeco-main.css`
- `web/frontend/src/styles/artdeco-variables.css`
- `web/frontend/src/styles/theme-tokens.scss`
- `web/frontend/src/styles/design-tokens.scss`

规则：

- 可以修兼容层，但只能做最小必要修复。
- 不能因为它们仍被加载，就把它们当新的设计系统事实源。
- 如果兼容层里某个 token 真有价值，先提升到 `artdeco-*` 真值层。
- `artdeco-main.css` 当前只应被理解为兼容入口，并通过 `artdeco-colors.css` / `artdeco-variables.css` 链接入兼容 token。

## 4. 架构怎么理解

### 4.1 视觉架构

建议按这 4 层理解：

1. **样式基础设施层**
   `artdeco-tokens / grid / global / financial / quant-extended`
2. **布局壳层**
   例如 `ArtDecoLayoutEnhanced.vue`
3. **可复用资产层**
   `src/components/artdeco/**`
4. **页面工作台层**
   `views/artdeco-pages/**`

### 4.2 页面骨架

当前已验证有效的页面骨架是：

1. `hero`
2. `meta rail`
3. `stats strip`
4. `tabs shell`
5. `content shell`
6. 内部再挂 domain 组件或 workbench block

不要反过来先堆业务组件，再希望页面“看起来像 ArtDeco”。

### 4.3 运行时承载模式

当前仓库不是单一 `Container-Tab` 模型，而是三种模式并存：

- **模板化工作台**
  例如 `ArtDecoPageTemplate.vue`、`ArtDecoRiskManagement.vue`
- **直接 Tab 容器**
  例如 `ArtDecoMarketData.vue`
- **功能树驱动总控容器**
  例如 `ArtDecoTradingCenter.vue`

另有一条共享运行时桥接模式：

- **Layout 级共享摘要**
  例如 `useHeaderSummary.ts` -> `ArtDecoLayoutEnhanced.vue`

### 4.4 组件边界

当前要区分 3 类对象：

- `src/components/artdeco/**`
  可持续沉淀的 reusable assets
- `views/artdeco-pages/components/`
  页面系统内部共享片段
- `views/artdeco-pages/*-tabs/`
  域内工作台块

## 5. 当前开发必须遵守的规则

### 5.1 视觉规则

- 禁止硬编码颜色、间距、圆角、阴影、过渡时长
- 禁止在新页面继续引入 emoji 作为主图标语汇
- 金色是主品牌强调，不是随机点缀色
- 数值与代码优先使用 `JetBrains Mono`
- A 股涨跌必须遵守 `红涨绿跌`

### 5.2 页面规则

- 新页面优先复用现有工作台壳层
- 页面至少要明确：标题区、元信息区、内容层
- 需要 tabs 时，优先延续 `tabs shell -> content shell` 的结构
- TRACE_ID / request meta 位要有落点，不要完全丢掉可观测性

### 5.3 工程规则

- 先读 `architecture/STANDARDS.md`
- 涉及菜单结构、UI/UX 风格、核心架构时，先走审批门禁
- 不要把旧兼容链升级为新真值
- 当前项目是桌面端工作台，不做移动端 / 平板适配

## 6. 你要改什么，就去哪里改

| 目标 | 应改文件 |
|------|----------|
| 品牌色、字体、间距、圆角、过渡 | `artdeco-tokens.scss` |
| Grid 模式、断点、语义布局类 | `artdeco-grid.scss` |
| 全局 reset、背景、排版、滚动条 | `artdeco-global.scss` |
| 指标/风险/监控/金融语义 | `artdeco-financial.scss` |
| 高密度交易工作台扩展 | `artdeco-quant-extended.scss` |
| Element Plus 对齐 | `element-plus-override.scss` |
| 可复用资产 | `src/components/artdeco/**` |
| 页面系统共享片段 | `views/artdeco-pages/components/` |
| 域内工作台块 | `views/artdeco-pages/*-tabs/` |
| 页面舞台层 | `views/artdeco-pages/*.vue` |
| 布局壳层 | `layouts/*.vue` |

## 7. 新页面 / 新组件的开发顺序

### 7.1 新页面

建议顺序：

1. 确定它属于哪个业务域
2. 判断它更适合模板化工作台、直接 Tab 容器，还是总控容器
3. 先复用已有页面骨架
4. 再放 stats / tabs / content
5. 最后才做领域细节

### 7.2 新组件

建议顺序：

1. 先判断它是不是 reusable asset
2. 如果是 reusable，再判断属于 `base / core / business / charts / trading / advanced / specialized`
3. 如果不是 reusable，再判断应放 `views/artdeco-pages/components/` 还是 `views/artdeco-pages/*-tabs/`
4. 样式优先用 token，不要自带第二套视觉语言

## 8. 验证怎么做

### 8.1 基础门禁

当前变更范围检查：

```bash
cd web/frontend
npm run lint:artdeco:changed
```

单文件检查：

```bash
cd web/frontend
node scripts/check-artdeco-tokens.js --target-file src/path/to/file.vue
```

### 8.2 Layout / 路由变更

涉及 Layout、路由、菜单结构时，必须跑：

```bash
bash scripts/run_e2e_pm2.sh
```

报告时必须写实际执行结果，不要复用固定通过文案。

## 9. 当前文档地图

### 9.1 先读

- [ARTDECO_MASTER_INDEX](./ARTDECO_MASTER_INDEX.md)
- [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
- [DESIGN.md](../../../DESIGN.md)
- [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
- [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md)

### 9.2 再读

- [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT](./ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md)
- [ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md)
- [ARTDECO_PAGE_TEMPLATE_GUIDE](./ARTDECO_PAGE_TEMPLATE_GUIDE.md)
- [ArtDeco System Architecture Summary](../../api/ArtDeco_System_Architecture_Summary.md)
- [ARTDECO_COMPONENTS_CATALOG](../../../web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
- [ARTDECO_V3_COMPLETE_SUMMARY](../../reports/ARTDECO_V3_COMPLETE_SUMMARY.md)

## 10. 一句话结论

现在的 MyStocks ArtDeco 已经不是“黑金主题集合”，而是一套由统一规格、设计令牌、组件分层和页面工作台共同维持的 `ArtDeco Fintech` 前端体系。
