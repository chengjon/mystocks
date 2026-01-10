# MyStocks 统一视觉规范 (Unified Visual Specification)

**版本**: v2.0
**生成时间**: 2026-01-08
**适用范围**: 所有31个前端页面
**技术栈**: Vue 3 + Element Plus + SCSS
**设计理念**: Bloomberg Terminal专业金融系统风格

---

## 📐 设计系统核心原则

### 基于用户需求的优化优先级

1. **文字对齐** (P0) - 最影响视觉体验
2. **卡片比例** (P1) - 视觉一致性
3. **组件间距** (P2) - 层次感和紧凑度

### 8px网格系统

**基础单位**: 8px
**所有间距必须是8的倍数**: 4px(0.5x), 8px(1x), 16px(2x), 24px(3x), 32px(4x), 48px(6x)

**禁止使用的间距**: 7px, 10px, 12px, 15px, 20px, 30px, 35px, 40px, 80px

---

## 🎴 1. 卡片规范 (Card Specification)

### 1.1 卡片类型定义

根据功能和内容密度，定义4种标准卡片类型：

#### A. 数据展示卡片 (Data Display Card)

**用途**: 显示统计数据、关键指标、图表
**典型页面**: Dashboard统计卡片、Market行情卡片、Portfolio资产卡片

```scss
// ============ 数据展示卡片 ============
.card-data {
  // 尺寸比例 (适配1920x1080)
  width: 100%;
  min-height: 120px;  // 宽高比约 4:1 到 5:1
  aspect-ratio: 4 / 1;

  // 内边距 (紧凑但舒适)
  padding: var(--spacing-md);  // 16px (8px × 2)

  // 圆角 (统一)
  border-radius: var(--radius-lg);  // 8px

  // 边框 (精致)
  border: 1px solid var(--border-base);  // #3A3E45

  // 阴影 (层次感)
  box-shadow: var(--shadow-1);  // 0 2px 8px rgba(0, 0, 0, 0.3)

  // 背景
  background: var(--bg-card);  // #232936

  // 悬停效果
  transition: all var(--transition-base);  // 250ms ease-in-out

  &:hover {
    border-color: var(--border-light);  // #4A4E55
    box-shadow: var(--shadow-2);  // 0 4px 16px rgba(0, 0, 0, 0.4)
  }
}

// 响应式适配 (1366x768)
@media (max-width: 1366px) {
  .card-data {
    min-height: 100px;  // 略小
    padding: var(--spacing-sm);  // 12px
  }
}
```

#### B. 内容容器卡片 (Content Container Card)

**用途**: 包含复杂内容的卡片（表格、表单、图表）
**典型页面**: Analysis技术分析、StockDetail股票详情、Backtest回测结果

```scss
// ============ 内容容器卡片 ============
.card-content {
  // 尺寸比例 (灵活高度)
  width: 100%;
  min-height: 300px;  // 保证内容可读

  // 内边距 (宽松，容纳复杂内容)
  padding: var(--spacing-lg);  // 24px (8px × 3)

  // 圆角 (统一)
  border-radius: var(--radius-lg);  // 8px

  // 边框 (精致)
  border: 1px solid var(--border-base);

  // 阴影 (层次感)
  box-shadow: var(--shadow-1);

  // 背景
  background: var(--bg-card);

  // 头部区域
  .card-header {
    padding: 0 0 var(--spacing-md) 0;  // 0 0 16px 0
    margin: 0 0 var(--spacing-md) 0;
    border-bottom: 1px solid var(--border-base);

    h2, h3 {
      margin: 0;
      color: var(--text-primary);
      font-size: var(--font-size-lg);  // 18px
      font-weight: var(--font-weight-semibold);  // 600
    }
  }

  // 内容区域
  .card-body {
    padding: var(--spacing-md) 0;  // 16px 0
    color: var(--text-secondary);
  }
}

// 响应式适配
@media (max-width: 1366px) {
  .card-content {
    padding: var(--spacing-md);  // 16px
    min-height: 250px;
  }
}
```

#### C. 操作卡片 (Action Card)

**用途**: 触发操作、快捷入口
**典型页面**: Settings设置项、Strategy策略操作、Task任务卡片

