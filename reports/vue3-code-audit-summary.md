# Vue3 代码审核总结报告

> 审核周期：2025-02-13 ~ 2025-07-15
> 项目：MyStocks Web Frontend (Vue 3.4+ / TypeScript / Element Plus)

---

## 一、审核成果总览

| 审核项 | 修复前 | 修复后 | 状态 |
|--------|--------|--------|------|
| v-for 缺少 :key | 222 处 | 0 | ✅ |
| ECharts 全量导入 | 多处 `import * as echarts` | 按需导入 | ✅ |
| ant-design-vue 残留 | 多处引用 | 0（全部迁移至 Element Plus） | ✅ |
| `as any` 滥用 | 178 处 | 20 处（全在测试文件，合理用法） | ✅ |
| 内存泄漏风险 | 29+ 处 timer 无清理 | 全部添加 onUnmounted 清理 | ✅ |
| 超 1000 行组件 | 25 个 | 1 个（StockAnalysisDemo.vue 1002 行，demo 静态内容） | ✅ |
| Stylelint 错误 | 4639 个 | 0 | ✅ |

---

## 二、架构优化详情

### 2.1 CSS 提取（Style Extraction）

将 47 个大组件的内联 CSS 提取为独立 SCSS 文件，存放于各组件目录下的 `styles/` 子目录。

**提取模式：**
```vue
<!-- 修改前 -->
<style lang="scss" scoped>
  /* 500~1100 行 CSS */
</style>

<!-- 修改后 -->
<style lang="scss" scoped>
@import './styles/ComponentName.scss';
</style>
```

**涉及目录：**
- `src/components/artdeco/advanced/styles/` — 6 个 ArtDeco 高级组件
- `src/views/demo/styles/` — FreqtradeDemo, TdxpyDemo
- `src/views/monitoring/styles/` — WatchlistManagement, RiskDashboard
- `src/views/market/styles/` — Etf, Technical, Tdx
- `src/views/styles/` — monitor, StockDetail, EnhancedDashboard 等
- `src/views/artdeco-pages/styles/` — ArtDecoDashboard

### 2.2 Composable 提取

从逻辑膨胀组件中提取了 4 个 composable + 1 个配置模块：

| 文件 | 行数 | 来源组件 | 职责 |
|------|------|----------|------|
| `useKLineData.ts` | 235 | KLineChart.vue | K线数据管理：hash生成、数据转换、缓存、批量渲染 |
| `useKLineControls.ts` | 203 | KLineChart.vue | K线交互控制：缩放、平移、重置、周期切换 |
| `klineChartConfig.ts` | 248 | KLineChart.vue | 图表配置常量：样式、初始化选项、缩放级别 |
| `useDashboardCharts.ts` | 311 | EnhancedDashboard.vue | 仪表盘图表：价格分布、热力图、板块、资金流 |
| `useDashboardWatchlist.ts` | 118 | EnhancedDashboard.vue | 自选股操作：加载、添加、删除 |

**重构效果：**
- KLineChart.vue: 1128 → 436 行（-61%）
- EnhancedDashboard.vue: 1100 → 577 行（-48%）

---

## 三、编码规范指南

### 3.1 组件体积控制

| 指标 | 阈值 | 处理方式 |
|------|------|----------|
| 总行数 > 800 | ⚠️ 警告 | 评估是否需要拆分 |
| 总行数 > 1000 | 🚫 禁止 | 必须拆分 |
| style > 300 行 | ⚠️ 警告 | 提取为独立 SCSS 文件 |
| script > 500 行 | ⚠️ 警告 | 提取 composable |
| template > 400 行 | ⚠️ 警告 | 拆分子组件 |

### 3.2 CSS/SCSS 规范

```bash
# 提交前必须通过 Stylelint 检查
cd web/frontend
npx stylelint "src/**/*.{vue,scss,css}"

# 自动修复
npx stylelint "src/**/*.{vue,scss,css}" --fix
```

**关键规则：**
- 不允许 shorthand 属性覆盖 longhand（如 `padding-bottom` 后跟 `padding`）
- 不允许重复选择器
- 不允许重复 @keyframes 百分比选择器
- 不允许使用废弃属性（如 `clip`，使用 `clip-path` 替代）
- 颜色函数使用现代写法：`rgb(0 0 0 / 50%)` 而非 `rgba(0, 0, 0, 0.5)`
- 透明度使用百分比：`50%` 而非 `0.5`

