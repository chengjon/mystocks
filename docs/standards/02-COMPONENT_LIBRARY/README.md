# 组件库

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [UI_DESIGN_SYSTEM.md](../UI_DESIGN_SYSTEM.md)

---

## 📋 目录

本目录包含 MyStocks 的所有 UI 组件规范。

### 📄 文档列表

1. **[基础组件](./base-components.md)** - Base Components
   - 按钮 (Buttons)
   - 表单 (Forms)
   - 输入框 (Inputs)
   - 选择器 (Selects)
   - 日期选择 (Date Pickers)

2. **[业务组件](./business-components.md)** - Business Components
   - 股票卡片 (Stock Card)
   - 行情表格 (Quote Table)
   - K线图表 (Kline Chart)
   - 技术指标面板 (Indicator Panel)
   - 交易面板 (Trade Panel)

3. **[图表组件](./chart-components.md)** - Chart Components
   - 分时图 (Time-sharing Chart)
   - K线图 (Candlestick Chart)
   - 热力图 (Heatmap)
   - 资金流向图 (Fund Flow Chart)

4. **[复合组件](./composite-components.md)** - Composite Components
   - 策略配置器 (Strategy Configurator)
   - 回测报告 (Backtest Report)
   - 风险仪表板 (Risk Dashboard)
   - 数据表格 (Data Table)

---

## 🎨 组件库概述

MyStocks 组件库基于 **Element Plus**，结合金融数据可视化的特殊需求，提供专业、高效、易用的组件集合。

### 设计原则

1. **一致性** - 统一的交互模式和视觉风格
2. **可复用** - 高度模块化，支持多场景使用
3. **可定制** - 支持主题定制和样式覆盖
4. **高性能** - 优化的渲染性能和大数据处理

### 组件层级

```
组件库
├── 基础组件 (Base Components)
│   ├── 按钮
│   ├── 表单
│   ├── 输入框
│   └── 选择器
│
├── 业务组件 (Business Components)
│   ├── 股票卡片
│   ├── 行情表格
│   └── 技术指标面板
│
├── 图表组件 (Chart Components)
│   ├── 分时图
│   ├── K线图
│   └── 热力图
│
└── 复合组件 (Composite Components)
    ├── 策略配置器
    ├── 回测报告
    └── 风险仪表板
```

---

## 🎯 快速参考

### Element Plus 常用组件

