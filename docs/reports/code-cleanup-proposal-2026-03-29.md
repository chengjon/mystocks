# 代码清理提案 — 2026-03-29 历史提案

> 日期: 2026-03-29
> 状态: 历史材料，仅供回溯，不代表当前主线状态。
> 说明: 该提案未在当前主线按原样执行，文中候选清理项需要重新评估后方可实施。
> 范围: `web/frontend/src/`
> 前置条件: 已完成响应式 media query 清理（87 文件，1624 行）

---

## 1. 移除调试日志 `console.log/debug/info`（94 处，20 文件）

### 理由

项目规范要求"保持最小变更"，生产代码中的 `console.log` 是开发调试残留，会：
- 污染浏览器控制台，影响用户排查问题
- 在某些环境下造成性能开销（大量日志序列化）
- 泄露内部实现细节

**保留规则**: `console.error` 和 `console.warn` 不移除（它们用于运行时错误报告，是有意义的）。

### 文件清单

| 文件 | 数量 | 说明 |
|------|------|----------|
| `src/stores/marketData.ts` | 10 | IndexedDB 缓存/网络请求日志 |
| `src/layouts/BaseLayout.vue` | 5 | 命令面板、API 调用日志 |
| `src/stores/examples/pageConfigStoreExample.ts` | 7 | 示例代码日志 |
| `src/views/examples/WebSocketConfigExample.vue` | 7 | WebSocket 示例日志 |
| `src/views/examples/PageConfigExample.vue` | 7 | 页面配置示例日志 |
| `src/views/examples/composables/useTradingDashboard.migrated.ts` | 6 | 迁移示例日志 |
| `src/views/artdeco-pages/ArtDecoMarketQuotes.vue` | 2 | API/WebSocket 调试 |
| `src/views/artdeco-pages/composables/useArtDecoTradingManagement.ts` | 6 | 交易管理操作日志 |
| `src/views/artdeco-pages/ArtDecoTradingCenter.vue` | 3 | 交易中心日志 |
| `src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` | 2 | 技术分析日志 |
| `src/views/artdeco-pages/ArtDecoRiskManagement.vue` | 4 | 风险管理日志 |
| `src/views/artdeco-pages/ArtDecoDataAnalysis.vue` | 2 | 数据分析日志 |
| `src/views/artdeco-pages/ArtDecoStockManagement.vue` | 1 | 股票管理日志 |
| `src/views/monitoring/MonitoringDashboard.vue` | 5 | 监控排序/刷新日志 |
| `src/views/trading-decision/*.vue` | 7 | 交易决策操作日志 |
| `src/stores/baseStore.ts` | 2 | 基础 store 日志 |
| `src/stores/ui.ts` | 3 | UI 状态日志 |
| `src/stores/trading.ts` | 2 | 交易切换日志 |
| `src/views/Stocks.vue` | 1 | 选择变更日志 |
| `src/views/StrategyManagement.vue` | 3 | 策略操作占位日志 |
| 其他（ArtDecoTest, MinimalTest, PyprofilingDemo 等） | ~13 | 测试/Demo 页面日志 |

### 处理方式

- **删除**: 纯调试日志（`console.log('xxx')`、`console.log('Started...')`）
- **替换为空操作**: 带有占位逻辑的（如 `const handleView = (s) => console.log('View:', s)` → `const handleView = (_s: Strategy) => { /* TODO */ }`)
- **保留不处理**: `examples/` 目录下的示例文件（教学用途），以及注释中的 `console.log`（文档示例）

### 预计影响

- 修改约 15 个文件
- 删除约 80 行
- 无功能影响（console.log 不影响逻辑）
- 构建产物体积微减

---

## 2. 静态内联样式 `style="..."` 迁移（69 处，20+ 文件）

### 理由

项目 CSS/SCSS 开发规范明确要求：
> **禁止内联样式**：Vue 组件 `<style>` 块仅允许 `@import` 引用外部 SCSS 文件，不得直接编写 CSS

### 分类

