# MyStocks ARIA 无障碍性实施指南

**版本**: 1.0
**创建日期**: 2026-01-13
**优先级**: P1 - 无障碍性增强

---

## 📋 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [useAria Composable API](#usearia-composable-api)
4. [组件ARIA实施指南](#组件aria实施指南)
5. [测试清单](#测试清单)
6. [常见问题](#常见问题)

---

## 🚀 快速开始

### 安装和导入

```typescript
import { useAria } from '@/composables/useAria'

const aria = useAria()
```

### 基础用法

```vue
<script setup lang="ts">
import { useAria } from '@/composables/useAria'

const { button, input, liveRegion } = useAria()

// 按钮ARIA标签
const submitButtonAria = button('提交表单')

// 输入框ARIA标签
const searchInputAria = input('股票代码', {
  required: true,
  describedBy: 'search-hint'
})

// 实时数据区域ARIA标签
const statCardAria = liveRegion('上证指数', 'polite')
</script>

<template>
  <!-- 按钮 -->
  <button v-bind="submitButtonAria">提交</button>

  <!-- 输入框 -->
  <input v-bind="searchInputAria" />
  <div id="search-hint">输入6位股票代码</div>

  <!-- 实时数据卡片 -->
  <div v-bind="statCardAria">3,245.67</div>
</template>
```

---

## 🎯 核心概念

### ARIA标签的作用

ARIA（Accessible Rich Internet Applications）标签帮助辅助技术（如屏幕阅读器）理解和导航Web应用。

### 关键ARIA属性

| 属性 | 用途 | 示例 |
|------|------|------|
| `aria-label` | 为元素提供可访问名称 | `<button aria-label="关闭对话框">×</button>` |
| `aria-live` | 标识动态内容区域 | `<div aria-live="polite">股票价格</div>` |
| `aria-describedby` | 关联描述文本 | `<input aria-describedby="hint">` |
| `aria-expanded` | 标识可展开/折叠状态 | `<button aria-expanded="false">菜单</button>` |
| `aria-hidden` | 隐藏装饰性内容 | `<span aria-hidden="true">✨</span>` |
| `role` | 定义元素语义角色 | `<div role="button">点击</div>` |

### WCAG合规性

本指南遵循WCAG 2.1 Level AA标准：
- **1.1.1 Text Alternatives**: 为非文本内容提供替代
- **1.3.1 Info and Relationships**: 明确元素角色和关系
- **2.4.4 Link Purpose**: 链接目的明确
- **4.1.2 Name, Role, Value**: 所有UI元素有名称、角色和值

---

## 📚 useAria Composable API

### 1. button() - 按钮ARIA标签

为按钮提供无障碍标签。

```typescript
const aria = useAria()

button(label?: string, options?: {
  disabled?: boolean
  pressed?: boolean
  expanded?: boolean
  hasPopup?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog'
  controls?: string
})
```

**示例**：

```vue
<!-- 基础按钮 -->
<script setup>
const { button } = useAria()
const ariaProps = button('执行交易')
</script>

<template>
  <button v-bind="ariaProps">执行交易</button>
</template>

<!-- 切换按钮 -->
<script setup>
const { button } = useAria()
const isActive = ref(false)
const ariaProps = computed(() =>
  button('静音', { pressed: isActive.value })
)
</script>

<template>
  <button v-bind="ariaProps" @click="isActive = !isActive">
    静音
  </button>
</template>

<!-- 下拉按钮 -->
<script setup>
const { button } = useAria()
const ariaProps = button('用户菜单', { hasPopup: true, expanded: false })
</script>

<template>
  <button v-bind="ariaProps" aria-controls="user-menu">
    用户 ▼
  </button>
  <div id="user-menu">...</div>
</template>
```

### 2. link() - 链接ARIA标签

为链接提供无障碍标签。

```typescript
const aria = useAria()

link(label?: string, options?: {
  current?: boolean
  describedBy?: string
})
```

**示例**：

```vue
<!-- 当前页面链接 -->
<script setup>
const { link } = useAria()
const ariaProps = link(undefined, { current: true })
</script>

<template>
  <router-link to="/dashboard" v-bind="ariaProps">
    仪表盘（当前页面）
  </router-link>
</template>

<!-- 带描述的链接 -->
<script setup>
const { link, hintId } = useAria()
const hint = hintId('download', 'description')
const ariaProps = link('下载年度报表', { describedBy: hint })
</script>

<template>
  <a v-bind="ariaProps" href="/report.pdf">下载报表</a>
  <span :id="hint">PDF格式，15MB</span>
</template>
```

### 3. input() - 输入框ARIA标签

为表单输入提供无障碍标签。

```typescript
const aria = useAria()

input(label: string, options?: {
  required?: boolean
  invalid?: boolean
  errorMessage?: string
  describedBy?: string
  placeholder?: string
})
```

**示例**：

```vue
<!-- 必填输入框 -->
<script setup>
const { input, hintId } = useAria()
const hint = hintId('stock-code', 'hint')
const ariaProps = input('股票代码', {
  required: true,
  describedBy: hint
})
</script>

<template>
  <label for="stock-code">股票代码</label>
  <input
    id="stock-code"
    v-bind="ariaProps"
    type="text"
  />
  <span :id="hint">请输入6位股票代码</span>
</template>

<!-- 错误状态 -->
<script setup>
const { input, hintId } = useAria()
const errorHint = hintId('email', 'error')
const ariaProps = computed(() => input('电子邮箱', {
  invalid: !isValidEmail.value,
  errorMessage: errorHint
}))
</script>

<template>
  <input v-bind="ariaProps" />
  <span v-if="!isValidEmail" :id="errorHint" role="alert">
    请输入有效的电子邮箱地址
  </span>
</template>
```

### 4. liveRegion() - 实时数据区域

标记动态内容区域（如股票价格、实时数据）。

```typescript
const aria = useAria()

liveRegion(label: string, politeness?: 'polite' | 'assertive')
```

**Politeness级别**：
- `polite`: 等待用户空闲时通知（推荐用于股票价格更新）
- `assertive`: 立即通知用户（仅用于关键警报）

**示例**：

```vue
<!-- 股票价格卡片（已集成到ArtDecoStatCard） -->
<script setup>
import { useAria } from '@/composables/useAria'

const { liveRegion } = useAria()
const ariaProps = liveRegion('上证指数', 'polite')
const stockPrice = ref('3,245.67')
</script>

<template>
  <div v-bind="ariaProps">
    {{ stockPrice }}
  </div>
</template>

<!-- 关键警报 -->
<script setup>
const { liveRegion } = useAria()
const alertAria = liveRegion('价格警报', 'assertive')
</script>

<template>
  <div v-bind="alertAria" role="alert">
    ⚠️ 价格跌破止损线！
  </div>
</template>
```

### 5. modal() - 模态框ARIA标签

为模态框/对话框提供无障碍标签。

```typescript
const aria = useAria()

modal(label: string, options?: {
  describedBy?: string
  labelledBy?: string
})
```

**示例**：

```vue
<script setup>
import { ref } from 'vue'
import { useAria } from '@/composables/useAria'

const { modal } = useAria()
const ariaProps = modal('交易确认')
</script>

<template>
  <div v-bind="ariaProps">
    <h2 id="dialog-title">确认交易</h2>
    <p id="dialog-desc">您确定要以100元买入AAPL吗？</p>
    <button>确认</button>
    <button>取消</button>
  </div>
</template>
```

### 6. selection() - 选择器ARIA标签

为单选框、复选框、选择器提供标签。

```typescript
const aria = useAria()

selection(label: string, options?: {
  checked?: boolean | 'mixed'
  required?: boolean
  invalid?: boolean
  describedBy?: string
})
```

**示例**：

```vue
<!-- 复选框 -->
<script setup>
const { selection } = useAria()
const checked = ref(false)
const ariaProps = computed(() => selection('记住我', {
  checked: checked.value
}))
</script>

<template>
  <label>
    <input
      type="checkbox"
      v-bind="ariaProps"
      v-model="checked"
    />
    记住我
  </label>
</template>
```

### 7. card() - 可点击卡片ARIA标签

为可点击的卡片元素提供标签。

```typescript
const aria = useAria()

card(label: string, options?: {
  selected?: boolean
  expanded?: boolean
  hasPopup?: boolean
})
```

**示例**：

```vue
<script setup>
import { useAria } from '@/composables/useAria'

const { card } = useAria()
const ariaProps = card('查看股票详情', { selected: false })
</script>

<template>
  <div
    v-bind="ariaProps"
    @click="navigateToDetail"
    @keydown.enter="navigateToDetail"
  >
    <h3>AAPL</h3>
    <p>Apple Inc.</p>
  </div>
</template>
```

### 8. decorative() - 隐藏装饰性元素

隐藏纯装饰性内容（如图标、分隔符）。

```typescript
const aria = useAria()

decorative()
```

**示例**：

```vue
<script setup>
import { useAria } from '@/composables/useAria'

const { decorative } = useAria()
const decorativeProps = decorative()
</script>

<template>
  <!-- 装饰性图标 -->
  <span v-bind="decorativeProps">✨</span>

  <!-- 装饰性背景图 -->
  <img v-bind="decorativeProps" src="/pattern.png" alt="" />
</template>
```

---

## 🎨 组件ARIA实施指南

### ArtDecoStatCard 组件

**已集成ARIA标签** ✅

```vue
<template>
  <ArtDecoCard v-bind="ariaProps">
    <!-- icon已设置aria-hidden="true" -->
    <div class="artdeco-stat-icon" aria-hidden="true">📊</div>

    <!-- 实时数据更新区域 -->
    <div
      class="artdeco-stat-value"
      :aria-label="`${label}: ${displayValue}`"
      role="status"
      aria-live="polite"
    >
      {{ displayValue }}
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { useAria } from '@/composables/useAria'

const ariaProps = computed(() => {
  const { liveRegion } = useAria()
  return liveRegion(props.label, 'polite').value
})
</script>
```

### ArtDecoButton 组件

**需要手动添加ARIA标签**（可选）

```vue
<script setup lang="ts">
import { useAria } from '@/composables/useAria'

const { button } = useAria()
const ariaProps = button('执行交易', { disabled: false })
</script>

<template>
  <button :class="buttonClasses" v-bind="ariaProps">
    <span class="artdeco-button__text">
      <slot />
    </span>
  </button>
</script>
```

**何时需要aria-label**：
- ✅ 按钮只有图标：`<button aria-label="关闭">✕</button>`
- ✅ 按钮文字不够描述性：`<button aria-label="添加到自选股">+</button>`
- ❌ 按钮文字已清晰：`<button>提交表单</button>` （无需aria-label）

### 表单组件

**输入框示例**：

```vue
<script setup lang="ts">
import { useAria } from '@/composables/useAria'

const { input, hintId } = useAria()
const hintText = hintId('stock-code', 'hint')
const errorText = hintId('stock-code', 'error')

const ariaProps = computed(() => input('股票代码', {
  required: true,
  describedBy: hintText,
  invalid: hasError.value,
  errorMessage: hasError.value ? errorText : undefined
}))
</script>

<template>
  <label for="stock-code">股票代码</label>
  <input
    id="stock-code"
    v-bind="ariaProps"
    v-model="stockCode"
    @blur="validate"
  />

  <!-- 帮助提示 -->
  <span :id="hintText">请输入6位股票代码</span>

  <!-- 错误消息 -->
  <span v-if="hasError" :id="errorText" role="alert">
    {{ errorMessage }}
  </span>
</template>
```

### 导航组件

**面包屑导航示例**：

```vue
<template>
  <nav aria-label="面包屑导航">
    <ol class="breadcrumb">
      <li>
        <router-link to="/" aria-label="返回首页">
          首页
        </router-link>
      </li>
      <li>
        <router-link to="/stocks" aria-label="返回股票列表">
          股票
        </router-link>
      </li>
      <li aria-current="page">
        AAPL
      </li>
    </ol>
  </nav>
</template>
```

### 实时数据更新区域

**股票行情示例**：

```vue
<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { useAria } from '@/composables/useAria'

const { liveRegion } = useAria()

const props = defineProps<{
  symbol: string
  price: number
  change: number
}>()

const ariaProps = liveRegion(`${props.symbol} 实时价格`, 'polite')

// 价格变化时自动通知屏幕阅读器
watchEffect(() => {
  console.log(`Price updated for ${props.symbol}: ${props.price}`)
})
</script>

<template>
  <div v-bind="ariaProps" class="stock-price">
    <span class="symbol">{{ symbol }}</span>
    <span class="price">{{ price }}</span>
    <span class="change" :class="change > 0 ? 'up' : 'down'">
      {{ change > 0 ? '+' : '' }}{{ change }}%
    </span>
  </div>
</template>
```

---

## ✅ 测试清单

### 1. 屏幕阅读器测试

使用NVDA（Windows）或VoiceOver（Mac）进行测试：

- [ ] 所有交互元素可通过Tab键访问
- [ ] 按钮和链接有清晰的名称
- [ ] 表单输入有关联的标签
- [ ] 实时数据更新时屏幕阅读器会通知
- [ ] 模态框打开时焦点正确移动
- [ ] 错误消息会朗读出来

### 2. 键盘导航测试

- [ ] Tab键顺序符合逻辑
- [ ] Shift+Tab反向导航正常
- [ ] Enter/Space激活按钮和链接
- [ ] Esc键关闭模态框和下拉菜单
- [ ] 方向键操作列表和菜单

### 3. 验证工具测试

使用Chrome DevTools Lighthouse或axe DevTools：

- [ ] 无ARIA错误
- [ ] 对比度≥4.5:1（正常文本）或3:1（大文本/焦点环）
- [ ] 所有图片有alt属性
- [ ] 表单有正确的标签关联

### 4. 浏览器兼容性测试

- [ ] Chrome 86+（支持:focus-visible）
- [ ] Firefox 85+（支持:focus-visible）
- [ ] Safari 15.4+（支持:focus-visible）
- [ ] Edge 86+（支持:focus-visible）

---

## ❓ 常见问题

### Q1: 何时使用aria-label vs. aria-labelledby?

**A**:
- `aria-label`: 直接提供文本标签
  ```vue
  <button aria-label="关闭对话框">✕</button>
  ```
- `aria-labelledby`: 引用页面中可见文本
  ```vue
  <h2 id="dialog-title">确认交易</h2>
  <div aria-labelledby="dialog-title">
    ...
  </div>
  ```

### Q2: aria-live的polite和assertive有何区别？

**A**:
- `polite`: 等待用户空闲时通知（推荐用于股票价格、进度更新）
- `assertive`: 立即中断用户并通知（仅用于关键警报、错误提示）

```vue
<!-- ✅ 正确：股票价格使用polite -->
<div aria-live="polite">价格: 100.50</div>

<!-- ✅ 正确：关键错误使用assertive -->
<div aria-live="assertive" role="alert">
  ⚠️ 交易失败！余额不足
</div>

<!-- ❌ 错误：不要用assertive显示股票价格 -->
<div aria-live="assertive">价格: 100.50</div>
```

### Q3: 何时应该使用role属性？

**A**: 仅在HTML元素语义不足时使用：

```vue
<!-- ✅ 正确：使用原生HTML元素 -->
<button>点击</button>  <!-- 自动获得role="button" -->

<!-- ❌ 错误：不必要的role -->
<button role="button">点击</button>  <!-- 多余！ -->

<!-- ✅ 正确：div模拟按钮时添加role -->
<div role="button" tabindex="0" @click="handleClick" @keydown.enter="handleClick">
  点击
</div>
```

### Q4: 如何隐藏装饰性内容？

**A**: 使用`aria-hidden="true"`：

```vue
<!-- 装饰性图标 -->
<span aria-hidden="true">✨</span>

<!-- 装饰性背景图 -->
<img aria-hidden="true" src="/pattern.png" alt="" />

<!-- ❌ 不要隐藏重要内容 -->
<span aria-hidden="true">关闭</span>  <!-- 错误！屏幕阅读器用户无法关闭 -->
```

### Q5: focus和focus-visible的区别？

**A**:
- `:focus`: 鼠标点击和键盘导航时都显示
- `:focus-visible`: 仅键盘导航时显示（推荐）

本项目的焦点增强已自动处理此差异，无需手动干预。

---

## 📖 参考资料

- [WCAG 2.1标准](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [Vue.js无障碍性指南](https://vuejs.org/guide/best-practices/accessibility.html)
- [MDN ARIA文档](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)

---

## 🔄 更新日志

- **v1.0** (2026-01-13): 初始版本
  - 创建useAria composable
  - 集成到ArtDecoStatCard组件
  - 提供完整API文档和示例

---

**维护者**: MyStocks前端团队
**反馈**: 请在项目Issues中报告无障碍性问题