```scss
// ============ 操作卡片 ============
.card-action {
  // 尺寸比例 (点击区域足够大)
  width: 100%;
  min-height: 80px;
  aspect-ratio: 6 / 1;

  // 内边距 (紧凑)
  padding: var(--spacing-sm) var(--spacing-md);  // 8px 16px

  // 圆角 (统一)
  border-radius: var(--radius-md);  // 4px (略小，强调操作感)

  // 边框 (可点击感)
  border: 1px solid var(--border-base);

  // 阴影 (轻微)
  box-shadow: var(--shadow-1);

  // 背景
  background: var(--bg-card);

  // 交互状态
  cursor: pointer;
  transition: all var(--transition-fast);  // 150ms

  &:hover {
    border-color: var(--color-primary);  // 蓝色边框
    box-shadow: var(--shadow-glow);  // 0 0 20px rgba(41, 121, 255, 0.4)
  }

  &:active {
    transform: translateY(1px);
  }
}
```

#### D. 模态对话框卡片 (Modal Card)

**用途**: 弹窗、对话框
**典型页面**: 所有页面的弹窗

```scss
// ============ 模态对话框卡片 ============
.card-modal {
  // 尺寸 (限制最大宽度)
  width: 90%;
  max-width: 800px;
  max-height: 90vh;

  // 内边距
  padding: 0;  // 使用header/body分离的padding

  // 圆角 (略大)
  border-radius: var(--radius-xl);  // 12px

  // 边框 (强调)
  border: 1px solid var(--border-light);

  // 阴影 (深度)
  box-shadow: var(--shadow-3);  // 0 8px 32px rgba(0, 0, 0, 0.5)

  // 背景
  background: var(--bg-card);

  // 头部
  .modal-header {
    padding: var(--spacing-lg);  // 24px
    border-bottom: 1px solid var(--border-base);

    display: flex;
    justify-content: space-between;
    align-items: center;

    .modal-title {
      margin: 0;
      color: var(--text-primary);
      font-size: var(--font-size-xl);  // 20px
      font-weight: var(--font-weight-semibold);  // 600
    }
  }

  // 内容区
  .modal-body {
    padding: var(--spacing-lg);  // 24px
    max-height: 60vh;
    overflow-y: auto;
  }

  // 底部操作区
  .modal-footer {
    padding: var(--spacing-md) var(--spacing-lg);  // 16px 24px
    border-top: 1px solid var(--border-base);
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-sm);  // 8px
  }
}
```

### 1.2 Element Plus卡片覆盖

**全局覆盖** - 在`theme-apply.scss`中添加：

```scss
// ==========================================
// Element Plus Card 统一规范
// ==========================================

// 基础卡片 (默认使用数据展示卡片规范)
.el-card {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-base) !important;
  border-radius: var(--radius-lg) !important;  // 8px统一
  box-shadow: var(--shadow-1) !important;

  // 内边距统一为 16px (数据展示卡片标准)
  .el-card__body {
    padding: var(--spacing-md) !important;  // 16px
  }

  // 悬停效果
  &:hover {
    border-color: var(--border-light) !important;
    box-shadow: var(--shadow-2) !important;
  }
}

// 卡片头部
.el-card__header {
  background-color: var(--bg-secondary) !important;
  border-bottom: 1px solid var(--border-base) !important;
  padding: var(--spacing-md) !important;  // 16px (统一上下左右)

  color: var(--text-primary) !important;
  font-weight: var(--font-weight-semibold) !important;
  font-size: var(--font-size-lg) !important;  // 18px
}

// 可悬停卡片
.el-card.is-hoverable {
  cursor: pointer;
  transition: all var(--transition-base);
}
```

---

## 🔘 2. 按钮规范 (Button Specification)

### 2.1 按钮尺寸标准

**核心原则**: 所有按钮文字必须**水平居中 + 垂直居中**

#### A. 主按钮 (Primary Button)

**用途**: 主要操作、提交、确认
**尺寸**: 标准

