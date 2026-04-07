# 字体系统

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [设计系统](./README.md)

---

## 📋 目录

- [字体族](#字体族)
- [字号系统](#字号系统)
- [字重](#字重)
- [行高与字间距](#行高与字间距)
- [文本样式](#文本样式)
- [响应式字体](#响应式字体)
- [使用指南](#使用指南)

---

## 字体族

### 中文字体

```scss
// 中文字体栈
$font-family-chinese: "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'WenQuanYi Micro Hei', sans-serif";

// 数字字体 (等宽)
$font-family-number: "'SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', 'Droid Sans Mono', 'Source Code Pro', monospace";
```

### 英文字体

```scss
// 英文字体栈
$font-family-english: "'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif";

// 代码字体
$font-family-code: "'Fira Code', 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace";
```

### Element Plus 默认字体

```scss
// Element Plus 使用
$--font-family: (
  '': "'Inter', 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif",
);

// 覆盖 Element Plus 字体
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $font-family: $--font-family,
);
```

---

## 字号系统

### 字号量表

| 级别 | 字号 | 行高 | 用途 | 类名 |
|-----|------|------|------|------|
| **Display** | 36px | 1.2 | 大标题 | `.text-display` |
| **H1** | 24px | 1.5 | 页面标题 | `.text-h1` |
| **H2** | 20px | 1.5 | 区块标题 | `.text-h2` |
| **H3** | 18px | 1.5 | 卡片标题 | `.text-h3` |
| **H4** | 16px | 1.5 | 小标题 | `.text-h4` |
| **Body** | 14px | 1.5 | 正文内容 | `.text-body` |
| **Small** | 12px | 1.5 | 辅助文本 | `.text-small` |
| **Tiny** | 10px | 1.5 | 标签/徽章 | `.text-tiny` |

### SCSS 变量

```scss
// 字号变量
$font-size-display: 36px;
$font-size-h1: 24px;
$font-size-h2: 20px;
$font-size-h3: 18px;
$font-size-h4: 16px;
$font-size-body: 14px;
$font-size-small: 12px;
$font-size-tiny: 10px;

// 行高变量
$line-height-tight: 1.2;
$line-height-normal: 1.5;
$line-height-loose: 1.8;
```

### 使用示例

```vue
<template>
  <!-- 标题层级 -->
  <h1 class="text-h1">页面标题</h1>
  <h2 class="text-h2">区块标题</h2>
  <h3 class="text-h3">卡片标题</h3>

  <!-- 文本内容 -->
  <p class="text-body">正文内容</p>
  <span class="text-small">辅助说明</span>
  <span class="text-tiny">标签文字</span>

  <!-- 金融数字 (特殊字体) -->
  <div class="stock-price">12.50</div>
</template>

<style lang="scss" scoped>
.stock-price {
  font-family: $font-family-number;
  font-size: $font-size-h3;
  font-weight: 600;
}
</style>
```

---

## 字重

### 字重等级

| 等级 | 数值 | 用途 |
|-----|------|------|
| **Light** | 300 | 轻标题 (很少使用) |
| **Regular** | 400 | 正文、常规文本 |
| **Medium** | 500 | 强调文本、小标题 |
| **Semibold** | 600 | 重要标题、按钮 |
| **Bold** | 700 | 大标题、强调 |

### SCSS 变量

```scss
// 字重变量
$font-weight-light: 300;
$font-weight-regular: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;
```

### 使用示例

```vue
<template>
  <p class="font-regular">常规文本</p>
  <p class="font-medium">中等字重</p>
  <p class="font-semibold">半粗体</p>
  <p class="font-bold">粗体</p>
</template>

<style lang="scss" scoped>
.font-regular {
  font-weight: $font-weight-regular;
}

.font-medium {
  font-weight: $font-weight-medium;
}

.font-semibold {
  font-weight: $font-weight-semibold;
}

.font-bold {
  font-weight: $font-weight-bold;
}
</style>
```

---

## 行高与字间距

### 行高 (Line Height)

| 场景 | 行高值 | 用途 |
|-----|--------|------|
| **Tight** | 1.2 | 大标题、数字 |
| **Normal** | 1.5 | 正文、表格 |
| **Loose** | 1.8 | 长段落阅读 |

### 字间距 (Letter Spacing)

| 场景 | 字间距 | 用途 |
|-----|--------|------|
| **Tight** | -0.02em | 大标题 |
| **Normal** | 0 | 正文、标题 |
| **Wide** | 0.1em | 英文大写、标签 |

### SCSS Mixins

```scss
// 行高 Mixins
@mixin line-height-tight {
  line-height: $line-height-tight;
}

@mixin line-height-normal {
  line-height: $line-height-normal;
}

@mixin line-height-loose {
  line-height: $line-height-loose;
}

// 使用
.page-title {
  font-size: $font-size-h1;
  @include line-height-tight;
}

.body-text {
  font-size: $font-size-body;
  @include line-height-normal;
}
```

---

## 文本样式

### 通用文本类

```scss
// 主文本
.text-primary {
  color: $--color-text-primary;
  font-size: $font-size-body;
  font-weight: $font-weight-regular;
}

// 次要文本
.text-secondary {
  color: $--color-text-secondary;
  font-size: $font-size-small;
}

// 占位文本
.text-placeholder {
  color: $--color-text-placeholder;
  font-size: $font-size-body;
}

// 强调文本
.text-emphasis {
  color: $--color-text-primary;
  font-weight: $font-weight-semibold;
}

// 链接文本
.text-link {
  color: $--color-primary;
  cursor: pointer;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}
```

### 金融数字样式

```scss
// 股票价格
.stock-price {
  font-family: $font-family-number;
  font-size: $font-size-h3;
  font-weight: $font-weight-semibold;
  font-variant-numeric: tabular-nums; // 等宽数字
}

// 涨跌幅
.stock-change {
  font-family: $font-family-number;
  font-size: $font-size-body;
  font-weight: $font-weight-medium;
  font-variant-numeric: tabular-nums;

  &.rise {
    color: $--color-stock-rise;
  }

  &.fall {
    color: $--color-stock-fall;
  }
}

// 百分比
.percent {
  font-family: $font-family-number;
  font-size: $font-size-body;
  font-variant-numeric: tabular-nums;
}

// 千分位格式化
.number-with-comma {
  font-family: $font-family-number;
  font-variant-numeric: tabular-nums;
}
```

### 代码样式

```scss
// 行内代码
code {
  font-family: $font-family-code;
  font-size: 0.9em;
  padding: 2px 6px;
  background-color: $--color-bg-page;
  border-radius: $--border-radius-base;
  color: $--color-danger;
}

// 代码块
pre {
  font-family: $font-family-code;
  font-size: $font-size-small;
  line-height: $line-height-normal;
  padding: $spacing-md;
  background-color: $--color-bg-page;
  border-radius: $--border-radius-base;
  overflow-x: auto;
}
```

---

## 响应式字体

### 移动端字体调整

```scss
// 移动端字体缩放
@mixin responsive-font($desktop-size, $mobile-size) {
  font-size: $desktop-size;

  @media (max-width: $breakpoint-md) {
    font-size: $mobile-size;
  }
}

// 使用
.page-title {
  @include responsive-font(24px, 20px);
}
```

### 流式字体 (Fluid Typography)

```scss
// 流式字体: 随视口宽度平滑缩放
@mixin fluid-font($min-size, $max-size, $min-vw: 320px, $max-vw: 1200px) {
  font-size: $min-size;

  @media (min-width: $min-vw) and (max-width: $max-vw) {
    font-size: calc(
      #{$min-size} + #{strip-unit($max-size - $min-size)} *
      ((100vw - #{$min-vw}) / #{strip-unit($max-vw - $min-vw)})
    );
  }

  @media (min-width: $max-vw) {
    font-size: $max-size;
  }
}

// 使用: 最小 14px, 最大 18px, 在 320px-1200px 之间平滑缩放
.body-text {
  @include fluid-font(14px, 18px, 320px, 1200px);
}
```

---

## 使用指南

### 文本层级决策树

```
需要设置文本?
│
├─ 是标题?
│  ├─ 页面主标题 → H1 (24px, Semibold)
│  ├─ 区块标题 → H2 (20px, Semibold)
│  ├─ 卡片标题 → H3 (18px, Medium)
│  └─ 小标题 → H4 (16px, Medium)
│
├─ 是正文?
│  ├─ 主要内容 → Body (14px, Regular)
│  ├─ 辅助说明 → Small (12px, Regular)
│  └─ 标签/徽章 → Tiny (10px, Regular)
│
├─ 是金融数字?
│  ├─ 价格 → Number Font, H3, Semibold
│  ├─ 涨跌幅 → Number Font, Body, Medium
│  └─ 百分比 → Number Font, Body, Regular
│
└─ 是代码?
   ├─ 行内代码 → Code Font, 0.9em
   └─ 代码块 → Code Font, Small
```

### 文本截断

```scss
// 单行截断
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 多行截断 (2行)
.text-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

// 多行截断 (3行)
.text-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

### 文本对齐

```scss
// 左对齐 (默认)
.text-left {
  text-align: left;
}

// 居中
.text-center {
  text-align: center;
}

// 右对齐
.text-right {
  text-align: right;
}

// 两端对齐
.text-justify {
  text-align: justify;
}

// 金融数字右对齐
.text-number-right {
  text-align: right;
  font-family: $font-family-number;
  font-variant-numeric: tabular-nums;
}
```

---

## 🎨 完整示例

### 股票信息卡片

```vue
<template>
  <el-card class="stock-card">
    <!-- 股票名称 -->
    <div class="stock-name">浦发银行 (600000)</div>

    <!-- 当前价格 -->
    <div class="stock-price">12.50</div>

    <!-- 涨跌幅 -->
    <div class="stock-change rise">+0.35 (+2.88%)</div>

    <!-- 成交量 -->
    <div class="stock-volume">
      <span class="label">成交量:</span>
      <span class="value">12,345,678</span>
    </div>
  </el-card>
</template>

<style lang="scss" scoped>
.stock-card {
  padding: $spacing-md;
}

.stock-name {
  font-size: $font-size-h4;
  font-weight: $font-weight-medium;
  color: $--color-text-primary;
  margin-bottom: $spacing-sm;
}

.stock-price {
  font-family: $font-family-number;
  font-size: 36px;
  font-weight: $font-weight-bold;
  color: $--color-text-primary;
  line-height: $line-height-tight;
}

.stock-change {
  font-family: $font-family-number;
  font-size: $font-size-h3;
  font-weight: $font-weight-semibold;
  margin-top: $spacing-xs;

  &.rise {
    color: $--color-stock-rise;
  }

  &.fall {
    color: $--color-stock-fall;
  }
}

.stock-volume {
  margin-top: $spacing-sm;
  font-size: $font-size-small;

  .label {
    color: $--color-text-secondary;
  }

  .value {
    font-family: $font-family-number;
    font-variant-numeric: tabular-nums;
    color: $--color-text-primary;
  }
}
</style>
```

---

## 📚 参考资源

- [Element Plus Typography](https://element-plus.org/en-US/component/typography.html)
- [Material Design Typography](https://material.io/design/typography/)
- [Web Typography: Designing Systems](https://typescale.com/)
- [Fluid Typography](https://moderncss.dev/linearly-scale-font-size-with-css-clamp/)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/01-DESIGN_SYSTEM/typography.md`
