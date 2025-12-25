# 颜色系统

**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [设计系统](./README.md)

---

## 📋 目录

- [颜色原则](#颜色原则)
- [主题色](#主题色)
- [功能色](#功能色)
- [中性色](#中性色)
- [涨跌色](#涨跌色)
- [色彩无障碍](#色彩无障碍)
- [使用指南](#使用指南)

---

## 颜色原则

MyStocks 的颜色系统遵循以下原则：

1. **专业可信** - 使用沉稳的蓝色调，传达专业和稳定
2. **清晰易读** - 确保足够的色彩对比度，符合 WCAG AA 标准
3. **语义明确** - 颜色具有明确的语义，如红色表示上涨/危险
4. **一致性强** - 在整个应用中保持一致的色彩使用

---

## 主题色

### Primary Color (主色)

**用途**: 品牌色、主要操作、链接、激活状态

```scss
$--color-primary: #409EFF;

// 不同亮度的变体
$--color-primary-light-3: #79bbff; // 80% 亮度
$--color-primary-light-5: #a0cfff; // 60% 亮度
$--color-primary-light-7: #c6e2ff; // 40% 亮度
$--color-primary-light-8: #d9e8ff; // 20% 亮度
$--color-primary-light-9: #ecf5ff; // 10% 亮度
$--color-primary-dark-2: #337ecc;  // 80% 深度
```

**使用场景**:
- 主要按钮: `<el-button type="primary">`
- 激活状态的标签页
- 链接文字
- 进度条
- 加载状态

**示例**:
```vue
<template>
  <el-button type="primary">主要按钮</el-button>
  <el-link type="primary">链接文字</el-link>
  <div class="text-primary">主要文本</div>
</template>

<style lang="scss">
.text-primary {
  color: $--color-primary;
}
</style>
```

---

## 功能色

### Success Color (成功色)

**用途**: 成功提示、确认操作、通过状态

```scss
$--color-success: #67C23A;

// 变体
$--color-success-light: #e1f3d8;
$--color-success-lighter: #f0f9eb;
$--color-success-dark: #529b2e;
```

**使用场景**:
- 成功提示: `<el-tag type="success">`
- 状态指示: 已通过、已完成
- 确认操作
- **跌 (股市)**: 绿色表示股价下跌

**示例**:
```vue
<template>
  <el-tag type="success">已通过</el-tag>
  <el-result icon="success" title="操作成功" />
  <span class="fall">-2.35%</span> <!-- 股价下跌 -->
</template>

<style lang="scss">
.fall {
  color: $--color-success;
  font-weight: 600;
}
</style>
```

### Warning Color (警告色)

**用途**: 警告提示、注意事项、待处理

```scss
$--color-warning: #E6A23C;

// 变体
$--color-warning-light: #fdf6ec;
$--color-warning-lighter: #fef0e0;
$--color-warning-dark: #c77c10;
```

**使用场景**:
- 警告提示: `<el-alert type="warning">`
- 待处理状态
- 注意事项
- 风险提示

### Danger Color (危险色)

**用途**: 错误提示、删除操作、失败状态

```scss
$--color-danger: #F56C6C;

// 变体
$--color-danger-light: #fde2e2;
$--color-danger-lighter: #fef0f0;
$--color-danger-dark: #c93a3a;
```

**使用场景**:
- 错误提示: `<el-alert type="error">`
- 删除操作
- 失败状态
- **涨 (股市)**: 红色表示股价上涨

**示例**:
```vue
<template>
  <el-tag type="danger">已失败</el-tag>
  <el-button type="danger">删除</el-button>
  <span class="rise">+3.42%</span> <!-- 股价上涨 -->
</template>

<style lang="scss">
.rise {
  color: $--color-danger;
  font-weight: 600;
}
</style>
```

### Info Color (信息色)

**用途**: 信息提示、辅助说明、中性状态

```scss
$--color-info: #909399;

// 变体
$--color-info-light: #e9e9eb;
$--color-info-lighter: #f4f4f5;
$--color-info-dark: #73767a;
```

**使用场景**:
- 信息提示: `<el-alert type="info">`
- 辅助说明
- 禁用状态
- 次要文本

---

## 中性色

### Text Colors (文本颜色)

```scss
// 主要文本
$--color-text-primary: #303133;

// 常规文本
$--color-text-regular: #606266;

// 次要文本
$--color-text-secondary: #909399;

// 占位文本
$--color-text-placeholder: #C0C4CC;
```

**使用场景**:
```vue
<template>
  <div class="text-primary">主要标题</div>
  <div class="text-regular">常规内容</div>
  <div class="text-secondary">次要说明</div>
  <el-input placeholder="请输入..." />
</template>
```

### Background Colors (背景颜色)

```scss
// 白色背景
$--color-bg-white: #FFFFFF;

// 页面背景
$--color-bg-page: #F2F3F5;

// 遮罩层
$--color-bg-overlay: #000000;
```

### Border Colors (边框颜色)

```scss
// 基础边框
$--color-border-base: #DCDFE6;

// 轻量边框
$--color-border-light: #E4E7ED;

// 更轻边框
$--color-border-lighter: #EBEEF5;

// 更重边框
$--color-border-dark: #D4D7DE;
```

---

## 涨跌色

### 中国股市习惯

在中国股市中：
- 🔴 **红色** = **涨** (上涨)
- 🟢 **绿色** = **跌** (下跌)

```scss
// 涨 (红色)
$--color-stock-rise: #F56C6C;      // 使用 Danger 色值

// 跌 (绿色)
$--color-stock-fall: #67C23A;      // 使用 Success 色值

// 平 (灰色)
$--color-stock-flat: #909399;      // 使用 Info 色值
```

### 使用示例

```vue
<template>
  <!-- 涨跌幅显示 -->
  <div class="stock-price">
    <span class="price">12.50</span>
    <span :class="changeClass">+0.35 (+2.88%)</span>
  </div>

  <!-- K线图颜色 -->
  <el-option v-for="item in stockData" :key="item.symbol">
    <span>{{ item.name }}</span>
    <span :class="getChangeClass(item.change)">
      {{ item.changePercent }}%
    </span>
  </el-option>
</template>

<script setup lang="ts">
const props = defineProps<{
  change: number
}>()

const changeClass = computed(() => {
  if (props.change > 0) return 'stock-rise'
  if (props.change < 0) return 'stock-fall'
  return 'stock-flat'
})

const getChangeClass = (change: number) => {
  return change > 0 ? 'stock-rise' : change < 0 ? 'stock-fall' : 'stock-flat'
}
</script>

<style lang="scss" scoped>
.stock-rise {
  color: $--color-stock-rise;
}

.stock-fall {
  color: $--color-stock-fall;
}

.stock-flat {
  color: $--color-stock-flat;
}
</style>
```

### 图表颜色配置

```typescript
// ECharts 涨跌色配置
export const STOCK_COLORS = {
  rise: '#F56C6C',
  fall: '#67C23A',
  flat: '#909399',
}

// K线图配置
export const CANDLESTICK_COLORS = {
  // 阳线 (涨)
  positive: {
    itemStyle: {
      color: STOCK_COLORS.rise,
      color0: STOCK_COLORS.rise,
      borderColor: STOCK_COLORS.rise,
      borderColor0: STOCK_COLORS.rise,
    },
  },
  // 阴线 (跌)
  negative: {
    itemStyle: {
      color: STOCK_COLORS.fall,
      color0: STOCK_COLORS.fall,
      borderColor: STOCK_COLORS.fall,
      borderColor0: STOCK_COLORS.fall,
    },
  },
}
```

---

## 色彩无障碍

### WCAG 2.1 AA 标准

确保所有文本和背景的对比度至少达到:

- **正常文本** (< 18pt): 4.5:1
- **大文本** (≥ 18pt): 3:1
- **UI 组件**: 3:1

### 对比度检查

| 文字颜色 | 背景颜色 | 对比度 | 是否通过 |
|---------|---------|--------|---------|
| `#303133` | `#FFFFFF` | 12.6:1 | ✅ AA |
| `#606266` | `#FFFFFF` | 7.5:1 | ✅ AA |
| `#909399` | `#FFFFFF` | 4.0:1 | ✅ AA |
| `#FFFFFF` | `#409EFF` | 3.5:1 | ✅ AA |
| `#FFFFFF` | `#67C23A` | 3.1:1 | ✅ AA |
| `#FFFFFF` | `#F56C6C` | 3.1:1 | ✅ AA |

### 色盲友好

- **不仅依赖颜色传达信息**
- 使用图标 + 颜色组合
- 提供文字标签

**示例**:
```vue
<template>
  <!-- ❌ 不好: 仅依赖颜色 -->
  <span class="text-success">上涨</span>
  <span class="text-danger">下跌</span>

  <!-- ✅ 好: 颜色 + 图标 + 文字 -->
  <span class="text-success">
    <el-icon><Top /></el-icon>
    上涨
  </span>
  <span class="text-danger">
    <el-icon><Bottom /></el-icon>
    下跌
  </span>
</template>
```

---

## 使用指南

### 颜色选择决策树

```
需要使用颜色?
│
├─ 是品牌/主要操作?
│  └─ → Primary (#409EFF)
│
├─ 是功能反馈?
│  ├─ 成功/跌 → Success (#67C23A)
│  ├─ 警告 → Warning (#E6A23C)
│  ├─ 错误/涨 → Danger (#F56C6C)
│  └─ 信息 → Info (#909399)
│
├─ 是文本?
│  ├─ 标题/重要 → Text Primary (#303133)
│  ├─ 正文 → Text Regular (#606266)
│  ├─ 次要 → Text Secondary (#909399)
│  └─ 占位 → Text Placeholder (#C0C4CC)
│
└─ 是背景/边框?
   ├─ 页面背景 → Bg Page (#F2F3F5)
   ├─ 组件背景 → Bg White (#FFFFFF)
   └─ 边框 → Border Base (#DCDFE6)
```

### 颜色工具函数

```typescript
// utils/color.ts

/**
 * 获取涨跌颜色类名
 */
export function getStockChangeClass(change: number): string {
  if (change > 0) return 'stock-rise'
  if (change < 0) return 'stock-fall'
  return 'stock-flat'
}

/**
 * 获取涨跌颜色值
 */
export function getStockChangeColor(change: number): string {
  if (change > 0) return '#F56C6C' // Rise
  if (change < 0) return '#67C23A' // Fall
  return '#909399' // Flat
}

/**
 * 根据百分比获取颜色
 */
export function getColorByPercent(percent: number): string {
  if (percent >= 0) return '#F56C6C'
  return '#67C23A'
}
```

### SCSS Mixins

```scss
// mixins/color.scss

// 文本颜色
@mixin text-primary {
  color: $--color-text-primary;
}

@mixin text-secondary {
  color: $--color-text-secondary;
}

// 涨跌颜色
@mixin stock-rise {
  color: $--color-stock-rise;
}

@mixin stock-fall {
  color: $--color-stock-fall;
}

// 使用
.my-component {
  @include text-primary;

  &.rise {
    @include stock-rise;
  }

  &.fall {
    @include stock-fall;
  }
}
```

---

## 🎨 完整色板

### Element Plus 默认色板

```scss
// Primary (蓝色)
$--color-primary: #409EFF;
$--color-primary-light-3: #79bbff;
$--color-primary-light-5: #a0cfff;
$--color-primary-light-7: #c6e2ff;
$--color-primary-light-8: #d9e8ff;
$--color-primary-light-9: #ecf5ff;
$--color-primary-dark-2: #337ecc;

// Success (绿色)
$--color-success: #67C23A;
$--color-success-light: #e1f3d8;
$--color-success-lighter: #f0f9eb;
$--color-success-dark: #529b2e;

// Warning (橙色)
$--color-warning: #E6A23C;
$--color-warning-light: #fdf6ec;
$--color-warning-lighter: #fef0e0;
$--color-warning-dark: #c77c10;

// Danger (红色)
$--color-danger: #F56C6C;
$--color-danger-light: #fde2e2;
$--color-danger-lighter: #fef0f0;
$--color-danger-dark: #c93a3a;

// Info (灰色)
$--color-info: #909399;
$--color-info-light: #e9e9eb;
$--color-info-lighter: #f4f4f5;
$--color-info-dark: #73767a;
```

---

## 📚 参考资源

- [Element Plus 颜色系统](https://element-plus.org/en-US/guide/design.html#color-system)
- [Material Design Color System](https://material.io/design/color/)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/01-DESIGN_SYSTEM/color-system.md`