```scss
// ============ 主按钮 ============
.btn-primary {
  // 尺寸
  height: 40px;
  min-width: 120px;

  // 内边距 (上下左右相等，确保垂直居中)
  padding: 0 var(--spacing-lg);  // 0 24px

  // 文字对齐 (核心!)
  display: inline-flex;
  align-items: center;  // 垂直居中
  justify-content: center;  // 水平居中
  text-align: center;  // 文字居中
  line-height: 1;  // 消除行高影响

  // 圆角
  border-radius: var(--radius-md);  // 4px

  // 字体
  font-size: var(--font-size-base);  // 14px
  font-weight: var(--font-weight-medium);  // 500

  // 颜色
  background: var(--color-primary);  // #2979FF
  color: var(--text-primary);  // #FFFFFF
  border: none;

  // 阴影
  box-shadow: 0 2px 4px rgba(41, 121, 255, 0.3);

  // 过渡
  transition: all var(--transition-base);

  // 悬停
  &:hover {
    background: var(--color-primary-hover);  // #5393FF
    box-shadow: var(--shadow-glow);  // 发光效果
    transform: translateY(-1px);
  }

  // 激活
  &:active {
    background: var(--color-primary-active);  // #1E5CBF
    transform: translateY(0);
  }

  // 图标+文字组合
  .btn-icon + span,
  span + .btn-icon {
    margin-left: var(--spacing-sm);  // 8px
  }
}
```

#### B. 次要按钮 (Secondary Button)

**用途**: 次要操作、取消、返回

```scss
// ============ 次要按钮 ============
.btn-secondary {
  // 尺寸
  height: 40px;
  min-width: 100px;

  // 内边距 (垂直居中)
  padding: 0 var(--spacing-md);  // 0 16px

  // 文字对齐 (核心!)
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 1;

  // 圆角
  border-radius: var(--radius-md);  // 4px

  // 字体
  font-size: var(--font-size-base);  // 14px
  font-weight: var(--font-weight-normal);  // 400

  // 颜色 (幽灵按钮)
  background: transparent;
  color: var(--text-secondary);  // #B0B3B8
  border: 1px solid var(--border-base);  // #3A3E45

  // 过渡
  transition: all var(--transition-base);

  // 悬停
  &:hover {
    border-color: var(--border-light);  // #4A4E55
    color: var(--text-primary);  // #FFFFFF
    background: var(--bg-hover);  // #2D3446
  }

  // 激活
  &:active {
    background: var(--bg-active);  // #343A4D
  }
}
```

#### C. 小按钮 (Small Button)

**用途**: 紧凑空间、表格内操作

```scss
// ============ 小按钮 ============
.btn-small {
  // 尺寸
  height: 32px;
  min-width: 80px;

  // 内边距 (垂直居中)
  padding: 0 var(--spacing-sm);  // 0 8px

  // 文字对齐 (核心!)
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 1;

  // 圆角
  border-radius: var(--radius-sm);  // 2px

  // 字体
  font-size: var(--font-size-sm);  // 13px
  font-weight: var(--font-weight-normal);  // 400

  // 颜色
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-base);

  // 过渡
  transition: all var(--transition-fast);

  // 悬停
  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}
```

#### D. 图标按钮 (Icon Button)

**用途**: 纯图标操作（刷新、编辑、删除）

```scss
// ============ 图标按钮 ============
.btn-icon {
  // 尺寸 (正方形)
  width: 36px;
  height: 36px;

  // 内边距 (确保图标居中)
  padding: 0;

  // 图标居中 (核心!)
  display: inline-flex;
  align-items: center;
  justify-content: center;

  // 圆形
  border-radius: var(--radius-round);  // 50%

  // 颜色
  background: transparent;
  border: 1px solid var(--border-base);
  color: var(--text-secondary);

  // 过渡
  transition: all var(--transition-fast);

  // 悬停
  &:hover {
    background: var(--bg-hover);
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  // SVG图标尺寸
  svg {
    width: 18px;
    height: 18px;
  }
}
```

### 2.2 Element Plus按钮全局覆盖

**在`theme-apply.scss`中添加**：

