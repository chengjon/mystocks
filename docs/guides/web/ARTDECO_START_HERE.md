# ArtDeco Start Here

本文件是 MyStocks 前端 ArtDeco / ArtDeco Fintech 的单页入口文档。

如果你是第一次接手这个体系，先看这份，再决定要不要继续读更细的治理文档。

## 0. 本文档的职责

`ARTDECO_START_HERE.md` 只负责 3 件事：

1. 用最短路径解释“当前 ArtDeco 到底是什么”
2. 告诉你“先看哪几份文档、先跑哪些命令”
3. 按任务把你路由到正确文档

它不是完整目录，也不追求收录所有文档。

如果你需要：

- **完整目录** -> 看 `ARTDECO_MASTER_INDEX.md`
- **详细组件目录** -> 看 `ARTDECO_COMPONENTS_CATALOG.md`
- **详细页面治理结论** -> 看 `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
- **详细样式真值和兼容层边界** -> 看 `ARTDECO_SCSS_GOVERNANCE_BASELINE.md`

## 1. 先记住这 7 句话

1. 当前项目的活跃风格不是“原始 ArtDeco 复刻”，而是 `ArtDeco Fintech v1`。
2. 新代码只认 `artdeco-*` 主链，不认历史 `theme-*` / `fintech-*` 为真值。
3. 视觉属性禁止硬编码，优先走 `artdeco-tokens.scss`。
4. 页面不能只做黑金配色，必须有 `hero / meta / stats / tabs / content` 这类舞台层。
5. A 股语义强制执行“红涨绿跌”。
6. 涉及 Layout 或路由变更，必须跑 `bash scripts/run_e2e_pm2.sh`。
7. 任何菜单结构、UI/UX 风格、核心架构变更，都先遵守 `architecture/STANDARDS.md` 的 `Proposal-First Rule`。

## 2. 当前设计身份

当前项目应被理解为：

`Original ArtDeco` + `A 股金融语义` + `高密度量化终端` = `ArtDeco Fintech v1`

核心气质：

- 黑金高对比
- 几何优先于圆润
- 标题 uppercase + tracking
- glow 优先于普通阴影
- JetBrains Mono 承载数值和数据
- A 股红涨绿跌

原始参考文件：

- `/opt/mydoc/design/ArtDeco/ArtDeco.md`

## 3. 认哪套真值

### 3.1 主真值层

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
  高密度交易终端扩展、dense spacing、数据字体

### 3.2 兼容层

这些文件仍在运行，但不再是新真值：

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

## 4. 架构怎么理解

### 4.1 视觉架构

建议按这 3 层理解：

1. **样式基础设施层**
   `artdeco-tokens / grid / global / financial / quant-extended`
2. **布局壳层**
   例如 `ArtDecoLayoutEnhanced.vue`
3. **页面舞台层**
   例如 `ArtDecoMarketData.vue`、`ArtDecoTradingCenter.vue`

### 4.2 页面骨架

当前已验证有效的页面骨架是：

1. `hero`
2. `meta rail`
3. `stats strip`
4. `tabs shell`
5. `content shell`
6. 内部再放 domain 组件

不要反过来先堆业务组件，再希望页面“看起来像 ArtDeco”。

### 4.3 组件架构

总体采用 `Container-Tab` 混合架构：

- 父容器：`web/frontend/src/views/artdeco-pages/`
- 领域组件：`web/frontend/src/views/artdeco-pages/components/`
- 基础资产：`web/frontend/src/components/artdeco/`

组件目录总览见：

- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

## 5. 当前开发必须遵守的规则

### 5.1 视觉规则

- 禁止硬编码颜色、间距、圆角、阴影、过渡时长
- 禁止在新页面继续引入 emoji 作为主图标语汇
- 金色是主品牌强调，不是随机点缀色
- 数值与代码优先使用 `JetBrains Mono`
- A 股涨跌必须遵守 `红涨绿跌`

### 5.2 页面规则

- 新页面优先使用 `ArtDecoHeader` 或已有页面骨架模式
- 页面至少要明确：标题区、元信息区、tabs 层、内容层
- TRACE_ID / request meta 位要有落点，不要完全丢掉可观测性

### 5.3 工程规则

- 先读 `architecture/STANDARDS.md`
- 涉及菜单结构、UI/UX 风格、核心架构时，先走审批门禁
- 不要把旧兼容链升级为新真值

## 6. 你要改什么，就去哪里改

| 目标 | 应改文件 |
|------|----------|
| 品牌色、字体、间距、圆角、过渡 | `artdeco-tokens.scss` |
| Grid 模式、断点、语义布局类 | `artdeco-grid.scss` |
| 全局 reset、背景、排版、滚动条 | `artdeco-global.scss` |
| 指标/风险/监控/金融语义 | `artdeco-financial.scss` |
| 高密度交易终端扩展 | `artdeco-quant-extended.scss` |
| Element Plus 对齐 | `element-plus-override.scss` |
| 页面舞台层 | 对应 `views/artdeco-pages/*.vue` |
| 布局壳层 | `layouts/*.vue` |

## 7. 新页面 / 新组件的开发顺序

### 7.1 新页面

建议顺序：

1. 确定它属于哪个业务域
2. 先复用已有页面骨架
3. 再接入 `ArtDecoHeader`
4. 再放 stats / tabs / content
5. 最后才做领域组件细节

### 7.2 新组件

建议顺序：

1. 优先放在 `src/components/artdeco/`
2. 先判断属于 `base / core / business / charts / trading / advanced`
3. 样式优先用 token，不要自带第二套视觉语言

## 8. 验证怎么做

### 8.1 基础门禁

单文件样式检查：

```bash
cd web/frontend
node scripts/check-artdeco-tokens.js --target-file src/path/to/file.vue
```

当前变更范围检查：

```bash
cd web/frontend
npm run lint:artdeco:changed
```

### 8.2 Layout / 路由变更

涉及 Layout、路由、菜单结构时，必须跑：

```bash
bash scripts/run_e2e_pm2.sh
```

当前这条链已经验证通过：

- 项目：`chromium`
- 套件：`tests/navigation-consistency.spec.ts`
- 结果：`14 passed`

## 9. 当前已完成到什么程度

### 9.1 已完成

- P0：字体真值、glow 语义、主导入链路统一
- P1：兼容层边界显式化、活跃旧字体清理
- P2 第一轮页面治理：
  - `ArtDecoMarketData.vue`
  - `ArtDecoSystemSettings.vue`
  - `ArtDecoTradingCenter.vue`
  - `ArtDecoTechnicalAnalysis.vue`
  - `ArtDecoSettings.vue`
  - `ArtDecoDataAnalysis.vue`
  - `ArtDecoLayoutEnhanced.vue`
  - `ArtDecoMarketOverview.vue`

### 9.2 进行中

- P3 第二轮页面治理：
  - `ArtDecoStockManagement.vue`
  - `ArtDecoMarketQuotes.vue`
  - `ArtDecoTradingManagement.vue`

### 9.3 仍待继续

- 剩余未专项治理页面的一致性审查
- 页面壳层进一步模板化
- 历史兼容层长期归档/下线顺序

## 10. 文档地图

### 10.1 先读

- [ARTDECO_SCSS_GOVERNANCE_BASELINE](./ARTDECO_SCSS_GOVERNANCE_BASELINE.md)
- [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
- [ARTDECO_FINTECH_IMPLEMENTATION_AUDIT](./ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md)
- [ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md)

### 10.2 继续读

- [ARTDECO_MASTER_INDEX](./ARTDECO_MASTER_INDEX.md)
- [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md)
- [ARTDECO_GRID_QUICK_REFERENCE](./ARTDECO_GRID_QUICK_REFERENCE.md)
- [ARTDECO_PAGE_TEMPLATE_GUIDE](./ARTDECO_PAGE_TEMPLATE_GUIDE.md)
- [ARTDECO_UI_UX_FUNCTIONALITY_GUIDE](./ARTDECO_UI_UX_FUNCTIONALITY_GUIDE.md)

### 10.3 架构与组件

- [ArtDeco System Architecture Summary](/opt/claude/mystocks_spec/docs/api/ArtDeco_System_Architecture_Summary.md)
- [ARTDECO_COMPONENTS_CATALOG](/opt/claude/mystocks_spec/web/frontend/ARTDECO_COMPONENTS_CATALOG.md)
- [ARTDECO_V3_COMPLETE_SUMMARY](/opt/claude/mystocks_spec/docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md)

### 10.4 历史高价值文档

这些文档不是当前唯一事实源，但仍值得保留：

- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

使用方式：

- 看它们是为了理解历史架构、组件存量和 V3.0 升级过程
- 真正决定“现在怎么写”的，仍然是本目录下 `web/` 入口体系

## 11. 常见任务入口

如果你不是要“通读体系”，而是要“马上开始一个任务”，直接按下面找：

### 11.1 我要改页面骨架 / 页面布局

先看：

- `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
- `docs/guides/web/ARTDECO_PAGE_TEMPLATE_GUIDE.md`
- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`

再看源码：

- 目标页面对应的 `views/artdeco-pages/*.vue`
- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`

### 11.2 我要新增组件 / 判断组件该放哪里

先看：

- `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`

再做判断：

- 原子 UI -> `base`
- 页面骨架 / 导航 / 反馈 -> `core`
- 通用业务交互 -> `business`
- 图表 -> `charts`
- 交易域 -> `trading`
- 高阶分析 -> `advanced`
- 强专题 -> `specialized`
- 单页面专属 -> 页面域，不要提升

### 11.3 我要修样式 / token / 布局令牌

先看：

- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`

再改源码：

- `artdeco-tokens.scss`
- `artdeco-grid.scss`
- `artdeco-global.scss`
- `artdeco-financial.scss`
- `artdeco-quant-extended.scss`

### 11.4 我要修兼容层 / 历史层

先看：

- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
- `docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`

原则：

- 兼容层可以修，但只做最小必要修复
- 不要把兼容层重新升级为真值

### 11.5 我要判断当前进展到哪一步

先看：

- `docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`
- `docs/guides/web/ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`

它们分别回答：

- 基础设施层和治理层做到哪里了
- 页面级构图治理做到哪里了

### 11.6 我要做验证 / 自测

先跑：

```bash
cd web/frontend
npm run lint:artdeco:changed
```

单文件检查：

```bash
cd web/frontend
node scripts/check-artdeco-tokens.js --target-file src/path/to/file.vue
```

如果改了 Layout / 路由 / 菜单：

```bash
bash scripts/run_e2e_pm2.sh
```

### 11.7 我要理解历史背景 / 为什么会有今天这套体系

先看：

- `docs/api/ArtDeco_System_Architecture_Summary.md`
- `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- `docs/reports/ARTDECO_V3_COMPLETE_SUMMARY.md`

注意：

- 这些是高价值历史和结构文档
- 不是当前唯一事实源

## 12. 推荐阅读顺序

如果你是后续 AI 或开发者，建议按这个顺序接手：

1. 本文档
2. `architecture/STANDARDS.md`
3. `ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
4. `artdeco-tokens.scss`
5. `ARTDECO_FINTECH_UNIFIED_SPEC.md`
6. `ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`
7. `ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md`
8. 需要改的具体页面/组件源码

## 13. 一句话结论

现在的 MyStocks ArtDeco 已经不是“黑金主题集合”，而是一套已成形的 `ArtDeco Fintech v1` 前端体系。

后续开发的关键，不再是重新发明风格，而是：

- 继续坚持主 token 链
- 继续复用统一页面骨架
- 不让历史兼容层重新变成事实源
