# Linear Design System - 使用指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


基于 `/opt/iflow/myhtml/prompts/modern_dark_style.md` 的 Linear/Modern 设计风格实现。

---

## 🎨 设计理念

**核心原则**: 精确(Precision)、深度(Depth)、流畅性(Fluidity)

Linear 设计系统通过多层环境光照和精密微交互,营造出**高端开发者工具**的质感。类似于 Linear、Vercel、Raycast 的设计语言。

**设计特色**:
- 🌌 **多层背景系统**: 渐变 + 噪声 + 网格 + 动画blob
- ✨ **鼠标跟踪聚光灯**: 交互表面响应光标位置
- 🎭 **多层阴影系统**: 3-4层阴影组合创造真实深度
- ⚡ **精密微交互**: 200-300ms, expo-out缓动,移动4-8px
- 🎨 **渐变排版**: 标题使用渐变填充
- 💫 **动画环境光**: 4个大型渐变blob缓慢漂浮

---

## 📦 主题系统架构

### 1. JSON 配置文件

**深色主题**: `/src/config/themes/linear-dark.json`
**浅色主题**: `/src/config/themes/linear-light.json`

每个配置包含:
- 颜色系统 (背景、前景、强调色、边框、渐变)
- 背景层系统 (渐变、噪声、网格、动画blob)
- 多层阴影系统
- 排版系统 (字体、字重、行高、字间距)
- 间距系统
- 圆角系统
- 动画系统 (时长、缓动函数)
- 聚光灯设置
- 组件样式

### 2. 主题管理器

**位置**: `/src/config/theme-manager.ts`

**核心功能**:
- 单例模式管理主题状态
- CSS 变量运行时注入
- localStorage 持久化
- Vue 3 Composition API 集成

**使用示例**:
```typescript
import { useTheme } from '@/config/theme-manager'

const { isDark, toggleTheme, setDarkTheme, setLightTheme } = useTheme()

// 切换主题
toggleTheme()

// 设置深色主题
setDarkTheme()

// 检查当前主题
console.log(isDark.value) // true/false
```

### 3. CSS Token 系统

**位置**: `/src/styles/linear-tokens.scss`

**内容**:
- 100+ CSS 自定义属性
- 多层背景系统样式
- 排版样式类
- 卡片组件样式
- 按钮组件样式
- 输入框样式
- 工具类
- 动画关键帧

---

## 🚀 快速开始

### 1. 基本设置 (已完成)

```javascript
// main.js
import './styles/linear-tokens.scss'

// App.vue
<template>
  <LinearThemeProvider>
    <router-view />
  </LinearThemeProvider>
</template>

<script setup>
import LinearThemeProvider from '@/components/LinearThemeProvider.vue'
</script>
```

### 2. 使用主题组件

#### LinearCard - 带聚光灯效果的卡片

```vue
<template>
  <LinearCard>
    <h2>Card Title</h2>
    <p>Card content with mouse-tracking spotlight</p>
  </LinearCard>
</template>

<script setup>
import LinearCard from '@/components/LinearCard.vue'
</script>
```

**特性**:
- ✅ 多层玻璃效果背景
- ✅ 鼠标跟踪聚光灯(300px直径,accent色15%透明度)
- ✅ 悬停时渐变边框淡入
- ✅ 精密悬停动画(-4px位移)

#### LinearThemeToggle - 主题切换按钮

```vue
<template>
  <LinearThemeToggle :show-label="true" />
</template>

<script setup>
import LinearThemeToggle from '@/components/LinearThemeToggle.vue'
</script>
```

**特性**:
- ☀️ 深色模式显示太阳图标
- 🌙 浅色模式显示月亮图标
- 🎯 图标旋转/浮动动画
- 💾 自动保存用户偏好到localStorage

### 3. 使用工具类