```scss
// ==========================================
// Element Plus Button 统一规范
// ==========================================

// 默认按钮 (使用次要按钮规范)
.el-button {
  // 尺寸统一
  height: 40px;

  // 内边距 (垂直居中 - 核心!)
  padding: 0 var(--spacing-md) !important;  // 0 16px

  // 文字对齐 (核心!)
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  line-height: 1 !important;

  // 圆角统一
  border-radius: var(--radius-md) !important;  // 4px

  // 字体统一
  font-size: var(--font-size-base) !important;  // 14px
  font-weight: var(--font-weight-normal) !important;  // 400

  // 过渡
  transition: all var(--transition-base) !important;

  // 图标+文字间距
  .el-icon + span {
    margin-left: var(--spacing-sm) !important;  // 8px
  }
}

// 小按钮
.el-button--small {
  height: 32px !important;
  padding: 0 var(--spacing-sm) !important;  // 0 8px
  font-size: var(--font-size-sm) !important;  // 13px
}

// 大按钮
.el-button--large {
  height: 48px !important;
  padding: 0 var(--spacing-xl) !important;  // 0 32px
  font-size: var(--font-size-md) !important;  // 16px
}

// 主按钮
.el-button--primary {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
  color: var(--text-primary) !important;

  &:hover {
    background-color: var(--color-primary-hover) !important;
    border-color: var(--color-primary-hover) !important;
  }

  &:active {
    background-color: var(--color-primary-active) !important;
  }
}

// 成功按钮
.el-button--success {
  background-color: var(--color-success) !important;
  border-color: var(--color-success) !important;

  &:hover {
    opacity: 0.85 !important;
  }
}

// 警告按钮
.el-button--warning {
  background-color: var(--color-warning) !important;
  border-color: var(--color-warning) !important;

  &:hover {
    opacity: 0.85 !important;
  }
}

// 危险按钮
.el-button--danger {
  background-color: var(--color-danger) !important;
  border-color: var(--color-danger) !important;

  &:hover {
    opacity: 0.85 !important;
  }
}

// 文字按钮 (幽灵按钮)
.el-button.is-plain {
  background: transparent !important;

  &:hover {
    background: var(--bg-hover) !important;
  }
}

// 圆形按钮
.el-button.is-circle {
  width: 40px !important;
  height: 40px !important;
  padding: 0 !important;
  border-radius: var(--radius-round) !important;  // 50%
}

// 按钮组内的按钮间距
.el-button-group {
  .el-button {
    margin: 0 !important;

    &:not(:first-child):not(:last-child) {
      border-radius: 0 !important;
    }

    &:first-child {
      border-top-right-radius: 0 !important;
      border-bottom-right-radius: 0 !important;
    }

    &:last-child {
      border-top-left-radius: 0 !important;
      border-bottom-left-radius: 0 !important;
    }
  }
}
```

---

## 📏 3. 间距规范 (Spacing Specification)

### 3.1 8px网格系统

**核心原则**: 所有间距必须是8的倍数

| 间距级别 | CSS变量 | 值 | 用途 |
|---------|---------|---|------|
| 0.5x | `var(--spacing-xs)` | 4px | 紧凑组件内间距 |
| 1x | `var(--spacing-sm)` | 8px | 组件内间距、小元素间距 |
| 2x | `var(--spacing-md)` | 16px | 组件间间距、表单间距 |
| 3x | `var(--spacing-lg)` | 24px | 模块内大间距 |
| 4x | `var(--spacing-xl)` | 32px | 模块间间距 |
| 6x | `var(--spacing-xxl)` | 48px | 页面级间距 |

### 3.2 间距应用层级

#### 级别1: 组件内间距 (Internal Component Spacing)

**范围**: 8px / 16px
**用途**: 同一组件内部元素间距

```scss
// 示例: 卡片内部元素的间距
.card-data {
  // 标题与内容之间
  .stat-title {
    margin-bottom: var(--spacing-sm);  // 8px
  }

  // 多个数据点之间
  .stat-item + .stat-item {
    margin-left: var(--spacing-sm);  // 8px
  }
}

// 示例: 表单控件间距
.form-group {
  .form-item {
    margin-bottom: var(--spacing-md);  // 16px (表单项之间)
  }

  .form-label {
    margin-bottom: var(--spacing-sm);  // 8px (标签与输入框)
  }
}
```

#### 级别2: 组件间间距 (Component-to-Component Spacing)

**范围**: 16px / 24px
**用途**: 独立组件之间的间距

```scss
// 示例: 卡片网格间距
.stats-grid {
  display: grid;
  gap: var(--spacing-md);  // 16px (标准卡片间距)

  // 或使用flex布局
  display: flex;
  flex-wrap: wrap;

  .stat-card {
    margin-right: var(--spacing-md);  // 16px
    margin-bottom: var(--spacing-md);  // 16px
  }
}

// 示例: 表格与分页器间距
.table-section {
  .el-table {
    margin-bottom: var(--spacing-lg);  // 24px
  }

  .el-pagination {
    // 分页器紧接表格
  }
}
```

