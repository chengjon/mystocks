# TechStyle 主题系统实施指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 目录结构

```
web/frontend/src/
├── config/
│   ├── themes/
│   │   ├── tech-style-light.json      # 浅色主题配置
│   │   └── tech-style-dark.json       # 深色主题配置
│   └── theme-manager.ts              # 主题管理器
├── styles/
│   └── techstyle-tokens.scss         # TechStyle Token系统
└── components/
    ├── ThemeProvider.vue            # 主题提供者
    └── ThemeToggle.vue              # 主题切换器
```

## 🚀 快速开始

### 1. 在main.js中初始化主题系统

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import ThemeProvider from './components/ThemeProvider.vue'

const app = createApp(App)

// 包装根组件
app.component('ThemeProvider', ThemeProvider)

app.mount('#app')
```

### 2. 修改App.vue使用ThemeProvider

```vue
<template>
  <ThemeProvider>
    <router-view />
    <ThemeToggle />
  </ThemeProvider>
</template>

<script setup>
import ThemeProvider from '@/components/ThemeProvider.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>
```

### 3. 导入TechStyle样式

在main.js中导入：

```javascript
import './styles/techstyle-tokens.scss'
```

或在组件中导入：

```vue
<style scoped lang="scss">
@import '@/styles/techstyle-tokens.scss';

// 使用token
.my-component {
  background: var(--theme-card);
  color: var(--theme-foreground);
}
</style>
```

## 💡 使用主题系统

### 在组件中使用主题

```vue
<template>
  <div class="ts-container ts-section-spacing">
    <!-- Section Label -->
    <div class="ts-section-label">
      <span class="ts-dot pulsing"></span>
      <span>DASHBOARD</span>
    </div>

    <!-- Gradient Text -->
    <h1 class="ts-gradient-text ts-font-display">
      Welcome to <span class="ts-gradient-underline">MyStocks</span>
    </h1>

    <!-- Buttons -->
    <button class="ts-btn primary">Primary Action</button>
    <button class="ts-btn secondary">Secondary</button>

    <!-- Card -->
    <div class="ts-card">
      <p>Card content with TechStyle design</p>
    </div>

    <!-- Theme Toggle -->
    <ThemeToggle />
  </div>
</template>

<script setup>
import { useTheme } from '@/config/theme-manager'

const { theme, isDark, toggleTheme } = useTheme()
</script>

<style scoped lang="scss">
@import '@/styles/techstyle-tokens.scss';
</style>
```

### 可用的CSS变量

```scss
// 颜色
--theme-background
--theme-foreground
--theme-muted
--theme-muted-foreground
--theme-accent
--theme-accent-secondary
--theme-border
--theme-card

// 渐变
--gradient-accent
--gradient-accent-diagonal
--gradient-accent-subtle

// 字体
--font-display
--font-body
--font-mono

// 间距
--spacing-xs
--spacing-sm
--spacing-md
--spacing-lg
--spacing-xl
--spacing-section

// 圆角
--radius-sm
--radius-md
--radius-lg
--radius-xl
--radius-full

// 阴影
--shadow-sm
--shadow-md
--shadow-lg
--shadow-xl
--shadow-accent
```

### 可用的Utility Classes

#### 文本类
- `.ts-gradient-text` - 渐变文本
- `.ts-gradient-underline` - 渐变下划线
- `.ts-font-display` - Display字体 (Calistoga)
- `.ts-font-body` - Body字体 (Inter)
- `.ts-font-mono` - Monospace字体 (JetBrains Mono)

#### 组件类
- `.ts-btn` - 基础按钮样式
  - `.primary` - 主要按钮（渐变背景）
  - `.secondary` - 次要按钮（边框）
  - `.ghost` - 幽灵按钮（无背景）
- `.ts-card` - 卡片样式
  - `.elevated` - 抬升卡片（更强阴影）
- `.ts-input` - 输入框样式
- `.ts-section-label` - Section标签
- `.ts-dot` - 装饰圆点
  - `.pulsing` - 脉冲动画

#### 背景和纹理
- `.ts-dot-pattern` - 点阵背景
- `.ts-section-inverted` - 反色区域

#### 动画类
- `.ts-animate-float` - 浮动动画
- `.ts-animate-rotate` - 旋转动画
- `.ts-animate-pulse` - 脉冲动画

#### 布局类
- `.ts-container` - 居中容器（max-width: 72rem）
- `.ts-section-spacing` - Section间距（py-7rem）
- `.ts-section-spacing-large` - 大Section间距（py-11rem）

## 🎨 自定义主题

### 修改颜色

编辑 `config/themes/tech-style-light.json` 或 `tech-style-dark.json`：

```json
{
  "colors": {
    "accent": "#YOUR_COLOR",
    "accentSecondary": "#YOUR_COLOR_2"
  }
}
```

### 添加新主题

1. 在 `config/themes/` 创建新的JSON文件
2. 在 `theme-manager.ts` 中导入和注册：

```typescript
import customTheme from './themes/your-theme.json'

