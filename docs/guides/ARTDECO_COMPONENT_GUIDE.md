# ArtDeco 组件开发指南

> 基于 MyStocks 项目实践总结的组件开发规范

## 目录

- [概述](#概述)
- [开发流程](#开发流程)
- [模板规范](#模板规范)
- [脚本规范](#脚本规范)
- [样式规范](#样式规范)
- [验收标准](#验收标准)
- [检查清单](#检查清单)
- [常见问题](#常见问题)

---

## 概述

本文档定义了 MyStocks 项目中 ArtDeco 风格组件的开发规范。基于项目的 ArtDeco 混合风格（Art Deco + 现代 Vue 3 + A 股金融标准），提供从设计到交付的完整开发指南。

### 设计原则

| 原则 | 说明 |
|------|------|
| **几何装饰** | 阶梯角、L形装饰、几何形状是 Art Deco 的核心特征 |
| **戏剧化对比** | 黑金配色、发光效果、戏剧化过渡 |
| **金融标准** | A 股红涨绿跌、单色号字体、等宽数字 |
| **BEM 规范** | 使用 BEM 命名保证样式隔离和可维护性 |
| **SCSS 设计令牌** | 所有颜色、间距、字体必须使用 CSS 变量 |

### 设计令牌引用

```scss
// 必须导入的设计令牌
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';
```

---

## 开发流程

### 第一步：需求分析与结构设计

#### 1.1 分析组件职责
- 确定组件是 **展示型** 还是 **交互型**
- 确定数据输入接口 (`props`)
- 确定事件输出接口 (`emits`)
- 确定依赖的子组件

#### 1.2 定义 TypeScript 接口

```typescript
// ✅ 推荐：完整的类型定义
export interface TradeHistory {
  id: number
  time: string
  symbol: string
  symbolName: string
  type: 'buy' | 'sell'
  typeText: string
  price: number
  quantity: number
  amount: number
  fee: number
  status: 'completed' | 'pending' | 'cancelled'
  statusText: string
}

interface Props {
  history: TradeHistory[]
}

defineProps<Props>()
```

#### 1.3 规划模板结构

```
组件容器
├── 角落装饰 (corner decorations)
├── 头部 (可选 header slot)
├── 内容区 (body slot)
└── 底部 (可选 footer slot)
```

### 第二步：模板编写

#### 2.1 基础结构

```vue
<template>
  <div class="artdeco-[component-name]">
    <!-- Art Deco 签名：角落装饰 -->
    <div class="artdeco-[component-name]__corner artdeco-[component-name]__corner--tl"></div>
    <div class="artdeco-[component-name]__corner artdeco-[component-name]__corner--br"></div>

    <!-- 内容区域 -->
    <ArtDecoCard title="组件标题" hoverable>
      <div class="artdeco-[component-name]__content">
        <!-- 业务内容 -->
      </div>
    </ArtDecoCard>
  </div>
</template>
```

#### 2.2 使用现有 ArtDeco 组件

```vue
<script setup lang="ts">
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
import ArtDecoInput from '@/components/artdeco/base/ArtDecoInput.vue'
import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
</script>
```

#### 2.3 表格/列表结构 (BEM 规范)

```vue
<div class="artdeco-trading-signals__table">
  <!-- 表头 -->
  <div class="artdeco-trading-signals__header">
    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time">时间</div>
    <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol">股票</div>
  </div>
  
  <!-- 数据行 -->
  <div class="artdeco-trading-signals__body">
    <div class="artdeco-trading-signals__row" v-for="item in data" :key="item.id">
      <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time">{{ item.time }}</div>
      <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol">{{ item.symbol }}</div>
    </div>
  </div>
</div>
```

### 第三步：样式编写

#### 3.1 基础框架

```scss
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

.artdeco-[component-name] {
  position: relative;
  width: 100%;

  // Art Deco 签名：阶梯角
  @include artdeco-stepped-corners(8px);

  // Art Deco 签名：几何角落装饰
  @include artdeco-geometric-corners(
    $color: var(--artdeco-gold-primary),
    $size: 16px,
    $border-width: 2px
  );

  // 戏剧化悬停效果
  @include artdeco-hover-lift-glow;
}
```

#### 3.2 颜色使用规范

```scss
// ✅ 正确：使用设计令牌

// 背景色
background: var(--artdeco-bg-card);
background: var(--artdeco-bg-elevated);

// 前景色
color: var(--artdeco-fg-primary);      // 主文本 (香槟奶油)
color: var(--artdeco-fg-muted);        // 次要文本 (锡色)

// 边框色
border: 1px solid var(--artdeco-border-default);

// A 股金融色 (红涨绿跌)
color: var(--artdeco-up);    // 涨/盈利/红色
color: var(--artdeco-down);  // 跌/亏损/绿色

// 金色强调
color: var(--artdeco-gold-primary);
border-color: var(--artdeco-gold-primary);

// ❌ 错误：硬编码颜色
color: #FF5252;  // 应该用 var(--artdeco-up)
color: #52c41a;  // 应该用 var(--artdeco-down)
color: #D4AF37;  // 应该用 var(--artdeco-gold-primary)
```

#### 3.3 排版规范

```scss
// 标签使用大写 + 宽字间距
.artdeco-[component-name]__label {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  font-weight: 600;
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

// 数据使用等宽字体
.artdeco-[component-name]__value {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-base);
  font-weight: 600;
}

// 标题使用 Display 字体
.artdeco-[component-name]__title {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
}
```

#### 3.4 过渡动画

```scss
// 所有交互使用戏剧化过渡 (300-500ms)
transition: all var(--artdeco-transition-base);  // 300ms
transition: all var(--artdeco-transition-slow);  // 500ms
transition: all var(--artdeco-transition-fast); // 150ms
```

#### 3.5 角落装饰

```scss
.artdeco-[component-name]__corner {
  position: absolute;
  width: 16px;
  height: 16px;
  border-color: var(--artdeco-gold-primary);
  border-style: solid;
  opacity: 0.4;
  transition: opacity var(--artdeco-transition-base);
  z-index: 1;
}

.artdeco-[component-name]__corner--tl {
  top: -1px;
  left: -1px;
  border-width: 2px 0 0 2px;  // 左上角
}

.artdeco-[component-name]__corner--br {
  bottom: -1px;
  right: -1px;
  border-width: 0 2px 2px 0;  // 右下角
}
```

### 第四步：单元测试

```typescript
// tests/unit/components/ArtDecoTradingSignals.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ArtDecoTradingSignals from '@/views/artdeco-pages/components/ArtDecoTradingSignals.vue'

describe('ArtDecoTradingSignals', () => {
  it('正确渲染信号列表', () => {
    const signals = [
      { id: 1, symbol: '600519', type: 'buy', typeText: '买入' }
    ]
    const wrapper = mount(ArtDecoTradingSignals, {
      props: { signals }
    })
    expect(wrapper.findAll('.artdeco-trading-signals__row')).toHaveLength(1)
  })

  it('正确显示涨跌颜色', () => {
    // 测试用例...
  })
})
```

---

## 模板规范

### 文件命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 页面组件 | `ArtDeco[功能]Management.vue` | `ArtDecoTradingManagement.vue` |
| 子组件 | `ArtDeco[功能][类型].vue` | `ArtDecoTradingSignals.vue` |
| 组合式函数 | `use[功能].ts` | `useTradingData.ts` |
| API 层 | `[功能].ts` | `trading.ts` |

### 目录结构

```
web/frontend/src/
├── views/artdeco-pages/
│   ├── ArtDecoTradingManagement.vue    # 主页面
│   └── components/
│       ├── ArtDecoTradingSignals.vue      # 信号表格
│       ├── ArtDecoTradingHistory.vue      # 历史记录
│       └── ArtDecoTradingPositions.vue   # 持仓列表
├── composables/artdeco/
│   ├── useTradingData.ts
│   └── useSignalMonitoring.ts
└── api/artdeco/
    ├── trading.ts
    └── types.ts
```

---

## 脚本规范

### Vue 3 Composition API

```vue
<script setup lang="ts">
import { computed, ref } from 'vue'

// 1. 类型定义
export interface TradeItem {
  id: number
  symbol: string
  type: 'buy' | 'sell'
  // ...
}

// 2. Props 定义
interface Props {
  data: TradeItem[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// 3. Emits 定义
const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'delete', id: number): void
}>()

// 4. 组合式函数
const { data, loading } = useTradingData()

// 5. 计算属性
const filteredData = computed(() => {
  return props.data.filter(item => item.status === 'active')
})

// 6. 方法
const handleSelect = (id: number) => {
  emit('select', id)
}
</script>
```

---

## 样式规范

### SCSS 结构顺序

```scss
<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

// 1. 容器基础样式
.artdeco-[component-name] {
  @include artdeco-stepped-corners(8px);
  @include artdeco-geometric-corners(...);
  @include artdeco-hover-lift-glow;
}

// 2. 子元素样式 (BEM: __element)
.artdeco-[component-name]__header {
  // ...
}

.artdeco-[component-name]__body {
  // ...
}

// 3. 修饰符 (BEM: --modifier)
.artdeco-[component-name]--variant {
  // ...
}

// 4. 状态
.is-active {
  // ...
}

// 5. 响应式
@media (max-width: 1200px) {
  // ...
}
</style>
```

### 常用 Mixins

| Mixin | 用途 | 示例 |
|-------|------|------|
| `@include artdeco-stepped-corners(8px)` | 阶梯角效果 | 卡片容器 |
| `@include artdeco-geometric-corners()` | L形角落装饰 | 卡片、组件容器 |
| `@include artdeco-hover-lift-glow` | 悬停提升+发光 | 可交互元素 |
| `@include artdeco-hover-lift` | 悬停提升 | 非发光交互 |
| `@include artdeco-financial-data` | 金融数据样式 | 数字显示 |

---

## 验收标准

### 功能验收

| 检查项 | 标准 |
|--------|------|
| 数据渲染 | 正确渲染所有 prop 数据 |
| 事件传递 | 正确触发定义的 emit 事件 |
| 交互响应 | 按钮点击、选项切换等交互正常 |
| 边界条件 | 空数据、加载状态处理正确 |

### 样式验收

| 检查项 | 标准 |
|--------|------|
| 阶梯角 | 组件有明显的阶梯角效果 |
| 角落装饰 | 左上角和右下角有 L 形金色装饰 |
| 悬停效果 | 悬停时有提升 + 发光效果 |
| 颜色规范 | 使用 CSS 变量，无硬编码颜色 |
| 排版规范 | 标签使用大写 + 宽字间距 |
| 过渡动画 | 交互有 300ms 过渡效果 |
| A 股标准 | 涨红 (#FF5252)、跌绿 (#00E676) |

### 代码质量验收

| 检查项 | 标准 |
|--------|------|
| 类型安全 | 所有 props/emits 有完整类型定义 |
| 导入规范 | 使用 `@/` 别名导入 |
| 命名规范 | BEM 命名，组件 PascalCase |
| 样式隔离 | 使用 `scoped` |
| 设计令牌 | 颜色/间距/字体使用 CSS 变量 |

### 性能验收

| 检查项 | 标准 |
|--------|------|
| 渲染性能 | 大数据量无明显卡顿 |
| 包体积 | 无冗余依赖 |
| 响应式 | 适配项目定义的断点 |

---

## 检查清单

### 新增组件前

- [ ] 分析组件职责和数据流
- [ ] 定义完整的 TypeScript 接口
- [ ] 规划模板结构
- [ ] 确定依赖的 ArtDeco 基础组件

### 开发中

- [ ] 导入设计令牌 (`@/styles/artdeco-tokens.scss`)
- [ ] 应用阶梯角 mixin
- [ ] 应用几何角落装饰
- [ ] 使用 CSS 变量替代硬编码颜色
- [ ] 应用大写 + 宽字间距排版
- [ ] 添加戏剧化过渡动画
- [ ] 正确使用 A 股金融色

### 完成后

- [ ] 运行 `lsp_diagnostics` 无错误
- [ ] 单元测试覆盖核心逻辑
- [ ] 样式验收通过
- [ ] 与现有组件风格一致

---

## 常见问题

### Q1: 什么时候使用 `var(--artdeco-up)` 和 `var(--artdeco-down)`？

A 股标准是「红涨绿跌」，与美股相反：
- `var(--artdeco-up)` = 涨/盈利/收益 = 红色 (#FF5252)
- `var(--artdeco-down)` = 跌/亏损/损失 = 绿色 (#00E676)

```vue
<!-- 价格显示 -->
<span :class="price >= 0 ? 'text-rise' : 'text-fall'">
  {{ price >= 0 ? '+' : '' }}{{ price }}%
</span>

<style scoped>
.text-rise {
  color: var(--artdeco-up);  // 红色 = 涨
}

.text-fall {
  color: var(--artdeco-down);  // 绿色 = 跌
}
</style>
```

### Q2: 角落装饰的位置？

ArtDeco 惯例使用 **左上角 + 右下角** 的对角线装饰：

```html
<div class="artdeco-xxx__corner artdeco-xxx__corner--tl"></div>  <!-- 左上 -->
<div class="artdeco-xxx__corner artdeco-xxx__corner--br"></div>  <!-- 右下 -->
```

### Q3: 过渡动画时长如何选择？

| 时长 | 使用场景 | CSS 变量 |
|------|----------|----------|
| 150ms | 简单状态切换 | `var(--artdeco-transition-fast)` |
| 300ms | 常规交互 | `var(--artdeco-transition-base)` |
| 500ms | 戏剧化效果 | `var(--artdeco-transition-slow)` |

### Q4: 字体如何选择？

| 用途 | 字体变量 | 使用场景 |
|------|----------|----------|
| Display | `var(--artdeco-font-display)` | 标题、标签 |
| Body | `var(--artdeco-font-body)` | 正文、说明 |
| Mono | `var(--artdeco-font-mono)` | 数字、代码 |

### Q5: 如何处理表格/列表？

使用 CSS Grid + BEM 命名：

```vue
<div class="artdeco-trading-signals__header">
  <div class="artdeco-trading-signals__col artdeco-trading-signals__col--time">时间</div>
  <div class="artdeco-trading-signals__col artdeco-trading-signals__col--symbol">股票</div>
</div>

<style scoped>
.artdeco-trading-signals__header {
  display: grid;
  grid-template-columns: 150px 120px;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}
</style>
```

---

## 参考资源

### 内部资源

- [ArtDeco.md](/opt/mydoc/design/ArtDeco/ArtDeco.md) - ArtDeco 设计规范
- [README.md](/opt/mydoc/design/ArtDeco/README.md) - 组件库文档
- `web/frontend/src/styles/artdeco-tokens.scss` - 设计令牌
- `web/frontend/src/styles/artdeco-patterns.scss` - 样式模式

### 现有组件参考

- `ArtDecoCard.vue` - 卡片容器
- `ArtDecoButton.vue` - 按钮变体
- `ArtDecoStatCard.vue` - 统计卡片
- `ArtDecoTable.vue` - 数据表格

---

**维护者**: MyStocks 前端团队  
**最后更新**: 2026-01-14