#### 级别3: 模块间间距 (Module-to-Module Spacing)

**范围**: 32px / 48px
**用途**: 页面主要模块之间的间距

```scss
// 示例: 页面主要区域间距
.page-container {
  // 页面头部与内容之间
  .page-header + .content-section {
    margin-top: var(--spacing-xl);  // 32px
  }

  // 主要模块之间
  .module-section + .module-section {
    margin-top: var(--spacing-xxl);  // 48px
  }
}

// 示例: Dashboard布局
.dashboard {
  .stats-grid {
    margin-bottom: var(--spacing-xl);  // 32px (统计区与主内容区)
  }

  .main-grid {
    // 主内容区
  }

  .bottom-section {
    margin-top: var(--spacing-xxl);  // 48px (主内容与底部)
  }
}
```

### 3.3 特殊场景间距

#### 页面容器内边距 (Page Container Padding)

**标准**: 24px (8px × 3)

```scss
.page-container {
  padding: var(--spacing-lg);  // 24px

  // 1366x768适配
  @media (max-width: 1366px) {
    padding: var(--spacing-md);  // 16px
  }
}
```

#### 卡片内边距 (Card Padding)

**数据展示卡片**: 16px (8px × 2)
**内容容器卡片**: 24px (8px × 3)

```scss
.card-data {
  padding: var(--spacing-md);  // 16px
}

.card-content {
  padding: var(--spacing-lg);  // 24px
}
```

#### 表格内边距 (Table Cell Padding)

**标准**: 8px 16px (上下8px，左右16px)

```scss
.el-table {
  th {
    padding: var(--spacing-sm) var(--spacing-md) !important;  // 8px 16px
  }

  td {
    padding: var(--spacing-sm) var(--spacing-md) !important;  // 8px 16px
  }
}
```

### 3.4 间距工具类

**快速设置间距的工具类**：

```scss
// Margin工具类
.m-0 { margin: 0 !important; }
.m-1 { margin: var(--spacing-xs) !important; }  // 4px
.m-2 { margin: var(--spacing-sm) !important; }  // 8px
.m-3 { margin: var(--spacing-md) !important; }  // 16px
.m-4 { margin: var(--spacing-lg) !important; }  // 24px
.m-5 { margin: var(--spacing-xl) !important; }  // 32px
.m-6 { margin: var(--spacing-xxl) !important; } // 48px

.mx-1 { margin-left: var(--spacing-xs) !important; margin-right: var(--spacing-xs) !important; }
.mx-2 { margin-left: var(--spacing-sm) !important; margin-right: var(--spacing-sm) !important; }
.mx-3 { margin-left: var(--spacing-md) !important; margin-right: var(--spacing-md) !important; }

.my-1 { margin-top: var(--spacing-xs) !important; margin-bottom: var(--spacing-xs) !important; }
.my-2 { margin-top: var(--spacing-sm) !important; margin-bottom: var(--spacing-sm) !important; }
.my-3 { margin-top: var(--spacing-md) !important; margin-bottom: var(--spacing-md) !important; }

// Padding工具类
.p-0 { padding: 0 !important; }
.p-1 { padding: var(--spacing-xs) !important; }  // 4px
.p-2 { padding: var(--spacing-sm) !important; }  // 8px
.p-3 { padding: var(--spacing-md) !important; }  // 16px
.p-4 { padding: var(--spacing-lg) !important; }  // 24px
.p-5 { padding: var(--spacing-xl) !important; }  // 32px

.px-1 { padding-left: var(--spacing-xs) !important; padding-right: var(--spacing-xs) !important; }
.px-2 { padding-left: var(--spacing-sm) !important; padding-right: var(--spacing-sm) !important; }
.px-3 { padding-left: var(--spacing-md) !important; padding-right: var(--spacing-md) !important; }

.py-1 { padding-top: var(--spacing-xs) !important; padding-bottom: var(--spacing-xs) !important; }
.py-2 { padding-top: var(--spacing-sm) !important; padding-bottom: var(--spacing-sm) !important; }
.py-3 { padding-top: var(--spacing-md) !important; padding-bottom: var(--spacing-md) !important; }
```

---