```vue
<template>
  <!-- 排版 -->
  <h1 class="linear-text--display">Display Heading</h1>
  <h2 class="linear-text--h1">H1 Heading</h2>
  <p class="linear-text--body">Body text</p>
  <span class="linear-text--label">LABEL</span>

  <!-- 渐变文字 -->
  <h2 class="linear-text--gradient">Gradient Text</h2>

  <!-- 按钮 -->
  <button class="linear-button linear-button--primary">
    Primary Button
  </button>
  <button class="linear-button linear-button--secondary">
    Secondary Button
  </button>

  <!-- 输入框 -->
  <input
    type="text"
    class="linear-input"
    placeholder="Enter text..."
  />

  <!-- 间距 -->
  <div class="linear-p-md linear-gap-lg">
    <span>Content</span>
  </div>

  <!-- 圆角 -->
  <div class="linear-rounded-xl">
    Rounded content
  </div>
</template>
```

### 4. 使用CSS变量

```vue
<style scoped>
.custom-component {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-card);
  color: var(--fg-primary);
  font-family: var(--font-sans);
  transition: all var(--duration-normal) var(--easing-default);
}

.custom-component:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-4px);
}
</style>
```

---

## 🎨 设计 Token 参考

### 颜色系统

| Token | 深色主题值 | 浅色主题值 | 用途 |
|-------|-----------|-----------|------|
| `--bg-deep` | #020203 | #ffffff | 最深层背景 |
| `--bg-base` | #050506 | #f9fafb | 主页面背景 |
| `--bg-elevated` | #0a0a0c | #ffffff | 抬升表面 |
| `--bg-surface` | rgba(255,255,255,0.05) | rgba(0,0,0,0.02) | 卡片背景 |
| `--fg-primary` | #EDEDEF | #111827 | 主文本 |
| `--fg-muted` | #8A8F98 | #6B7280 | 次要文本 |
| `--accent-primary` | #5E6AD2 | #5E6AD2 | 主强调色 |

### 阴影系统

```css
/* 卡片默认 */
--shadow-card: 0 0 0 1px rgba(255,255,255,0.06),
                0 2px 20px rgba(0,0,0,0.4),
                0 0 40px rgba(0,0,0,0.2);

/* 卡片悬停 */
--shadow-card-hover: 0 0 0 1px rgba(255,255,255,0.10),
                     0 8px 40px rgba(0,0,0,0.5),
                     0 0 80px rgba(94,106,210,0.1);

/* 按钮发光 */
--shadow-button: 0 0 0 1px rgba(94,106,210,0.5),
                  0 4px 12px rgba(94,106,210,0.3),
                  inset 0 1px 0 0 rgba(255,255,255,0.2);
```

### 动画时长

| Token | 值 | 用途 |
|-------|-----|------|
| `--duration-fast` | 200ms | 快速交互 |
| `--duration-normal` | 300ms | 标准过渡 |
| `--duration-slow` | 600ms | 入场动画 |
| `--duration-blob` | 8000ms | 背景blob漂浮 |

### 缓动函数

```css
--easing-default: cubic-bezier(0.16, 1, 0.3, 1);  /* expo-out */
--easing-out: ease-out;
--easing-in-out: ease-in-out;
```

---

## 🎭 背景动画系统

### 多层背景结构

```
Layer 4: Animated Blobs (4个大型渐变形状)
    ↓
Layer 3: Grid Overlay (64px网格, 2%透明度)
    ↓
Layer 2: Noise Texture (SVG噪声, 1.5%透明度)
    ↓
Layer 1: Base Gradient (径向渐变)
    ↓
Browser Background
```

### Blob 动画配置

| Blob | 位置 | 尺寸 | 颜色 | 动画时长 |
|------|------|------|------|---------|
| Primary | 顶部居中 | 900×1400px | accent 25% | 8s |
| Secondary | 左侧 | 600×800px | purple 15% | 10s |
| Tertiary | 右侧 | 500×700px | indigo 12% | 9s |
| Accent | 底部 | 800×600px | accent 10% + pulse | 8s |

**关键帧动画**:
```css
@keyframes linear-float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(1deg); }
}

@keyframes linear-pulse {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.15; }
}
```

---

