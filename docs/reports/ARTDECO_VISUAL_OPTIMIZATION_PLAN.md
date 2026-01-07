# ArtDeco 风格页面视觉优化方案

**文档版本**: v1.0
**创建时间**: 2026-01-06
**优化目标**: 解决卡片比例、按钮对齐、组件间距三大视觉问题
**技术栈**: Vue 3.4+ / SCSS / ArtDeco Design System

---

## 📋 目录

1. [问题诊断清单](#1-问题诊断清单)
2. [统一视觉规范](#2-统一视觉规范核心)
3. [分模块优化方案](#3-分模块优化方案)
4. [验证要点](#4-验证要点)
5. [实施路线图](#5-实施路线图)

---

## 1. 问题诊断清单

### 1.1 卡片比例失调问题

| 页面 | 模块 | 问题类型 | 具体表现 | 严重程度 |
|------|------|----------|----------|----------|
| Dashboard | 统计卡片网格 | 比例不一致 | `ArtDecoStatCard` 没有固定宽高比，响应式布局时卡片大小不统一 | 🔴 高 |
| Dashboard | 主图表卡片 | 留白过多 | 卡片padding 32px对于大面积图表来说过大，内容占比不足70% | 🟡 中 |
| MarketCenter | 行情卡片列表 | 宽高比混乱 | 不同行情卡片宽度由内容决定，导致视觉参差不齐 | 🔴 高 |
| StrategyLab | 策略卡片 | 内容溢出 | 卡片高度固定但内容可能溢出，未设置overflow处理 | 🟠 严重 |
| BacktestArena | 回测配置表单 | 比例失衡 | 表单卡片宽高比接近3:1，过于扁平，视觉压抑 | 🟡 中 |
| RiskCenter | 风险仪表板 | 比例不当 | 风险卡片4:3比例在1920px屏幕上显得过小，留白过多 | 🟡 中 |

**根本原因分析**:
```scss
// 当前代码：只有padding，无固定宽高比
.artdeco-card {
  padding: var(--artdeco-spacing-4); // 32px
  // ❌ 缺少: width, height, aspect-ratio
  // ❌ 缺少: min-width, max-width 约束
  // ❌ 缺少: overflow 处理
}
```

---

### 1.2 按钮文字对齐问题

| 页面 | 组件 | 问题类型 | 具体表现 | 严重程度 |
|------|------|----------|----------|----------|
| 全局 | `ArtDecoButton` | 垂直不居中 | 虽使用`display: flex`，但`line-height: 1`与`height`配合时，文字视觉上偏上1-2px | 🟡 中 |
| 全局 | `ArtDecoButton` | padding混乱 | 移动端响应式padding覆盖了桌面端定义，导致不同屏幕padding不一致 | 🟠 严重 |
| Dashboard | 按钮组 | 水平不居中 | 按钮组`artdeco-btn-group`中，secondary按钮与solid按钮padding差异过大 | 🟡 中 |
| MarketCenter | 操作按钮 | 文字基线偏移 | 图标+文字按钮中，图标与文字垂直对齐不一致（图标16px vs 文字14px） | 🟡 中 |
| StrategyLab | 表单按钮 | 对齐不一致 | 表单提交按钮与取消按钮并排时，视觉重心不在同一水平线 | 🟡 中 |

**根本原因分析**:
```scss
// 当前代码：Flexbox居中，但存在细节问题
.artdeco-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1; // ❌ 与height配合时可能导致视觉偏移

  // ❌ 移动端覆盖了桌面端padding
  @media (max-width: 768px) {
    &--md {
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
    }
  }
}
```

---

### 1.3 组件间距松散/混乱问题

| 页面 | 区域 | 问题类型 | 具体表现 | 严重程度 |
|------|------|----------|----------|----------|
| 全局 | 组件间间距 | 间距不统一 | 同一页面内，卡片间距有时16px有时32px，无明确规则 | 🟡 中 |
| Dashboard | Stats网格 | 间距过密 | `artdeco-stats-grid` gap仅16px，在1920px屏幕上显得拥挤 | 🟡 中 |
| Dashboard | 主布局 | 间距混乱 | 左右列间距32px，但右侧上下卡片间距24px，不一致 | 🟡 中 |
| MarketCenter | 筛选区域 | 间距过疏 | 表单组件间距24px，但按钮组与表单间距40px，过于松散 | 🟢 轻微 |
| StrategyLab | 参数面板 | 层次不清 | 所有组件使用统一间距16px，无法区分"组内"与"组间"关系 | 🟡 中 |
| 全局 | Section间距 | 响应式断裂 | 桌面端section-padding 96px，但移动端骤减到32px，过渡生硬 | 🟢 轻微 |

**根本原因分析**:
```scss
// 当前代码：有8px网格，但缺少使用规范
$artdeco-spacing-1: 8px;   // micro
$artdeco-spacing-2: 16px;  // tight
$artdeco-spacing-3: 24px;  // medium
$artdeco-spacing-4: 32px;  // standard

// ❌ 缺少: 何时使用spacing-2 vs spacing-3的明确规则
// ❌ 缺少: 组件内间距 vs 组件间间距 vs 模块间间距的区分
// ❌ 缺少: 响应式间距缩放策略
```

---

## 2. 统一视觉规范（核心）

### 2.1 卡片规范

#### 2.1.1 基础卡片样式

```scss
// ============================================
//   ARTDECO 卡片统一规范
//   基于8px网格系统，适配1920*1080分辨率
// ============================================

.artdeco-card {
  // 尺寸规范
  --artdeco-card-padding: var(--artdeco-spacing-4); // 32px
  --artdeco-card-border-radius: var(--artdeco-radius-md); // 8px
  --artdeco-card-border-width: 2px;

  // 内间距
  padding: var(--artdeco-card-padding);

  // 边框样式
  border: var(--artdeco-card-border-width) solid rgba(212, 175, 55, 0.2);
  border-radius: var(--artdeco-card-border-radius);

  // 背景
  background: var(--artdeco-bg-card);

  // 阴影（ArtDeco使用发光而非传统阴影）
  box-shadow: var(--artdeco-glow-subtle);

  // 过渡动画
  transition: all var(--artdeco-transition-base) var(--artdeco-ease-in-out);

  // 确保盒模型一致
  box-sizing: border-box;

  // 溢出处理
  overflow: hidden;

  // 悬停效果（可选）
  &:hover {
    border-color: var(--artdeco-accent-gold);
    box-shadow: var(--artdeco-glow-medium);
  }
}
```

#### 2.1.2 卡片类型与宽高比

| 卡片类型 | 使用场景 | 宽高比 | 固定尺寸（1920px） | 响应式断点 |
|---------|---------|--------|-------------------|-----------|
| **数据展示卡片** | 统计数字、指标卡片 | 4:3 | 360px × 270px | → 300×225 (1440px) → 240×180 (1280px) |
| **操作卡片** | 按钮、开关、输入框组 | 3:2 | 480px × 320px | → 400×267 (1440px) → 320×213 (1280px) |
| **图表卡片** | K线图、热力图 | 16:9 | 800px × 450px | → 640×360 (1440px) → 512×288 (1280px) |
| **列表卡片** | 表格、数据列表 | 3:1 | 100% × 400px | 高度自适应内容，最小320px |
| **表单卡片** | 配置、筛选表单 | 2:1 | 600px × 300px | → 500×250 (1440px) → 400×200 (1280px) |
| **全景卡片** | 全宽仪表板 | 21:9 | 1600px × 685px | → 1400×600 (1440px) |

**实现示例**:

```scss
// 数据展示卡片（4:3）
.artdeco-card--stat {
  aspect-ratio: 4 / 3;
  width: 360px;
  max-width: 100%;
  padding: var(--artdeco-spacing-5); // 40px（增加内边距突出内容）
  text-align: center;

  @media (max-width: 1440px) {
    width: 300px;
  }

  @media (max-width: 1280px) {
    width: 240px;
  }

  @media (max-width: 768px) {
    width: 100%;
    aspect-ratio: auto;
    padding: var(--artdeco-spacing-4);
  }
}

// 图表卡片（16:9）
.artdeco-card--chart {
  aspect-ratio: 16 / 9;
  width: 100%;
  min-height: 360px;
  padding: var(--artdeco-spacing-4);

  @media (max-width: 1440px) {
    min-height: 300px;
  }

  @media (max-width: 1280px) {
    min-height: 250px;
  }
}

// 表单卡片（2:1）
.artdeco-card--form {
  aspect-ratio: 2 / 1;
  width: 600px;
  max-width: 100%;
  padding: var(--artdeco-spacing-5);

  @media (max-width: 1440px) {
    width: 500px;
  }

  @media (max-width: 1280px) {
    width: 100%;
    aspect-ratio: auto;
  }
}
```

#### 2.1.3 卡片间距规范

| 场景 | 间距值 | 使用位置 | 示例 |
|------|--------|----------|------|
| **网格内卡片间距** | 24px | `gap`属性 | `grid-gap: var(--artdeco-spacing-3)` |
| **卡片与容器边缘** | 32px | 容器padding | `padding: var(--artdeco-spacing-4)` |
| **卡片内元素间距** | 16px | 卡片内部组件 | `margin-bottom: var(--artdeco-spacing-2)` |
| **卡片组之间** | 48px | 不同模块之间 | `margin-bottom: var(--artdeco-spacing-6)` |

**网格布局示例**:

```scss
// 统计卡片网格（4列）
.artdeco-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-3); // 24px - 卡片间距
  padding: var(--artdeco-spacing-4); // 32px - 容器内边距
  margin-bottom: var(--artdeco-spacing-6); // 48px - 模块间距

  @media (max-width: 1440px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--artdeco-spacing-2); // 16px - 移动端减小间距
    padding: var(--artdeco-spacing-3); // 24px - 移动端减小内边距
  }
}
```

---

### 2.2 按钮规范

#### 2.2.1 基础按钮样式

```scss
// ============================================
//   ARTDECO 按钮统一规范
//   确保完美居中 + 统一padding + 清晰尺寸
// ============================================

.artdeco-button {
  // ✅ 强制1: 使用Flexbox确保完美居中
  display: inline-flex;
  align-items: center; // 垂直居中
  justify-content: center; // 水平居中

  // ✅ 强制2: 零边框圆角（ArtDeco风格）
  border-radius: var(--artdeco-radius-none); // 0px

  // ✅ 强制3: 统一文字样式
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-family: var(--artdeco-font-body);
  font-weight: 600;
  line-height: 1; // ✅ 关键: 配合height实现精确垂直居中

  // ✅ 强制4: 移除默认样式
  border: none;
  outline: none;
  cursor: pointer;

  // 过渡动画
  transition: all var(--artdeco-transition-slow) var(--artdeco-ease-in-out);

  // 焦点状态（可访问性）
  &:focus-visible {
    outline: 2px solid var(--artdeco-accent-gold);
    outline-offset: 2px;
  }
}
```

#### 2.2.2 按钮尺寸与padding

| 尺寸 | 高度 | 水平padding | 字体大小 | 最小宽度 | 使用场景 |
|------|------|------------|----------|----------|----------|
| **sm (小)** | 40px | 24px (spacing-3) | 14px (0.875rem) | 80px | 表格操作、紧凑工具栏 |
| **md (中)** | 48px | 32px (spacing-4) | 16px (1rem) | 120px | 主要操作按钮（默认） |
| **lg (大)** | 56px | 40px (spacing-5) | 18px (1.125rem) | 160px | 主行动按钮、表单提交 |

**实现示例**:

```scss
// SMALL 按钮尺寸
.artdeco-button--sm {
  height: 40px;
  padding: 0 var(--artdeco-spacing-3); // 0 24px
  font-size: 0.875rem; // 14px
  min-width: 80px;

  // ❌ 删除移动端覆盖（保持一致性）
  // @media (max-width: 768px) { ... } ← 删除
}

// MEDIUM 按钮尺寸（默认）
.artdeco-button--md {
  height: 48px;
  padding: 0 var(--artdeco-spacing-4); // 0 32px
  font-size: 1rem; // 16px
  min-width: 120px;

  // ❌ 删除移动端覆盖
  // @media (max-width: 768px) { ... } ← 删除
}

// LARGE 按钮尺寸
.artdeco-button--lg {
  height: 56px;
  padding: 0 var(--artdeco-spacing-5); // 0 40px
  font-size: 1.125rem; // 18px
  min-width: 160px;

  // ❌ 删除移动端覆盖
  // @media (max-width: 768px) { ... } ← 删除
}
```

#### 2.2.3 按钮变体样式

| 变体 | 背景色 | 文字色 | 边框 | 悬停效果 | 使用场景 |
|------|--------|--------|------|----------|----------|
| **default** | 透明 | 金色 | 2px金色边框 | 金色背景+发光 | 默认按钮 |
| **solid** | 金色 | 黑色 | 2px金色边框 | 浅金+强发光 | 主操作按钮 |
| **outline** | 透明 | 金色 | 1px金色边框 | 10%金填充 | 次要按钮 |
| **secondary** | 同outline | - | - | - | outline别名 |
| **rise** | 透明 | 红色 | 2px红色边框 | 红色发光 | 上涨按钮 |
| **fall** | 透明 | 绿色 | 2px绿色边框 | 绿色发光 | 下跌按钮 |

#### 2.2.4 按钮间距规范

| 场景 | 间距值 | 使用位置 | 示例 |
|------|--------|----------|------|
| **按钮组内** | 12px | 并排按钮之间 | `gap: 12px` |
| **按钮与表单元素** | 16px | 按钮与输入框之间 | `margin-left: var(--artdeco-spacing-2)` |
| **独立按钮** | 24px | 按钮与其他组件 | `margin-bottom: var(--artdeco-spacing-3)` |

**按钮组示例**:

```scss
// 按钮组容器
.artdeco-btn-group {
  display: flex;
  gap: 12px; // ✅ 统一按钮组间距
  align-items: center;

  // 确保按钮垂直对齐
  .artdeco-button {
    margin: 0; // 移除默认margin
  }

  // 表单中的按钮组
  &.in-form {
    margin-top: var(--artdeco-spacing-4); // 32px - 与表单字段间距
  }
}
```

---

### 2.3 间距规范（8px网格系统）

#### 2.3.1 间距等级定义

| 等级 | 变量名 | 值 | 用途分类 | 典型使用场景 |
|------|--------|---|----------|--------------|
| **0** | `--artdeco-spacing-0` | 0px | 无间距 | 重置默认间距 |
| **1** | `--artdeco-spacing-1` | 8px | 微间距 | 组件内元素最小间距（图标与文字） |
| **2** | `--artdeco-spacing-2` | 16px | 紧凑间距 | 组件内元素间距（表单字段、卡片内元素） |
| **3** | `--artdeco-spacing-3` | 24px | 中等间距 | 组件间间距（卡片gap、按钮与表单） |
| **4** | `--artdeco-spacing-4` | 32px | 标准间距 | 模块内间距（容器padding、section内组件） |
| **5** | `--artdeco-spacing-5` | 40px | 宽松间距 | 大模块间距（独立section之间） |
| **6** | `--artdeco-spacing-6` | 48px | 宽敞间距 | 页面主要分区之间 |
| **8** | `--artdeco-spacing-8` | 64px | 大间距 | 页面顶部/底部留白 |

#### 2.3.2 间距使用规则

**规则1: 组件内间距（Component Internal）**
- 使用 `spacing-1` (8px) 或 `spacing-2` (16px)
- 场景：图标与文字、表单label与input、卡片header与body

```scss
// ✅ 正确示例
.artdeco-card-header {
  margin-bottom: var(--artdeco-spacing-2); // 16px
}

.artdeco-input__label {
  margin-bottom: var(--artdeco-spacing-1); // 8px
}
```

**规则2: 组件间间距（Component Spacing）**
- 使用 `spacing-3` (24px)
- 场景：相邻卡片、表单字段之间、按钮组与其他元素

```scss
// ✅ 正确示例
.artdeco-stats-grid {
  gap: var(--artdeco-spacing-3); // 24px
}

.form-field {
  margin-bottom: var(--artdeco-spacing-3); // 24px
}
```

**规则3: 模块内间距（Module Internal）**
- 使用 `spacing-4` (32px)
- 场景：容器padding、section内组件与边缘

```scss
// ✅ 正确示例
.artdeco-dashboard {
  padding: var(--artdeco-spacing-4); // 32px
}

.artdeco-card {
  padding: var(--artdeco-spacing-4); // 32px
}
```

**规则4: 模块间间距（Module Spacing）**
- 使用 `spacing-6` (48px)
- 场景：主要section之间、大型功能模块之间

```scss
// ✅ 正确示例
.artdeco-main-layout {
  margin-bottom: var(--artdeco-spacing-6); // 48px
}
```

**规则5: 页面级间距（Page Level）**
- 使用 `spacing-8` (64px) 或更大
- 场景：页面顶部留白、hero section之后

```scss
// ✅ 正确示例
.artdeco-hero-section {
  padding-top: var(--artdeco-spacing-8); // 64px
  padding-bottom: var(--artdeco-spacing-8);
}
```

#### 2.3.3 响应式间距缩放策略

| 屏幕尺寸 | 间距缩放系数 | spacing-2 | spacing-3 | spacing-4 | spacing-6 |
|---------|-------------|-----------|-----------|-----------|-----------|
| **1920px+** | 100% | 16px | 24px | 32px | 48px |
| **1440px** | 90% | 16px | 24px | 32px | 48px |
| **1366px** | 85% | 16px | 24px | 32px | 48px |
| **1280px** | 80% | 16px | 24px | 32px | 40px |
| **768px** | 75% | 16px | 24px | 32px | 40px |

**实现示例**:

```scss
// 容器padding响应式缩放
.artdeco-container {
  padding: var(--artdeco-spacing-4); // 32px (桌面端)

  @media (max-width: 1440px) {
    padding: var(--artdeco-spacing-4); // 保持32px
  }

  @media (max-width: 1280px) {
    padding: 28px; // 略微减小
  }

  @media (max-width: 768px) {
    padding: var(--artdeco-spacing-3); // 24px（移动端）
  }
}
```

---

## 3. 分模块优化方案

### 3.1 Dashboard页面优化

#### 3.1.1 统计卡片网格（Stats Grid）

**原问题**:
- 卡片无固定宽高比，响应式时大小不统一
- 间距仅16px，在1920px屏幕上显得拥挤

**优化方案**:

```scss
// ============================================
//   DASHBOARD 统计卡片网格优化
//   目标: 统一4:3宽高比 + 合理间距
// ============================================

.artdeco-stats-grid {
  // 布局
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-3); // ✅ 24px - 增加间距

  // 容器padding
  padding: var(--artdeco-spacing-4); // 32px
  margin-bottom: var(--artdeco-spacing-6); // 48px

  // 响应式
  @media (max-width: 1440px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--artdeco-spacing-2); // 16px - 移动端减小
    padding: var(--artdeco-spacing-3); // 24px - 移动端减小
  }
}

// 统计卡片组件
.artdeco-card--stat {
  // ✅ 固定4:3宽高比
  aspect-ratio: 4 / 3;
  width: 100%;
  min-width: 280px; // 防止过小
  max-width: 400px; // 防止过大

  // 内边距（增加突出内容）
  padding: var(--artdeco-spacing-5); // 40px

  // 文字居中
  text-align: center;

  // 溢出处理
  overflow: hidden;

  // 响应式调整
  @media (max-width: 1440px) {
    padding: var(--artdeco-spacing-4); // 32px
  }

  @media (max-width: 768px) {
    aspect-ratio: auto; // 移动端取消固定比例
    padding: var(--artdeco-spacing-4);
  }
}
```

**验证要点**:
- ✅ 所有卡片宽高比统一为4:3
- ✅ 卡片间距为24px（桌面端）/ 16px（移动端）
- ✅ 内容无溢出，文字完整显示
- ✅ 1440px屏幕自动切换为2列布局
- ✅ 768px屏幕自动切换为1列布局

---

#### 3.1.2 主图表卡片（Main Chart Card）

**原问题**:
- padding 32px对大面积图表过大，内容占比不足

**优化方案**:

```scss
// ============================================
//   DASHBOARD 主图表卡片优化
//   目标: 减少padding增加内容区域 + 统一16:9比例
// ============================================

.artdeco-card--chart {
  // ✅ 固定16:9宽高比
  aspect-ratio: 16 / 9;
  width: 100%;
  min-height: 400px;

  // 减少padding（图表卡片不需要太大内边距）
  padding: var(--artdeco-spacing-3); // 24px（原32px）

  // header与body间距
  .artdeco-card-header {
    margin-bottom: var(--artdeco-spacing-2); // 16px
    padding-bottom: var(--artdeco-spacing-2); // 16px
  }

  // 图表容器占满剩余空间
  .artdeco-chart {
    width: 100%;
    height: 100%;
    min-height: 320px;
  }

  // 响应式
  @media (max-width: 1440px) {
    min-height: 320px;

    .artdeco-chart {
      min-height: 260px;
    }
  }

  @media (max-width: 768px) {
    aspect-ratio: auto;
    min-height: 280px;
    padding: var(--artdeco-spacing-2); // 16px - 移动端进一步减小
  }
}
```

**验证要点**:
- ✅ 图表卡片宽高比16:9
- ✅ padding减少到24px（桌面端）/ 16px（移动端）
- ✅ 图表区域占比提升到85%以上
- ✅ 响应式断点下高度合理缩放

---

#### 3.1.3 策略控制面板（Strategy Control Panel）

**原问题**:
- 组件间距混乱，开关、滑块、状态框之间间距不统一

**优化方案**:

```scss
// ============================================
//   DASHBOARD 策略控制面板优化
//   目标: 统一组件间距 + 清晰层次
// ============================================

.strategy-controls {
  // 容器布局
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3); // ✅ 24px - 组件间统一间距

  // 组件内间距
  .artdeco-switch,
  .artdeco-slider {
    margin-bottom: 0; // ✅ 移除默认margin，使用gap
  }

  // 分隔线（视觉分组）
  .control-divider {
    height: 1px;
    background: rgba(212, 175, 55, 0.2);
    margin: var(--artdeco-spacing-2) 0; // 16px 上下边距
  }

  // 状态框
  .strategy-status-box {
    padding: var(--artdeco-spacing-3); // 24px
    background: rgba(212, 175, 55, 0.05);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--artdeco-radius-sm); // 4px

    .status-indicator {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2); // 16px - 图标与文字间距

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--artdeco-fg-muted);
        transition: all var(--artdeco-transition-base);
      }

      &.active .status-dot {
        background: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
      }
    }
  }
}
```

**验证要点**:
- ✅ 所有组件间距统一为24px
- ✅ 分隔线上下边距16px
- ✅ 状态框内图标与文字间距16px
- ✅ 视觉层次清晰（开关 > 分隔线 > 滑块 > 状态框）

---

### 3.2 MarketCenter页面优化

#### 3.2.1 行情卡片列表（Market Cards List）

**原问题**:
- 卡片宽度由内容决定，导致视觉参差不齐

**优化方案**:

```scss
// ============================================
//   MARKET CENTER 行情卡片列表优化
//   目标: 统一卡片宽度 + 固定比例
// ============================================

.market-cards-grid {
  // 布局
  display: grid;
  // ✅ 使用固定宽度列而非自适应
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--artdeco-spacing-3); // 24px

  padding: var(--artdeco-spacing-4); // 32px
  margin-bottom: var(--artdeco-spacing-6); // 48px

  // 响应式
  @media (max-width: 1440px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--artdeco-spacing-2); // 16px
    padding: var(--artdeco-spacing-3); // 24px
  }
}

// 行情卡片
.market-card {
  // ✅ 固定3:2宽高比
  aspect-ratio: 3 / 2;
  width: 100%;
  min-width: 320px;

  // 内边距
  padding: var(--artdeco-spacing-4); // 32px

  // 布局
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  // 溢出处理
  overflow: hidden;

  // 文字溢出省略
  .market-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .market-data {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--artdeco-spacing-2); // 16px
  }

  // 响应式
  @media (max-width: 1440px) {
    min-width: 280px;
    padding: var(--artdeco-spacing-3); // 24px
  }

  @media (max-width: 768px) {
    aspect-ratio: auto;
    min-width: 100%;
    padding: var(--artdeco-spacing-3);
  }
}
```

**验证要点**:
- ✅ 所有卡片宽度统一（最小320px）
- ✅ 宽高比固定3:2
- ✅ 自动填充布局，充分利用空间
- ✅ 文字溢出自动省略

---

#### 3.2.2 筛选区域（Filter Area）

**原问题**:
- 表单组件间距24px，但按钮组与表单间距40px，过于松散

**优化方案**:

```scss
// ============================================
//   MARKET CENTER 筛选区域优化
//   目标: 统一间距层次
// ============================================

.market-filter-area {
  // 容器padding
  padding: var(--artdeco-spacing-4); // 32px
  margin-bottom: var(--artdeco-spacing-4); // 32px

  // 表单布局
  .filter-form {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-2); // ✅ 16px - 表单字段间距（减小）

    // 按钮组与表单间距
    .filter-actions {
      margin-top: var(--artdeco-spacing-3); // ✅ 24px（原40px）

      display: flex;
      gap: var(--artdeco-spacing-2); // 16px - 按钮间距
      justify-content: flex-end;
    }
  }

  // 响应式
  @media (max-width: 768px) {
    padding: var(--artdeco-spacing-3); // 24px

    .filter-form {
      gap: var(--artdeco-spacing-1); // 8px - 移动端进一步减小

      .filter-actions {
        margin-top: var(--artdeco-spacing-2); // 16px
        flex-direction: column; // 按钮垂直排列

        .artdeco-button {
          width: 100%;
        }
      }
    }
  }
}
```

**验证要点**:
- ✅ 表单字段间距统一为16px
- ✅ 按钮组与表单间距24px（原40px）
- ✅ 按钮组内间距16px
- ✅ 移动端自动切换为垂直布局

---

### 3.3 StrategyLab页面优化

#### 3.3.1 策略卡片（Strategy Cards）

**原问题**:
- 卡片高度固定但内容可能溢出，未设置overflow处理

**优化方案**:

```scss
// ============================================
//   STRATEGY LAB 策略卡片优化
//   目标: 处理内容溢出 + 固定比例
// ============================================

.strategy-cards-grid {
  // 布局
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: var(--artdeco-spacing-4); // 32px - 卡片间距增大

  padding: var(--artdeco-spacing-4); // 32px
  margin-bottom: var(--artdeco-spacing-6); // 48px

  // 响应式
  @media (max-width: 1440px) {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--artdeco-spacing-3); // 24px
    padding: var(--artdeco-spacing-3); // 24px
  }
}

// 策略卡片
.strategy-card {
  // ✅ 固定4:3宽高比
  aspect-ratio: 4 / 3;
  width: 100%;
  min-height: 320px;

  // 内边距
  padding: var(--artdeco-spacing-4); // 32px

  // 布局
  display: flex;
  flex-direction: column;

  // ✅ 溢出处理（关键）
  overflow: hidden;

  // 卡片header
  .strategy-card-header {
    flex-shrink: 0; // 防止压缩

    .strategy-title {
      font-size: var(--artdeco-font-size-md); // 20px
      margin-bottom: var(--artdeco-spacing-1); // 8px

      // 标题溢出省略
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .strategy-meta {
      font-size: var(--artdeco-font-size-sm); // 14px
      color: var(--artdeco-fg-muted);
    }
  }

  // 卡片body（可滚动）
  .strategy-card-body {
    flex: 1;
    overflow-y: auto; // ✅ 内容溢出时滚动

    // 自定义滚动条样式
    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(212, 175, 55, 0.3);
      border-radius: 2px;

      &:hover {
        background: rgba(212, 175, 55, 0.5);
      }
    }

    // 内容溢出省略
    .strategy-description {
      display: -webkit-box;
      -webkit-line-clamp: 4; // 最多显示4行
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  // 卡片footer
  .strategy-card-footer {
    flex-shrink: 0; // 防止压缩
    margin-top: var(--artdeco-spacing-2); // 16px
    padding-top: var(--artdeco-spacing-2); // 16px
    border-top: 1px solid rgba(212, 175, 55, 0.2);

    display: flex;
    gap: var(--artdeco-spacing-2); // 16px
  }

  // 响应式
  @media (max-width: 1440px) {
    min-height: 280px;
    padding: var(--artdeco-spacing-3); // 24px
  }

  @media (max-width: 768px) {
    aspect-ratio: auto;
    min-height: auto;
    padding: var(--artdeco-spacing-3);
  }
}
```

**验证要点**:
- ✅ 卡片宽高比固定4:3
- ✅ 内容溢出时自动显示滚动条
- ✅ 标题过长自动省略
- ✅ 描述最多显示4行
- ✅ header和footer不会被压缩

---

#### 3.3.2 参数配置面板（Parameter Config Panel）

**原问题**:
- 所有组件使用统一间距16px，无法区分"组内"与"组间"关系

**优化方案**:

```scss
// ============================================
//   STRATEGY LAB 参数面板优化
//   目标: 使用间距区分层次
// ============================================

.parameter-config-panel {
  // 容器padding
  padding: var(--artdeco-spacing-4); // 32px

  // 参数组（使用间距分组）
  .parameter-group {
    margin-bottom: var(--artdeco-spacing-4); // ✅ 32px - 组间间距

    .group-title {
      font-size: var(--artdeco-font-size-base); // 16px
      margin-bottom: var(--artdeco-spacing-2); // 16px - 组标题与参数间距
    }

    // 组内参数
    .parameter-item {
      margin-bottom: var(--artdeco-spacing-2); // ✅ 16px - 参数间距（组内）
      padding: var(--artdeco-spacing-2); // 16px - 参数内边距

      background: rgba(212, 175, 55, 0.03);
      border: 1px solid rgba(212, 175, 55, 0.1);
      border-radius: var(--artdeco-radius-sm); // 4px

      &:last-child {
        margin-bottom: 0; // 最后一个参数无底部间距
      }
    }
  }

  // 面板底部按钮
  .panel-footer {
    margin-top: var(--artdeco-spacing-5); // ✅ 40px - 面板与按钮间距（增大）
    padding-top: var(--artdeco-spacing-3); // 24px
    border-top: 1px solid rgba(212, 175, 55, 0.2);

    display: flex;
    justify-content: flex-end;
    gap: var(--artdeco-spacing-2); // 16px - 按钮间距
  }

  // 响应式
  @media (max-width: 768px) {
    padding: var(--artdeco-spacing-3); // 24px

    .parameter-group {
      margin-bottom: var(--artdeco-spacing-3); // 24px

      .parameter-item {
        padding: var(--artdeco-spacing-1); // 8px - 移动端减小
      }
    }

    .panel-footer {
      margin-top: var(--artdeco-spacing-4); // 32px
      flex-direction: column;

      .artdeco-button {
        width: 100%;
      }
    }
  }
}
```

**验证要点**:
- ✅ 参数组之间间距32px（区分不同组）
- ✅ 参数之间间距16px（组内关系）
- ✅ 面板与按钮间距40px（突出操作区）
- ✅ 按钮间距16px
- ✅ 视觉层次清晰（组 > 参数项 > 按钮）

---

### 3.4 全局组件优化

#### 3.4.1 ArtDecoButton 组件修复

**原问题**:
- 移动端padding覆盖导致不一致
- 图标+文字按钮对齐不一致

**优化方案**:

```vue
<!-- ArtDecoButton.vue 修复版本 -->
<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    @click="handleClick"
  >
    <!-- 图标（可选） -->
    <span v-if="$slots.icon" class="artdeco-button__icon">
      <slot name="icon" />
    </span>

    <!-- 文字 -->
    <span class="artdeco-button__text">
      <slot />
    </span>
  </button>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   基础按钮样式（保持不变）
// ============================================
.artdeco-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--artdeco-radius-none);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-family: var(--artdeco-font-body);
  font-weight: 600;
  line-height: 1; // ✅ 保持精确垂直居中
  border: none;
  outline: none;
  cursor: pointer;
  transition: all var(--artdeco-transition-slow) var(--artdeco-ease-in-out);

  &:focus-visible {
    outline: 2px solid var(--artdeco-accent-gold);
    outline-offset: 2px;
  }
}

// ============================================
//   按钮尺寸（移除移动端覆盖）
// ============================================
.artdeco-button--sm {
  height: 40px;
  padding: 0 var(--artdeco-spacing-3); // 0 24px
  font-size: 0.875rem;
  min-width: 80px;
}

.artdeco-button--md {
  height: 48px;
  padding: 0 var(--artdeco-spacing-4); // 0 32px
  font-size: 1rem;
  min-width: 120px;
}

.artdeco-button--lg {
  height: 56px;
  padding: 0 var(--artdeco-spacing-5); // 0 40px
  font-size: 1.125rem;
  min-width: 160px;
}

// ❌ 删除移动端覆盖代码（原 line 319-334）
// @media (max-width: 768px) { ... } ← 完全删除

// ============================================
//   图标+文字对齐（新增）
// ============================================
.artdeco-button__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: var(--artdeco-spacing-1); // 8px - 图标与文字间距

  // 确保图标不变形
  flex-shrink: 0;

  // SVG图标样式
  svg {
    width: 100%;
    height: 100%;
    fill: currentColor;
  }
}

.artdeco-button__text {
  // 文字基线对齐
  line-height: 1;
  vertical-align: middle;
}

// 响应式图标大小（可选，根据实际需求）
@media (max-width: 768px) {
  .artdeco-button--sm,
  .artdeco-button--md {
    .artdeco-button__icon {
      width: 14px; // 略微减小
      height: 14px;
    }
  }
}
</style>
```

**使用示例**:

```vue
<!-- 图标+文字按钮 -->
<ArtDecoButton variant="solid" size="md">
  <template #icon>
    <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
  </template>
  Save Changes
</ArtDecoButton>
```

**验证要点**:
- ✅ 图标与文字垂直居中对齐
- ✅ 图标与文字间距8px
- ✅ 桌面端与移动端padding一致
- ✅ 不同尺寸按钮文字基线对齐

---

#### 3.4.2 ArtDecoCard 组件修复

**原问题**:
- 圆角系统定义冲突
- 缺少固定宽高比支持

**优化方案**:

```vue
<!-- ArtDecoCard.vue 修复版本 -->
<template>
  <div class="artdeco-card" :class="cardClasses" @click="handleClick">
    <!-- 角落装饰 -->
    <div class="artdeco-corner-tl"></div>
    <div class="artdeco-corner-br"></div>

    <!-- 卡片头部（可选） -->
    <div v-if="$slots.header || title" class="artdeco-card-header">
      <slot name="header">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="artdeco-card-subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- 卡片内容 -->
    <div class="artdeco-card-body">
      <slot></slot>
    </div>

    <!-- 卡片底部（可选） -->
    <div v-if="$slots.footer" class="artdeco-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  hoverable?: boolean
  clickable?: boolean
  variant?: 'default' | 'stat' | 'bordered' | 'chart' | 'form' // 新增chart和form
  aspectRatio?: string // 新增：4:3, 16:9, 3:2等
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  hoverable: true,
  clickable: false,
  variant: 'default',
  aspectRatio: '' // 不设置aspectRatio时不固定比例
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => ({
  'artdeco-card-clickable': props.clickable,
  'artdeco-card-hoverable': props.hoverable,
  [`artdeco-card-${props.variant}`]: true,
  [`artdeco-card-aspect-${props.aspectRatio.replace('/', '-')}`]: props.aspectRatio
}))

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   基础卡片样式（修复圆角冲突）
// ============================================
.artdeco-card {
  // ✅ 统一圆角（修复冲突定义）
  border-radius: var(--artdeco-radius-md); // 8px

  background: var(--artdeco-bg-card);
  border: 1px solid rgba(212, 175, 55, 0.2);
  padding: var(--artdeco-spacing-4); // 32px
  position: relative;
  overflow: hidden; // ✅ 添加溢出处理
  transition: all var(--artdeco-transition-base);
  box-sizing: border-box; // ✅ 确保盒模型一致

  // 悬停效果
  @include artdeco-hover-lift;
}

// ============================================
//   宽高比变体（新增）
// ============================================
.artdeco-card-aspect-4-3 {
  aspect-ratio: 4 / 3;
}

.artdeco-card-aspect-16-9 {
  aspect-ratio: 16 / 9;
}

.artdeco-card-aspect-3-2 {
  aspect-ratio: 3 / 2;
}

.artdeco-card-aspect-2-1 {
  aspect-ratio: 2 / 1;
}

// ============================================
//   其他变体（保持不变）
// ============================================
.artdeco-card-stat {
  padding: var(--artdeco-spacing-5); // 40px
  text-align: center;
}

.artdeco-card-bordered {
  border-width: 2px;
}

.artdeco-card-chart {
  padding: var(--artdeco-spacing-3); // 24px（图表卡片减小padding）
}

.artdeco-card-form {
  padding: var(--artdeco-spacing-5); // 40px
}

// 角落装饰、悬停效果等保持不变
// ...
</style>
```

**使用示例**:

```vue
<!-- 数据展示卡片（4:3） -->
<ArtDecoCard
  title="Market Index"
  subtitle="Real-time data"
  variant="stat"
  aspectRatio="4:3"
>
  <!-- content -->
</ArtDecoCard>

<!-- 图表卡片（16:9） -->
<ArtDecoCard
  variant="chart"
  aspectRatio="16:9"
>
  <!-- chart content -->
</ArtDecoCard>

<!-- 表单卡片（2:1） -->
<ArtDecoCard
  title="Filter Options"
  variant="form"
  aspectRatio="2:1"
>
  <!-- form content -->
</ArtDecoCard>
```

**验证要点**:
- ✅ 圆角统一为8px（修复冲突）
- ✅ 支持aspectRatio属性自定义宽高比
- ✅ 溢出内容正确处理
- ✅ 不同变体有对应padding
- ✅ 响应式自动调整

---

## 4. 验证要点

### 4.1 自动化验证脚本

创建自动化验证脚本，检查所有规范是否正确实施：

```javascript
// scripts/quality_gate/artdeco-visual-check.js
/**
 * ArtDeco 视觉规范自动化验证脚本
 * 运行: node scripts/quality_gate/artdeco-visual-check.js
 */

const fs = require('fs');
const path = require('path');

// 验证规则配置
const rules = {
  // 规则1: 检查按钮文字居中
  buttonCentering: {
    selector: '.artdeco-button',
    requiredStyles: {
      'display': 'inline-flex',
      'align-items': 'center',
      'justify-content': 'center',
      'line-height': '1'
    },
    forbiddenPatterns: [
      /@media\s*\([^)]*768px[^)]*\)\s*{[^}]*padding:/g // 禁止移动端覆盖padding
    ]
  },

  // 规则2: 检查卡片圆角统一
  cardBorderRadius: {
    selector: '.artdeco-card',
    requiredStyles: {
      'border-radius': 'var(--artdeco-radius-md)' // 8px
    }
  },

  // 规则3: 检查间距使用8px网格
  spacingGrid: {
    allowedValues: ['0px', '8px', '16px', '24px', '32px', '40px', '48px', '64px'],
    tolerance: 0.5 // 允许0.5px误差（calc结果）
  }
};

// 验证函数
function validateArtDecoStyles() {
  const results = {
    passed: 0,
    failed: 0,
    warnings: 0,
    errors: []
  };

  // 读取所有Vue组件和SCSS文件
  const componentsPath = path.join(__dirname, '../../web/frontend/src/components/artdeco');
  const files = getAllFiles(componentsPath, ['.vue', '.scss']);

  files.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');

    // 验证按钮居中
    if (content.includes('.artdeco-button')) {
      if (!content.includes('display: inline-flex')) {
        results.errors.push({
          file: path.relative(process.cwd(), file),
          rule: 'buttonCentering',
          message: '按钮未使用 inline-flex 实现居中'
        });
        results.failed++;
      } else {
        results.passed++;
      }
    }

    // 验证卡片圆角
    if (content.includes('.artdeco-card')) {
      if (content.includes('border-radius: 0px') || content.includes('border-radius: 2px')) {
        results.errors.push({
          file: path.relative(process.cwd(), file),
          rule: 'cardBorderRadius',
          message: '卡片圆角不是8px（radius-md）'
        });
        results.failed++;
      } else {
        results.passed++;
      }
    }

    // 验证移动端覆盖padding
    const mobilePaddingOverride = content.match(/@media\s*\([^)]*768px[^)]*\)\s*{[^}]*padding:/g);
    if (mobilePaddingOverride) {
      results.errors.push({
        file: path.relative(process.cwd(), file),
        rule: 'buttonPadding',
        message: '存在移动端padding覆盖',
        details: mobilePaddingOverride
      });
      results.failed++;
    }
  });

  // 输出结果
  console.log(`
========================================
ArtDeco 视觉规范验证结果
========================================

✅ 通过: ${results.passed}
❌ 失败: ${results.failed}
⚠️  警告: ${results.warnings}

${results.errors.length > 0 ? `
错误详情:
${results.errors.map(err => `
❌ ${err.file}
   规则: ${err.rule}
   问题: ${err.message}
   ${err.details ? `   代码: ${err.details}` : ''}
`).join('\n')}
` : ''}
========================================
  `);

  return results.failed === 0;
}

// 辅助函数：递归获取所有文件
function getAllFiles(dirPath, extensions) {
  const files = [];
  const items = fs.readdirSync(dirPath);

  items.forEach(item => {
    const fullPath = path.join(dirPath, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      files.push(...getAllFiles(fullPath, extensions));
    } else if (extensions.some(ext => item.endsWith(ext))) {
      files.push(fullPath);
    }
  });

  return files;
}

// 运行验证
if (require.main === module) {
  const success = validateArtDecoStyles();
  process.exit(success ? 0 : 1);
}

module.exports = { validateArtDecoStyles };
```

**运行验证**:

```bash
node scripts/quality_gate/artdeco-visual-check.js
```

---

### 4.2 手动验证清单

#### 4.2.1 按钮文字对齐验证

| 检查项 | 验证方法 | 预期结果 | 状态 |
|--------|---------|---------|------|
| **纯文字按钮居中** | 在不同尺寸按钮中输入单字/多字 | 文字水平和垂直完美居中 | ⬜ |
| **图标+文字对齐** | 添加16px图标+文字 | 图标与文字基线对齐，垂直居中 | ⬜ |
| **桌面端padding一致** | 检查sm/md/lg按钮padding | sm: 24px, md: 32px, lg: 40px | ⬜ |
| **移动端无覆盖** | 切换到768px宽度检查按钮尺寸 | 保持桌面端padding不变 | ⬜ |
| **按钮组对齐** | 并排不同尺寸按钮 | 所有按钮基线在同一水平线 | ⬜ |

**浏览器DevTools验证**:
```javascript
// 在控制台运行，检查所有按钮样式
document.querySelectorAll('.artdeco-button').forEach(btn => {
  const styles = window.getComputedStyle(btn);
  console.log({
    display: styles.display,
    alignItems: styles.alignItems,
    justifyContent: styles.justifyContent,
    lineHeight: styles.lineHeight,
    padding: styles.padding
  });
});
```

---

#### 4.2.2 卡片比例验证

| 检查项 | 验证方法 | 预期结果 | 状态 |
|--------|---------|---------|------|
| **数据卡片4:3** | 测量`ArtDecoStatCard`宽高 | 宽高比 = 1.333 (4/3) | ⬜ |
| **图表卡片16:9** | 测量图表卡片宽高 | 宽高比 = 1.778 (16/9) | ⬜ |
| **行情卡片3:2** | 测量市场卡片宽高 | 宽高比 = 1.5 (3/2) | ⬜ |
| **表单卡片2:1** | 测量表单卡片宽高 | 宽高比 = 2.0 (2/1) | ⬜ |
| **圆角统一** | 检查所有卡片border-radius | 全部为8px（radius-md） | ⬜ |
| **内容无溢出** | 输入超长文字测试 | 自动省略或滚动显示 | ⬜ |

**浏览器DevTools验证**:
```javascript
// 检查所有卡片的aspect-ratio
document.querySelectorAll('.artdeco-card').forEach(card => {
  const styles = window.getComputedStyle(card);
  const aspectRatio = styles.aspectRatio;
  const width = card.offsetWidth;
  const height = card.offsetHeight;
  const actualRatio = (width / height).toFixed(3);

  console.log({
    class: card.className,
    expectedRatio: aspectRatio || 'flex',
    actualRatio: actualRatio,
    width: width,
    height: height,
    match: !aspectRatio || Math.abs(width/height - parseAspectRatio(aspectRatio)) < 0.01
  });
});

function parseAspectRatio(ratio) {
  const [w, h] = ratio.split('/').map(Number);
  return w / h;
}
```

---

#### 4.2.3 组件间距验证

| 检查项 | 验证方法 | 预期结果 | 状态 |
|--------|---------|---------|------|
| **网格间距24px** | 测量卡片gap | gap = 24px (spacing-3) | ⬜ |
| **卡片padding 32px** | 测量卡片内边距 | padding = 32px (spacing-4) | ⬜ |
| **表单字段间距16px** | 测量表单组件margin-bottom | margin-bottom = 16px (spacing-2) | ⬜ |
| **按钮组间距12px** | 测量按钮gap | gap = 12px | ⬜ |
| **模块间距48px** | 测量section间距 | margin-bottom = 48px (spacing-6) | ⬜ |
| **8px网格遵守** | 检查所有间距值 | 全部为8的倍数（8/16/24/32/40/48/64） | ⬜ |

**浏览器DevTools验证**:
```javascript
// 检查所有间距是否符合8px网格
const spacingMultiples = [0, 8, 16, 24, 32, 40, 48, 64];

document.querySelectorAll('[class*="artdeco"]').forEach(el => {
  const styles = window.getComputedStyle(el);
  const properties = [
    'margin', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
    'padding', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right',
    'gap', 'grid-gap', 'column-gap', 'row-gap'
  ];

  properties.forEach(prop => {
    const value = styles[prop];
    if (value && value !== '0px' && value !== 'normal') {
      const pixels = parseFloat(value);
      const isMultiple = spacingMultiples.some(m => Math.abs(pixels - m) < 1);

      if (!isMultiple) {
        console.warn({
          element: el.className,
          property: prop,
          value: value,
          issue: `不是8的倍数（实际${pixels}px）`
        });
      }
    }
  });
});
```

---

### 4.3 响应式验证

#### 4.3.1 断点验证表格

| 断点 | 分辨率 | 验证项 | 预期行为 | 状态 |
|------|--------|--------|----------|------|
| **XXL** | 1920px+ | Stats网格 | 4列布局，卡片间距24px | ⬜ |
| **XL** | 1440px | Stats网格 | 2列布局，卡片间距24px | ⬜ |
| **LG** | 1366px | 图表卡片 | 最小高度300px | ⬜ |
| **MD** | 1280px | 图表卡片 | 最小高度250px | ⬜ |
| **SM** | 768px | 所有卡片 | 1列布局，间距减小 | ⬜ |
| **XS** | 480px | 按钮 | 保持桌面端padding | ⬜ |

**Chrome DevTools验证**:
1. 打开DevTools（F12）
2. 切换到设备工具栏（Ctrl+Shift+M）
3. 选择对应分辨率或自定义
4. 检查布局和间距是否符合预期

---

## 5. 实施路线图

### 5.1 优先级排序（按用户要求）

| 优先级 | 问题类型 | 预计工时 | 影响范围 | 实施顺序 |
|--------|---------|---------|---------|---------|
| **P0** | 按钮文字对齐 | 2小时 | 全局按钮组件 | ① |
| **P1** | 卡片比例失调 | 4小时 | 全局卡片组件 | ② |
| **P2** | 组件间距混乱 | 3小时 | 所有页面布局 | ③ |

**总预计工时**: 9小时（约1.5个工作日）

---

### 5.2 实施步骤

#### 阶段①：修复按钮文字对齐（2小时）

**步骤1.1**: 修改`ArtDecoButton.vue`（30分钟）
- ✅ 删除移动端padding覆盖代码（line 319-334）
- ✅ 添加图标+文字对齐支持
- ✅ 验证Flexbox居中属性完整

**步骤1.2**: 添加按钮组间距规范（30分钟）
- ✅ 创建`artdeco-btn-group`样式
- ✅ 统一按钮间距为12px（组内）/ 16px（组外）

**步骤1.3**: 测试验证（1小时）
- ✅ 纯文字按钮居中测试
- ✅ 图标+文字对齐测试
- ✅ 响应式断点测试
- ✅ 浏览器兼容性测试

**交付物**:
- 修改后的`ArtDecoButton.vue`
- 按钮验证清单

---

#### 阶段②：修复卡片比例失调（4小时）

**步骤2.1**: 修复`ArtDecoCard.vue`（1小时）
- ✅ 修复圆角系统冲突（统一为8px）
- ✅ 添加`aspectRatio`属性支持
- ✅ 添加`overflow: hidden`处理

**步骤2.2**: 创建卡片变体样式（1.5小时）
- ✅ `artdeco-card--stat`（4:3）
- ✅ `artdeco-card--chart`（16:9）
- ✅ `artdeco-card--form`（2:1）

**步骤2.3**: 更新现有页面（1小时）
- ✅ Dashboard统计卡片
- ✅ MarketCenter行情卡片
- ✅ StrategyLab策略卡片

**步骤2.4**: 测试验证（30分钟）
- ✅ 宽高比测量测试
- ✅ 内容溢出测试
- ✅ 响应式断点测试

**交付物**:
- 修改后的`ArtDecoCard.vue`
- 卡片验证清单
- 更新的页面文件

---

#### 阶段③：统一组件间距（3小时）

**步骤3.1**: 创建间距使用规范文档（1小时）
- ✅ 编写"组件内/组件间/模块间"间距规则
- ✅ 创建响应式间距缩放策略

**步骤3.2**: 更新全局布局（1小时）
- ✅ Dashboard网格间距
- ✅ MarketCenter筛选区域
- ✅ StrategyLab参数面板

**步骤3.3**: 测试验证（1小时）
- ✅ 8px网格遵守测试
- ✅ 间距层次测试
- ✅ 响应式缩放测试

**交付物**:
- 间距使用规范文档
- 更新的布局文件
- 间距验证清单

---

### 5.3 质量保证流程

**流程图**:

```
┌─────────────────────────────────────────────────────────────┐
│                    ArtDeco 优化质量保证流程                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① 开发完成                                                 │
│     ↓                                                      │
│  ② 自动化验证运行                                           │
│     ├─→ 通过 → ③ 手动验证清单                              │
│     └─→ 失败 → ⑦ 修复问题                                  │
│            ↓                                               │
│        ④ 全部通过？                                         │
│           ├─→ 是 → ⑤ 浏览器兼容性测试                     │
│           └─→ 否 → ⑦ 修复问题                              │
│                   ↓                                        │
│               ⑥ 回到②                                      │
│                                                             │
│  ⑤ 兼容性测试                                               │
│     ├─→ Chrome ✅                                          │
│     ├─→ Firefox ✅                                          │
│     ├─→ Safari ✅                                           │
│     ├─→ Edge ✅                                             │
│     └─→ 通过 → ⑧ 代码审查                                  │
│                                                             │
│  ⑧ 代码审查（Peer Review）                                 │
│     ├─→ 通过 → ⑨ 合并到主分支                              │
│     └─→ 修改 → ⑦ 修复问题                                  │
│                                                             │
│  ⑨ 合并后验证                                               │
│     └─→ 部署到测试环境 → 回归测试 → 生产部署               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.4 风险控制

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| **响应式布局破坏** | 中 | 高 | 每个阶段完成后立即测试所有断点 |
| **现有页面样式冲突** | 中 | 中 | 使用scoped样式，逐步迁移 |
| **浏览器兼容性问题** | 低 | 中 | 在Chrome/Firefox/Safari/Edge全量测试 |
| **用户习惯改变** | 低 | 低 | 保持视觉风格一致，仅优化细节 |

**回滚计划**:
- 所有修改通过Git分支管理
- 保留原始文件备份（`.backup`后缀）
- 发现问题立即回滚到上一个稳定版本

---

## 附录A：快速参考卡片

### A.1 卡片类型速查表

| 类型 | 比例 | 尺寸（1920px） | padding | 使用场景 |
|------|------|---------------|---------|----------|
| stat | 4:3 | 360×270px | 40px | 统计数字 |
| chart | 16:9 | 100%×400px | 24px | K线图、热力图 |
| form | 2:1 | 600×300px | 40px | 配置表单 |
| list | 3:1 | 100%×400px | 32px | 表格、列表 |

### A.2 按钮尺寸速查表

| 尺寸 | 高度 | padding | 字体 | 最小宽度 |
|------|------|---------|------|----------|
| sm | 40px | 0 24px | 14px | 80px |
| md | 48px | 0 32px | 16px | 120px |
| lg | 56px | 0 40px | 18px | 160px |

### A.3 间距速查表

| 场景 | 变量 | 值 | 用途 |
|------|------|---|------|
| 组件内 | spacing-2 | 16px | 表单字段、卡片元素 |
| 组件间 | spacing-3 | 24px | 卡片gap、按钮组 |
| 模块内 | spacing-4 | 32px | 容器padding |
| 模块间 | spacing-6 | 48px | section间距 |

---

## 附录B：常见问题FAQ

**Q1: 为什么移动端不覆盖按钮padding？**

A: 保持一致性比减小间距更重要。现代手机屏幕足够大，48px高度按钮在移动端依然舒适。如果必须优化，应该调整容器padding而非按钮本身。

**Q2: 卡片固定宽高比如何处理内容溢出？**

A: 使用`overflow-y: auto`在卡片body内部添加滚动条。对于标题和描述等文本，使用CSS省略号（`text-overflow: ellipsis`或`-webkit-line-clamp`）。

**Q3: 8px网格系统是否可以例外？**

A: 仅在极少数情况下允许例外（如border宽度1px）。所有padding/margin/gap必须严格遵守8的倍数。如有疑问，优先使用spacing变量而非直接写像素值。

**Q4: 响应式断点如何选择？**

A: 遵循"内容优先"原则：
- 1920px+ : 超大屏（4列网格）
- 1440px : 标准大屏（2列网格）
- 768px : 移动断点（1列布局）

---

**文档结束**

**下一步行动**:
1. ✅ 审阅本优化方案
2. ✅ 确认优先级和实施顺序
3. ✅ 开始阶段①：修复按钮文字对齐
4. ✅ 完成后运行自动化验证脚本

**联系方式**:
如有疑问或需要调整，请立即反馈以确保方案符合实际需求。