## 🎨 4. 响应式规范 (Responsive Specification)

### 4.1 断点定义

```scss
// 断点变量
$breakpoint-xs: 1366px;  // 小屏幕 (笔记本)
$breakpoint-md: 1920px;  // 标准屏幕 (桌面)
$breakpoint-lg: 2560px;  // 大屏幕 (高清显示器)

// 媒体查询
@mixin respond-to($breakpoint) {
  @if $breakpoint == xs {
    @media (max-width: $breakpoint-xs) { @content; }
  }
  @if $breakpoint == md {
    @media (min-width: $breakpoint-xs + 1) and (max-width: $breakpoint-md) { @content; }
  }
  @if $breakpoint == lg {
    @media (min-width: $breakpoint-md + 1) { @content; }
  }
}
```

### 4.2 响应式适配规则

#### 卡片响应式

```scss
.card-data {
  // 1920x1080标准
  padding: var(--spacing-md);  // 16px
  min-height: 120px;

  // 1366x768适配
  @include respond-to(xs) {
    padding: var(--spacing-sm);  // 12px
    min-height: 100px;
  }
}
```

#### 按钮响应式

```scss
.btn-primary {
  // 标准屏幕
  height: 40px;
  padding: 0 var(--spacing-lg);  // 0 24px

  // 小屏幕
  @include respond-to(xs) {
    height: 36px;
    padding: 0 var(--spacing-md);  // 0 16px
  }
}
```

#### 间距响应式

```scss
.page-container {
  // 标准屏幕
  padding: var(--spacing-lg);  // 24px

  // 小屏幕
  @include respond-to(xs) {
    padding: var(--spacing-md);  // 16px
  }
}
```

---

## ✅ 5. 实施检查清单 (Implementation Checklist)

### 阶段1: 准备工作

- [ ] 创建`styles/visual-spec.scss`文件
- [ ] 备份现有`theme-apply.scss`文件
- [ ] 通知团队规范变更

### 阶段2: 核心规范实施

- [ ] **按钮规范** (优先级P0)
  - [ ] 添加Element Plus按钮全局覆盖代码
  - [ ] 测试所有页面按钮对齐
  - [ ] 验证文字居中效果

- [ ] **卡片规范** (优先级P1)
  - [ ] 添加Element Plus卡片全局覆盖代码
  - [ ] 测试不同类型卡片显示
  - [ ] 验证padding和圆角统一

- [ ] **间距规范** (优先级P2)
  - [ ] 添加间距工具类
  - [ ] 审查并修改非8px倍数的间距
  - [ ] 测试响应式适配

### 阶段3: 验证与优化

- [ ] 在P0核心页面验证 (Dashboard, Market, Stocks, Analysis, Trade, Settings)
- [ ] 在P1重要页面验证
- [ ] 在P2辅助页面验证
- [ ] 收集反馈并微调

---

## 📖 6. 使用指南 (Usage Guide)

### 快速参考卡片类型

| 卡片类型 | 何时使用 | Padding | 高度 |
|---------|---------|---------|------|
| `.card-data` | 统计数据、关键指标 | 16px | 120px |
| `.card-content` | 复杂内容、表格图表 | 24px | 300px+ |
| `.card-action` | 操作按钮、快捷入口 | 8px 16px | 80px |
| `.card-modal` | 弹窗、对话框 | 自定义 | 自适应 |

### 快速参考按钮类型

| 按钮类型 | 何时使用 | 高度 | Padding |
|---------|---------|------|---------|
| `.btn-primary` | 主要操作、提交 | 40px | 0 24px |
| `.btn-secondary` | 次要操作、取消 | 40px | 0 16px |
| `.btn-small` | 表格内操作 | 32px | 0 8px |
| `.btn-icon` | 纯图标按钮 | 36px | 0 |

### 快速参考间距级别

| 场景 | 使用间距 | CSS变量 |
|------|---------|---------|
| 组件内元素 | 8px / 16px | `var(--spacing-sm/md)` |
| 组件之间 | 16px / 24px | `var(--spacing-md/lg)` |
| 模块之间 | 32px / 48px | `var(--spacing-xl/xxl)` |

---

**规范版本**: v2.0
**生成时间**: 2026-01-08
**维护者**: MyStocks Frontend Team
**下次更新**: 根据实施反馈动态调整
