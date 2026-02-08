# MyStocks 国际化实施指南

**版本**: 1.0
**创建日期**: 2026-01-13
**优先级**: P2 - 国际化支持

---

## 📋 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [useI18n Composable API](#usei18n-composable-api)
4. [翻译文件组织](#翻译文件组织)
5. [最佳实践](#最佳实践)
6. [测试清单](#测试清单)
7. [常见问题](#常见问题)

---

## 🚀 快速开始

### 安装

国际化依赖已安装：

```bash
npm install vue-i18n@9
```

### 基础用法

```vue
<script setup lang="ts">
import { useI18n } from '@/composables/useI18n'

const { t, locale, setLocale, formatCurrency, formatDate } = useI18n()
</script>

<template>
  <h1>{{ t('app.title') }}</h1>
  <p>{{ t('stock.price', { symbol: 'AAPL', price: 150.25 }) }}</p>
  <p>{{ formatCurrency(1234.56) }}</p>
  <p>{{ formatDate(new Date()) }}</p>
</template>
```

---

## 🎯 核心概念

### 支持的语言

| 语言代码 | 名称 | 国旗 | 状态 |
|---------|------|------|------|
| `zh-CN` | 简体中文 | 🇨🇳 | 默认 |
| `en-US` | English | 🇺🇸 | 可用 |

### 语言切换机制

1. **LocalStorage 持久化**: 用户选择保存在 `mystocks-locale` 键
2. **浏览器检测**: 首次访问时自动检测浏览器语言
3. **HTML lang 属性**: 自动更新 `<html lang="zh-CN">`
4. **降级策略**: 缺失翻译时回退到中文

---

## 📚 useI18n Composable API

### 核心 API

```typescript
const {
  t,              // 翻译函数
  locale,         // 当前语言（computed）
  localeInfo,     // 当前语言信息
  supportedLocales, // 支持的语言列表
  setLocale,      // 切换语言
  toggleLocale,   // 循环切换语言
} = useI18n()
```

#### 1. `t()` - 翻译函数

```vue
<script setup>
const { t } = useI18n()

// 简单翻译
const title = t('app.title')

// 带参数翻译
const message = t('stock.price', { symbol: 'AAPL', price: 150.25 })
// → "AAPL 价格: 150.25" (中文)
// → "AAPL Price: 150.25" (英文)

// 嵌套键
const errorMessage = t('validation.required')
// → "此项为必填项"
</script>
```

#### 2. `setLocale()` - 切换语言

```vue
<script setup>
const { setLocale } = useI18n()

const switchToEnglish = () => {
  setLocale('en-US')
  // 自动保存到 LocalStorage
  // 自动更新 HTML lang 属性
}
</script>
```

#### 3. `toggleLocale()` - 循环切换

```vue
<script setup>
const { toggleLocale } = useI18n()

// 在支持的语言间循环切换
const handleLanguageToggle = () => {
  toggleLocale()
  // zh-CN → en-US → zh-CN → ...
}
</script>
```

---

### 格式化 API

#### 4. `formatCurrency()` - 货币本地化

```vue
<script setup>
const { formatCurrency } = useI18n()

// 自动根据语言选择货币（中文→CNY，英文→USD）
const price = formatCurrency(1234.56)
// → "¥1,234.56" (中文)
// → "$1,234.56" (英文)

// 指定货币
const usdPrice = formatCurrency(1234.56, 'USD')
// → "$1,234.56"
</script>
```

#### 5. `formatNumber()` - 数字本地化

```vue
<script setup>
const { formatNumber } = useI18n()

const value = formatNumber(1234567.89)
// → "1,234,567.89" (英文)
// → "1,234,567.89" (中文)

// 指定小数位数
const precise = formatNumber(1234.5678, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4
})
// → "1,234.5678"
</script>
```

#### 6. `formatPercent()` - 百分比本地化

```vue
<script setup>
const { formatPercent } = useI18n()

const change = formatPercent(0.0523)
// → "5.23%" (英文)
// → "5.23%" (中文)

// 指定小数位数
const precise = formatPercent(0.05234, 3)
// → "5.234%"
</script>
```

#### 7. `formatDate()` - 日期本地化

```vue
<script setup>
const { formatDate } = useI18n()

const today = formatDate(new Date())
// → "2026-01-13" (英文，默认)
// → "2026-01-13" (中文，默认)

// 自定义格式
const fullDate = formatDate(new Date(), {
  year: 'numeric',
  month: 'long',
  day: 'numeric'
})
// → "January 13, 2026" (英文)
// → "2026年1月13日" (中文)
</script>
```

#### 8. `formatRelativeTime()` - 相对时间

```vue
<script setup>
const { formatRelativeTime } = useI18n()

const timeAgo = formatRelativeTime(new Date(Date.now() - 3600000))
// → "1 hour ago" (英文)
// → "1小时前" (中文)

const daysAgo = formatRelativeTime(new Date(Date.now() - 86400000 * 3))
// → "3 days ago" (英文)
// → "3天前" (中文)
</script>
```

#### 9. `formatChange()` - 涨跌幅格式化

```vue
<script setup>
const { formatChange } = useI18n()

const change = formatChange(0.0523)
// → "+5.23%"

const drop = formatChange(-0.0234)
// → "-2.34%"
</script>
```

#### 10. `formatCompactNumber()` - 紧凑数字

```vue
<script setup>
const { formatCompactNumber } = useI18n()

const marketCap = formatCompactNumber(1500000000)
// → "1.5B" (英文)
// → "1.5B" (中文)
</script>
```

#### 11. `formatBytes()` - 文件大小

```vue
<script setup>
const { formatBytes } = useI18n()

const fileSize = formatBytes(1536000)
// → "1.5 MB"
</script>
```

---

## 📂 翻译文件组织

### 文件结构

```
src/i18n/
├── index.ts              # i18n 配置
└── locales/
    ├── zh-CN.json        # 中文翻译
    └── en-US.json        # 英文翻译
```

### 翻译键命名规范

```json
{
  "模块名": {
    "功能名": {
      "具体项": "翻译内容"
    }
  }
}
```

**示例**:

```json
{
  "dashboard": {
    "title": "仪表盘",
    "overview": "概览",
    "market": "市场概况"
  },
  "stock": {
    "price": "价格",
    "change": "涨跌"
  }
}
```

### 参数化翻译

```json
{
  "stock": {
    "price": "股票价格: {symbol} - {price}"
  }
}
```

```vue
<template>
  {{ t('stock.price', { symbol: 'AAPL', price: 150.25 }) }}
  <!-- → "股票价格: AAPL - 150.25" -->
</template>
```

---

## 🎨 组件使用示例

### 1. 使用语言切换器组件

```vue
<script setup lang="ts">
import ArtDecoLanguageSwitcher from '@/components/artdeco/base/ArtDecoLanguageSwitcher.vue'
</script>

<template>
  <header>
    <h1>MyStocks</h1>
    <ArtDecoLanguageSwitcher />
  </header>
</template>
```

### 2. 在组件中使用翻译

```vue
<script setup lang="ts">
import { useI18n } from '@/composables/useI18n'

const { t, formatCurrency } = useI18n()

const stockData = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 150.25,
  change: 0.0523
}
</script>

<template>
  <div class="stock-card">
    <h2>{{ t('stock.name') }}</h2>
    <p>{{ stockData.name }} ({{ stockData.symbol }})</p>
    <p>{{ t('stock.price') }}: {{ formatCurrency(stockData.price) }}</p>
    <p>{{ t('stock.change') }}: {{ formatChange(stockData.change) }}</p>
  </div>
</template>
```

### 3. 表单验证翻译

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const stockCode = ref('')

const validateStockCode = () => {
  if (!stockCode.value) {
    return t('validation.required')
  }
  if (!/^\d{6}$/.test(stockCode.value)) {
    return t('validation.invalidStockCode')
  }
  return ''
}
</script>

<template>
  <form>
    <label>{{ t('stock.symbol') }}</label>
    <input v-model="stockCode" />
    <span v-if="error" class="error">{{ error }}</span>
  </form>
</template>
```

---

## 🏆 最佳实践

### 1. 翻译键命名

✅ **推荐**:

```json
{
  "dashboard": {
    "title": "仪表盘",
    "marketOverview": "市场概况"
  }
}
```

❌ **不推荐**:

```json
{
  "dashboardTitle": "仪表盘",
  "market_overview_text": "市场概况"
}
```

### 2. 参数化翻译

✅ **推荐**:

```json
{
  "welcome": "欢迎，{username}！",
  "stockInfo": "{symbol} 价格: {price}"
}
```

```vue
{{ t('welcome', { username: '张三' }) }}
{{ t('stockInfo', { symbol: 'AAPL', price: 150 }) }}
```

❌ **不推荐**:

```json
{
  "welcomeUser": "欢迎，用户！"
}
```

```vue
{{ t('welcomeUser').replace('用户', username) }}  // 避免字符串操作
```

### 3. 日期/数字格式化

✅ **推荐**:

```vue
<script setup>
const { formatDate, formatCurrency } = useI18n()
</script>

<template>
  <p>{{ formatDate(new Date()) }}</p>
  <p>{{ formatCurrency(1234.56) }}</p>
</template>
```

❌ **不推荐**:

```vue
<template>
  <p>{{ new Date().toLocaleDateString() }}</p>
  <p>${{ 1234.56.toFixed(2) }}</p>
</template>
```

### 4. 避免硬编码文本

✅ **推荐**:

```vue
<template>
  <button>{{ t('common.submit') }}</button>
</template>
```

❌ **不推荐**:

```vue
<template>
  <button>提交</button>  <!-- 硬编码中文 -->
</template>
```

### 5. 动态内容翻译

✅ **推荐**:

```json
{
  "itemCount": "{count} 项",
  "itemCount_zero": "0 项",
  "itemCount_one": "1 项",
  "itemCount_other": "{count} 项"
}
```

---

## ✅ 测试清单

### 功能测试

- [ ] 语言切换器显示正确
- [ ] 点击切换语言后内容立即更新
- [ ] LocalStorage 正确保存语言偏好
- [ ] 刷新页面后语言偏好保持
- [ ] 所有翻译键都有对应翻译
- [ ] 参数化翻译正确替换参数

### 格式化测试

- [ ] 货币格式化（中文→¥，英文→$）
- [ ] 数字格式化（千分位分隔符）
- [ ] 百分比格式化（符号和精度）
- [ ] 日期格式化（语言相关格式）
- [ ] 相对时间格式化

### 兼容性测试

- [ ] Chrome 语言检测正确
- [ ] Firefox 语言检测正确
- [ ] Safari 语言检测正确
- [ ] Edge 语言检测正确

### 无障碍测试

- [ ] HTML lang 属性正确更新
- [ ] 屏幕阅读器识别语言变化
- [ ] ARIA 标签包含翻译内容

---

## ❓ 常见问题

### Q1: 如何添加新语言？

**A**:

1. 创建翻译文件：`src/i18n/locales/ja-JP.json`
2. 更新 `src/i18n/index.ts`:

```typescript
import jaJP from './locales/ja-JP.json'

export const SUPPORTED_LOCALES = [
  { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'ja-JP', name: '日本語', flag: '🇯🇵' }  // 新增
]

messages: {
  'zh-CN': zhCN,
  'en-US': enUS,
  'ja-JP': jaJP  // 新增
}
```

### Q2: 翻译键缺失时会发生什么？

**A**:
- 开发环境：控制台警告 `Missing translation: xxx`
- 显示翻译键本身作为回退
- 不会报错或中断应用

### Q3: 如何翻译复数形式？

**A**:

```json
{
  "items": "无项目 | 1 项 | {count} 项"
}
```

```vue
<template>
  {{ $tn('items', itemCount, { count: itemCount }) }}
</template>
```

### Q4: 如何翻译 Element Plus 组件？

**A**:

```vue
<script setup>
import { ElConfigProvider } from 'element-plus'
import { useI18n } from '@/composables/useI18n'

const { locale } = useI18n()

// Element Plus 语言映射
const elementLocaleMap = {
  'zh-CN': zhCn,
  'en-US': en
}
</script>

<template>
  <el-config-provider :locale="elementLocaleMap[locale]">
    <App />
  </el-config-provider>
</template>
```

### Q5: 如何在路由中使用翻译？

**A**:

```typescript
// router/index.ts
{
  path: '/dashboard',
  name: 'dashboard',
  meta: {
    title: 'nav.dashboard'  // 翻译键
  }
}
```

```vue
<script setup>
import { useI18n } from '@/composables/useI18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()

// 在 watch 中更新页面标题
watch(() => route.meta.title, (titleKey) => {
  if (titleKey) {
    document.title = t(titleKey as string)
  }
}, { immediate: true })
</script>
```

---

## 📖 参考资料

- [Vue I18n 官方文档](https://vue-i18n.intlify.dev/)
- [Intl API - MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- [Unicode CLDR (本地化数据)](https://cldr.unicode.org/)
- [WCAG 2.1 - 语言声明](https://www.w3.org/WAI/WCAG21/Techniques/html/H57.html)

---

## 🔄 更新日志

- **v1.0** (2026-01-13): 初始版本
  - 安装并配置 vue-i18n
  - 创建中英文翻译文件
  - 实现 useI18n composable
  - 创建语言切换器组件
  - 提供完整 API 文档和示例

---

**维护者**: MyStocks前端团队
**反馈**: 请在项目 Issues 中报告国际化问题