## 🔧 自定义和扩展

### 1. 修改主题颜色

编辑 `/src/config/themes/linear-dark.json`:

```json
{
  "colors": {
    "accent": {
      "primary": "#5E6AD2",  // 修改这个值改变主题色
      "bright": "#6872D9",
      "glow": "rgba(94,106,210,0.3)"
    }
  }
}
```

### 2. 创建自定义组件

```vue
<!-- MyCustomLinearComponent.vue -->
<template>
  <div class="my-linear-component">
    <slot />
  </div>
</template>

<style scoped>
.my-linear-component {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-card);
  transition: all var(--duration-normal) var(--easing-default);
}

.my-linear-component:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--border-hover);
}
</style>
```

### 3. 添加新的CSS变量

在 `linear-tokens.scss` 中添加:

```scss
:root {
  --my-custom-color: #value;
  --my-custom-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

[data-theme="light"] {
  --my-custom-color: #light-value;
}
```

---

## 📱 响应式设计

### 移动端断点

```scss
@media (max-width: 768px) {
  .linear-text--display { font-size: 3rem; }
  .linear-text--h1 { font-size: 2.25rem; }
  .linear-card { padding: var(--spacing-lg); }
}
```

### 减少动画支持

```scss
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## ♿ 可访问性

### 对比度

- 主文本 (#EDEDEF on #050506): ~15:1 ✅
- 次要文本 (#8A8F98 on #050506): ~6:1 ✅
- 强调色: 确保4.5:1最小对比度

### 焦点状态

所有交互组件都有可见的焦点环:

```css
.linear-button:focus-visible,
.linear-input:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}
```

---

## 🎯 最佳实践

### ✅ 推荐做法

1. **使用CSS变量而非硬编码颜色**
   ```css
   /* ✅ Good */
   background: var(--bg-surface);
   color: var(--fg-primary);

   /* ❌ Bad */
   background: #050506;
   color: #EDEDEF;
   ```

2. **使用工具类而非内联样式**
   ```vue
   <!-- ✅ Good -->
   <div class="linear-p-md linear-gap-lg">

   <!-- ❌ Bad -->
   <div style="padding: 1rem; gap: 1.5rem;">
   ```

3. **使用主题管理器切换主题**
   ```typescript
   // ✅ Good
   import { useTheme } from '@/config/theme-manager'
   const { toggleTheme } = useTheme()

   // ❌ Bad
   document.documentElement.setAttribute('data-theme', 'light')
   ```

### ❌ 避免做法

1. **不要使用纯黑 (#000000)** → 使用 `#050506` 或 `#020203`
2. **不要使用纯白文本** → 使用 `#EDEDEF` 或 `var(--fg-primary)`
3. **不要使用大位移** → 悬停位移最大8px
4. **不要使用弹跳动画** → 使用 expo-out 缓动
5. **不要忽略减少动画偏好** → 始终提供 `@media (prefers-reduced-motion)`

---

## 🐛 故障排查

### 主题不生效

1. 检查 `main.js` 是否导入 `linear-tokens.scss`
2. 检查 `App.vue` 是否使用 `LinearThemeProvider`
3. 检查浏览器控制台是否有CSS变量未定义错误

### 动画不流畅

1. 确认使用了 `will-change` 或 `transform` 而非 `top/left`
2. 检查是否有JavaScript阻塞主线程
3. 使用 Chrome DevTools Performance 分析器

### 字体未加载

1. 检查 `index.html` 是否有 Google Fonts 链接
2. 检查 CSP 是否允许 `fonts.googleapis.com`
3. 清除浏览器缓存

---

## 📚 参考资源

- **设计规范**: `/opt/iflow/myhtml/prompts/modern_dark_style.md`
- **主题配置**: `/src/config/themes/linear-*.json`
- **主题管理器**: `/src/config/theme-manager.ts`
- **CSS Tokens**: `/src/styles/linear-tokens.scss`
- **示例组件**: `/src/components/Linear*.vue`

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-31
**作者**: MyStocks Design System