| 组件名 | 用途 | 文档 |
|-------|------|------|
| `el-button` | 按钮 | [文档](https://element-plus.org/en-US/component/button.html) |
| `el-input` | 输入框 | [文档](https://element-plus.org/en-US/component/input.html) |
| `el-select` | 下拉选择 | [文档](https://element-plus.org/en-US/component/select.html) |
| `el-table` | 表格 | [文档](https://element-plus.org/en-US/component/table.html) |
| `el-form` | 表单 | [文档](https://element-plus.org/en-US/component/form.html) |
| `el-dialog` | 对话框 | [文档](https://element-plus.org/en-US/component/dialog.html) |
| `el-card` | 卡片 | [文档](https://element-plus.org/en-US/component/card.html) |
| `el-tabs` | 标签页 | [文档](https://element-plus.org/en-US/component/tabs.html) |
| `el-tag` | 标签 | [文档](https://element-plus.org/en-US/component/tag.html) |
| `el-tooltip` | 文字提示 | [文档](https://element-plus.org/en-US/component/tooltip.html) |

### 自定义业务组件

| 组件名 | 文件路径 | 用途 |
|-------|---------|------|
| `StockCard` | `@/components/market/StockCard.vue` | 股票信息卡片 |
| `QuoteTable` | `@/components/market/QuoteTable.vue` | 实时行情表格 |
| `KlineChart` | `@/components/charts/KlineChart.vue` | K线图表 |
| `IndicatorPanel` | `@/components/analysis/IndicatorPanel.vue` | 技术指标面板 |
| `TradePanel` | `@/components/trade/TradePanel.vue` | 交易面板 |
| `StrategyConfigurator` | `@/components/strategy/StrategyConfigurator.vue` | 策略配置器 |
| `BacktestReport` | `@/components/strategy/BacktestReport.vue` | 回测报告 |
| `RiskDashboard` | `@/components/risk/RiskDashboard.vue` | 风险仪表板 |

---

## 🧩 组件开发规范

### 组件文件结构

```
ComponentName.vue
├── <template>          // 模板
├── <script setup>      // 逻辑
│   ├── Props 定义      // TypeScript 接口
│   ├── Emits 定义      // 事件定义
│   ├── 响应式数据      // ref/reactive
│   ├── 计算属性        // computed
│   ├── 方法            // functions
│   └── 生命周期        // onMounted 等
└── <style scoped>      // 样式 (SCSS)
```

### 组件命名规范

**文件命名**: PascalCase

```
✅ 正确:
StockCard.vue
QuoteTable.vue
KlineChart.vue

❌ 错误:
stockCard.vue
quote-table.vue
kline_chart.vue
```

**组件内部命名**:

```vue
<script setup lang="ts">
// ✅ 正确: 使用 use 前缀
const stockData = ref<StockData[]>([])
const isLoading = ref(false)
const handleClick = () => {}

// ❌ 错误: 过于简单
const data = ref([])
const loading = ref(false)
const click = () => {}
</script>
```

### 组件 Props 规范

**使用 TypeScript 接口定义**:

```vue
<script setup lang="ts">
interface Props {
  // 股票代码
  symbol: string
  // 股票名称
  name: string
  // 当前价格
  price: number
  // 涨跌幅
  changePercent: number
  // 是否加载中 (可选)
  loading?: boolean
  // 尺寸 (可选, 默认 'default')
  size?: 'small' | 'default' | 'large'
}

// 使用 withDefaults 设置默认值
const props = withDefaults(defineProps<Props>(), {
  loading: false,
  size: 'default',
})
</script>
```

### 组件 Emits 规范

**明确定义事件**:

```vue
<script setup lang="ts">
// 定义事件
interface Emits {
  (e: 'click', symbol: string): void
  (e: 'change', value: number): void
  (e: 'delete', id: string): void
}

const emit = defineEmits<Emits>()

// 触发事件
const handleClick = () => {
  emit('click', props.symbol)
}
</script>
```

### 组件示例

```vue
<template>
  <el-card class="stock-card" :class="[`size-${size}`]" @click="handleClick">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>

    <!-- 股票信息 -->
    <div class="stock-info">
      <div class="stock-name">
        <span class="symbol">{{ symbol }}</span>
        <span class="name">{{ name }}</span>
      </div>

      <div class="stock-price">
        <span class="price">{{ formatPrice(price) }}</span>
        <span :class="['change', changeClass]">
          {{ formatChange(changePercent) }}
        </span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

// Props 定义
interface Props {
  symbol: string
  name: string
  price: number
  changePercent: number
  loading?: boolean
  size?: 'small' | 'default' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  size: 'default',
})

// Emits 定义
interface Emits {
  (e: 'click', symbol: string): void
}

const emit = defineEmits<Emits>()

// 计算属性
const changeClass = computed(() => {
  if (props.changePercent > 0) return 'rise'
  if (props.changePercent < 0) return 'fall'
  return 'flat'
})

// 方法
const formatPrice = (price: number) => {
  return price.toFixed(2)
}

const formatChange = (percent: number) => {
  const sign = percent > 0 ? '+' : ''
  return `${sign}${percent.toFixed(2)}%`
}

const handleClick = () => {
  emit('click', props.symbol)
}
</script>

<style lang="scss" scoped>
.stock-card {
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: $--box-shadow-light;
    transform: translateY(-2px);
  }

  &.size-small {
    .stock-name {
      font-size: $font-size-small;
    }

    .stock-price .price {
      font-size: $font-size-h3;
    }
  }

  &.size-large {
    .stock-name {
      font-size: $font-size-h4;
    }

    .stock-price .price {
      font-size: 36px;
    }
  }
}

.stock-info {
  padding: $spacing-md;
}

.stock-name {
  margin-bottom: $spacing-sm;

  .symbol {
    font-weight: $font-weight-semibold;
    color: $--color-text-primary;
    margin-right: $spacing-xs;
  }

  .name {
    color: $--color-text-secondary;
  }
}

.stock-price {
  display: flex;
  align-items: baseline;
  gap: $spacing-sm;

  .price {
    font-family: $font-family-number;
    font-size: $font-size-h3;
    font-weight: $font-weight-bold;
    color: $--color-text-primary;
  }

  .change {
    font-family: $font-family-number;
    font-size: $font-size-body;
    font-weight: $font-weight-medium;

    &.rise {
      color: $--color-stock-rise;
    }

    &.fall {
      color: $--color-stock-fall;
    }

    &.flat {
      color: $--color-text-secondary;
    }
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
```

---

## 🎨 组件样式规范

### 使用 SCSS 变量

```vue
<style lang="scss" scoped>
.my-component {
  // ✅ 使用 Design Tokens
  padding: $spacing-md;
  border-radius: $--border-radius-base;
  background-color: $--color-bg-white;
  color: $--color-text-primary;

  // ❌ 避免硬编码
  // padding: 16px;
  // border-radius: 4px;
  // background-color: #FFFFFF;
}
</style>
```

### BEM 命名规范

```scss
// Block
.stock-card {}

// Element
.stock-card__header {}
.stock-card__body {}
.stock-card__footer {}

// Modifier
.stock-card--small {}
.stock-card--large {}
.stock-card--disabled {}

// 使用示例
<div class="stock-card stock-card--large">
  <div class="stock-card__header">...</div>
  <div class="stock-card__body">...</div>
  <div class="stock-card__footer">...</div>
</div>
```

### 响应式样式

```vue
<style lang="scss" scoped>
.my-component {
  padding: $spacing-md;

  // 平板和手机
  @media (max-width: $breakpoint-md) {
    padding: $spacing-sm;
  }

  // 手机
  @media (max-width: $breakpoint-sm) {
    padding: $spacing-xs;
  }
}
</style>
```

---

## 📊 组件性能优化

### 懒加载组件

```typescript
// 路由懒加载
const KlineChart = () => import('@/components/charts/KlineChart.vue')
const BacktestReport = () => import('@/components/strategy/BacktestReport.vue')

// 使用
{
  path: '/chart',
  component: KlineChart,
}
```

### 虚拟滚动

```vue
<template>
  <!-- 使用虚拟滚动处理大数据列表 -->
  <el-table
    :data="tableData"
    height="400"
    virtual
  >
    <el-table-column prop="symbol" label="代码" />
    <el-table-column prop="name" label="名称" />
  </el-table>
</template>
```

### 组件缓存

```vue
<template>
  <!-- 使用 keep-alive 缓存组件 -->
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>
```

---

## ✅ 组件检查清单

在创建新组件时，请确保：

- [ ] 使用 TypeScript 定义 Props 和 Emits
- [ ] 使用 PascalCase 命名文件
- [ ] 提供默认值和类型检查
- [ ] 添加加载状态
- [ ] 添加错误处理
- [ ] 使用 Design Tokens
- [ ] 遵循 BEM 命名规范
- [ ] 支持响应式布局
- [ ] 添加组件文档注释
- [ ] 编写单元测试

---

## 📚 相关资源

### Element Plus
- [Element Plus 组件文档](https://element-plus.org/en-US/component/overview.html)
- [Element Plus 设计指南](https://element-plus.org/en-US/guide/design.html)
- [Element Plus 主题定制](https://element-plus.org/en-US/guide/theming.html)

### Vue 3
- [Vue 3 组件基础](https://vuejs.org/guide/essentials/component-basics.html)
- [Vue 3 TypeScript 支持](https://vuejs.org/guide/typescript/overview.html)
- [Vue 3 性能优化](https://vuejs.org/guide/best-practices/performance.html)

### 开发工具
- [Vue DevTools](https://devtools.vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Volar (VS Code Extension)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

---

## 🔄 更新日志

### v1.0.0 (2025-12-25)
- ✅ 初始版本
- ✅ 定义组件开发规范
- ✅ 提供组件示例
- ✅ 建立组件检查清单

---

## 📞 联系方式

- **设计团队**: design@mystocks.com
- **前端团队**: frontend@mystocks.com
- **问题反馈**: [GitHub Issues](https://github.com/chengjon/mystocks/issues)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/02-COMPONENT_LIBRARY/README.md`