getAllThemes(): ThemeConfig[] {
  return [lightTheme, darkTheme, customTheme] as ThemeConfig[]
}
```

## 🔌 编程式主题切换

```vue
<script setup>
import { useTheme } from '@/config/theme-manager'

const {
  isDark,
  isLight,
  setLightTheme,
  setDarkTheme,
  toggleTheme
} = useTheme()

// 方法1: 切换到浅色
setLightTheme()

// 方法2: 切换到深色
setDarkTheme()

// 方法3: 自动切换
toggleTheme()

// 检查当前主题
console.log(isDark.value) // true/false
console.log(isLight.value) // true/false
</script>
```

## 📱 响应式设计

TechStyle已经包含响应式断点，继续使用现有的Tailwind响应式类：

```vue
<div class="ts-container ts-section-spacing">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Cards -->
  </div>
</div>
```

## ♿ 可访问性

TechStyle主题系统遵循WCAG AA标准：

- 所有文本对比度 ≥ 4.5:1
- 44px+ 最小触摸目标
- 清晰的焦点状态（2px ring）
- 支持prefers-reduced-motion

## 🎯 最佳实践

1. **使用CSS变量而非硬编码颜色**
   ```scss
   /* ✅ Good */
   color: var(--theme-foreground);

   /* ❌ Bad */
   color: #0F172A;
   ```

2. **使用语义化的类名**
   ```vue
   <!-- ✅ Good -->
   <button class="ts-btn primary">Click</button>

   <!-- ❌ Bad -->
   <button class="blue-button">Click</button>
   ```

3. **组合使用工具类**
   ```vue
   <div class="ts-card ts-animate-float">
     <h3 class="ts-gradient-text">Title</h3>
   </div>
   ```

## 🧪 测试主题切换

```bash
# 1. 启动开发服务器
npm run dev

# 2. 在浏览器中打开应用
# http://localhost:3020

# 3. 点击ThemeToggle按钮切换主题

# 4. 检查localStorage确认主题被持久化
# Application > Local Storage > techstyle-theme
```

## 📚 进阶使用

### 创建渐变边框卡片

```vue
<template>
  <div class="ts-gradient-border">
    <div class="p-6">
      <h3 class="ts-font-display">Featured Card</h3>
      <p>This card has a gradient border</p>
    </div>
  </div>
</template>
```

### 创建反色Section

```vue
<template>
  <section class="ts-section-inverted ts-section-spacing">
    <div class="ts-container">
      <div class="ts-section-label">
        <span class="ts-dot"></span>
        <span>STATISTICS</span>
      </div>
      <h2 class="text-4xl ts-font-display text-white">
        Key Metrics
      </h2>
    </div>
  </section>
</template>
```

### 使用渐变文本高亮

```vue
<template>
  <h1 class="text-5xl ts-font-display">
    <span class="ts-gradient-text">Powerful</span> Analytics
  </h1>
</template>
```

## 🐛 故障排除

### 主题没有应用

1. 确保导入了techstyle-tokens.scss
2. 确保ThemeProvider包裹了根组件
3. 检查浏览器控制台是否有错误

### 切换没有保存

检查localStorage是否被禁用或配额已满。

### 样式不一致

确保所有组件都通过ThemeProvider渲染。

## 📞 支持

如有问题，请查看：
- TechStyle.md - 完整设计规范
- theme-manager.ts - 主题管理器源码
- techstyle-tokens.scss - Token系统源码

---

**注意**: 主题系统使用localStorage持久化用户选择。清除浏览器数据会重置为默认主题（浅色）。