**SCSS 文件组织：**
```
src/components/artdeco/advanced/
├── ArtDecoCapitalFlow.vue
├── ArtDecoChipDistribution.vue
└── styles/
    ├── ArtDecoCapitalFlow.scss
    └── ArtDecoChipDistribution.scss
```

### 3.3 TypeScript 规范

- **禁止** 在业务代码中使用 `as any`，仅允许在测试文件中使用
- 优先使用具体类型或 `unknown` + 类型守卫
- API 响应类型定义在 `src/api/types/` 目录下

```typescript
// ❌ 错误
const data = response.data as any

// ✅ 正确
interface StockData { symbol: string; price: number }
const data = response.data as StockData
```

### 3.4 Vue 模板规范

- `v-for` 必须搭配 `:key`，且 key 值必须唯一
- 禁止使用 index 作为 key（列表有增删操作时）
- 使用 Element Plus 组件，禁止引入 ant-design-vue

```vue
<!-- ❌ 错误 -->
<div v-for="item in list">{{ item.name }}</div>
<div v-for="(item, index) in list" :key="index">{{ item.name }}</div>

<!-- ✅ 正确 -->
<div v-for="item in list" :key="item.id">{{ item.name }}</div>
```

### 3.5 内存管理规范

所有 `setInterval` / `setTimeout` / `addEventListener` 必须在 `onUnmounted` 中清理：

```typescript
// ✅ 正确模式
const timer = ref<ReturnType<typeof setInterval>>()

onMounted(() => {
  timer.value = setInterval(fetchData, 5000)
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = undefined
  }
})
```

ECharts 实例必须在卸载时 dispose：

```typescript
onUnmounted(() => {
  chartInstance?.dispose()
  chartInstance = null
})
```

### 3.6 ECharts 按需导入

```typescript
// ❌ 错误 - 全量导入 (~800KB)
import * as echarts from 'echarts'

// ✅ 正确 - 按需导入 (~200KB)
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent])
```

### 3.7 Composable 编写规范

```typescript
// 文件命名：use + 功能名，驼峰式
// 路径：src/composables/useXxx.ts

export function useStockData(symbol: Ref<string>) {
  // 1. 响应式状态
  const data = ref<StockData[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 2. 方法
  async function fetchData() { /* ... */ }

  // 3. 生命周期
  onMounted(() => fetchData())
  onUnmounted(() => { /* cleanup */ })

  // 4. 返回所有外部需要的状态和方法
  return { data, loading, error, fetchData }
}
```

---

## 四、测试检查清单

### 4.1 提交前自检

```bash
cd web/frontend

# 1. Stylelint（必须 0 错误）
npx stylelint "src/**/*.{vue,scss,css}"

# 2. ESLint
npx eslint src/ --ext .ts,.vue

# 3. TypeScript 类型检查
npx vue-tsc --noEmit

# 4. 单元测试
npx vitest --run
```

### 4.2 Code Review 关注点

- [ ] 新组件是否超过 800 行？
- [ ] v-for 是否都有唯一 :key？
- [ ] 是否有 `as any`？（测试文件除外）
- [ ] timer/listener 是否在 onUnmounted 中清理？
- [ ] ECharts 是否按需导入？
- [ ] CSS 超过 300 行是否提取为独立 SCSS？
- [ ] 是否引入了 ant-design-vue？（禁止）
- [ ] 新增 composable 是否遵循命名和返回值规范？

### 4.3 CI/CD 集成建议

```yaml
# 建议在 CI 中添加以下检查
lint:
  script:
    - cd web/frontend
    - npx stylelint "src/**/*.{vue,scss,css}"
    - npx eslint src/ --ext .ts,.vue
    - npx vue-tsc --noEmit

# 组件体积检查（可选）
size-check:
  script:
    - |
      cd web/frontend
      find src/ -name "*.vue" -exec sh -c '
        lines=$(wc -l < "$1")
        if [ "$lines" -gt 1000 ]; then
          echo "❌ $1: $lines lines (max 1000)"
          exit 1
        fi
      ' _ {} \;
```

---

## 五、当前技术债

| 项目 | 数量 | 优先级 | 说明 |
|------|------|--------|------|
| 500+ 行组件 | 108 个 | P3 | 大部分是 CSS 提取后的合理体积，可逐步优化 |
| 多入口文件 | 5 个 main-*.js/ts | P3 | main-debug.js 等调试入口，暂不影响生产 |
| StockAnalysisDemo.vue | 1002 行 | P3 | Demo 页面，静态内容为主 |

---

*本报告基于 `reports/vue3-code-audit-report.md` 审核计划生成，作为后续编码和测试的参考基准。*