| 类型 | 数量 | 示例 | 处理方式 |
|------|------|------|----------|
| **布局辅助** | ~30 | `style="width: 100%"`, `style="margin-top: 20px"` | 提取为 CSS class |
| **间距/边距** | ~15 | `style="margin-top: 15px"`, `style="padding: 15px"` | 用 ArtDeco token class 替代 |
| **字号/颜色** | ~10 | `style="font-size: var(--artdeco-text-4xl)"` | 已用 token，直接移入 class |
| **硬编码值** | ~10 | `style="border-color: var(--artdeco-gold-primary)"` | 提取为 class |
| **表格/组件宽度** | ~4 | `style="width: 100%"` (el-table) | 提取为 class |

### 重点文件

| 文件 | 内联样式数 | 说明 |
|------|-----------|------|
| `views/demo/pyprofiling/components/Profiling.vue` | ~8 | 全部为 margin-top/width |
| `views/demo/pyprofiling/components/Tech.vue` | ~5 | margin-top/padding |
| `views/demo/pyprofiling/components/Features.vue` | ~4 | margin-top/width |
| `views/demo/OpenStockDemo.vue` | ~4 | margin/width |
| `views/stocks/Watchlist.vue` | 1 | width: 100% |
| `views/TradingDashboard.vue` | 1 | width: 100% |
| `views/TaskManagement.vue` | 1 | borderColor |
| `views/data/Concepts.vue` | 1 | width: 100% |

### 处理方式

对每个 `style="..."` 属性：
1. 在组件的 `<style>` 块或对应 `.scss` 文件中创建命名 class
2. 使用 ArtDeco token 值替代硬编码像素值
3. 替换 template 中的 `style="..."` 为 `class="..."`

### 注意事项

- `el-table style="width: 100%"` 是 Element Plus 常见用法，需保留或用 `:class` + CSS 替代
- 单值 `style="width: 100%"` 可用 Tailwind 等效 class 或自定义 class 替代
- 每个文件单独处理，避免批量替换引入错误

---

## 3. 动态内联样式 `:style="..."` 评估（36 处，20+ 文件）

### 理由

动态 `:style` 绑定用于运行时计算的样式值（如进度条宽度、条件颜色），部分合理，部分可优化。

### 分类

| 类型 | 数量 | 合理性 | 处理建议 |
|------|------|--------|----------|
| **进度条/仪表盘宽度** | ~15 | ✅ 合理 | 保留（需要动态百分比） |
| **条件颜色** | ~8 | ⚠️ 可优化 | 改用 `:class` + CSS 条件类 |
| **图表容器尺寸** | ~5 | ✅ 合理 | 保留（ECharts 需要动态尺寸） |
| **ArtDeco token 内联** | ~3 | ❌ 不合理 | 移入 CSS class（token 是静态的） |
| **其他** | ~5 | 逐个评估 | — |

### 具体可优化项

```vue
<!-- ❌ 当前: 静态 ArtDeco token 用了 :style -->
<div :style="{ padding: 'var(--artdeco-spacing-6)' }">

<!-- ✅ 应改为: -->
<div class="content-section-padded">
<!-- CSS: .content-section-padded { padding: var(--artdeco-spacing-6); } -->
```

涉及文件：
- `views/stock-analysis/StockBacktestTab.vue`
- `views/stock-analysis/StockRealtimeTab.vue`
- `views/stock-analysis/StockStatusTab.vue`

### 不建议处理的项

- 图表组件的 `:style="{ width, height }"` — ECharts/动态图表需要运行时尺寸
- 进度条 `:style="{ width: xxx + '%' }"` — 数据驱动的动态宽度
- 条件复杂的颜色计算 — 重构成本高于收益

---

## 4. 执行优先级建议

| 优先级 | 任务 | 风险 | 工作量 |
|--------|------|------|--------|
| **P0** | 移除 console.log | 极低 | 小（批量替换） |
| **P1** | 修复静态 ArtDeco token 的 `:style` | 低 | 小（3 文件） |
| **P2** | 迁移静态内联 `style="..."` | 低 | 中（20+ 文件） |
| **P3** | 评估动态 `:style` 条件颜色 | 中 | 中（需逐个分析） |

---

## 5. 不建议清理的项

| 项目 | 原因 |
|------|------|
| `@media (prefers-color-scheme)` | 无障碍支持，非响应式 |
| `@media print` | 打印样式，合理 |
| `console.error` / `console.warn` | 运行时错误报告，有意义 |
| `examples/` 目录下的 console.log | 教学用途 |
| 图表组件的 `:style` 动态尺寸 | ECharts API 需要 |

---

**请审核后告知执行哪些部分。**
