# MyStocks CSS/SCSS 开发规范指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 版本：1.0 | 更新日期：2026-02-14
> 适用范围：`web/frontend/src/` 下所有 Vue 3 组件及样式文件
> 背景：本规范源自 Vue3 代码审核中对 47 个大组件的 CSS 提取实践，旨在从根源杜绝内联 CSS，保证样式管理的一致性和可维护性。

---

## 一、核心原则

1. **样式与逻辑完全分离** — CSS/SCSS 仅允许写在 `.scss` 文件中，`.vue` 文件的 `<style>` 块仅包含一行 `@import`
2. **组件级样式私有化** — 每个组件的样式存放于自身目录下的 `styles/` 子目录，不越级引用、不全局污染
3. **SCSS 优先** — 即使是单行样式，也必须写入 SCSS 文件，禁止"图省事"写内联

---

## 二、文件结构约定

### 2.1 全局样式目录

```
src/styles/                          # 全局样式（仅此目录允许全局选择器）
├── index.scss                       # 全局入口，统一导入
├── design-tokens.scss               # 设计令牌（颜色、间距、字体等）
├── artdeco-tokens.scss              # ArtDeco 主题令牌
├── theme-dark.scss                  # 暗色主题
├── theme-light.scss                 # 亮色主题
├── element-plus-override.scss       # Element Plus 覆盖样式
└── ...                              # 其他全局样式
```

### 2.2 组件样式目录

```
component-name/
├── ComponentName.vue                # 组件文件（style 块仅含 @import）
└── styles/
    └── ComponentName.scss           # 组件专属样式（必选）
```

**实际项目示例：**

```
src/components/artdeco/advanced/
├── ArtDecoCapitalFlow.vue           # <style> 仅含 @import
├── ArtDecoChipDistribution.vue
└── styles/
    ├── ArtDecoCapitalFlow.scss      # 1121 行样式，从组件中提取
    ├── ArtDecoChipDistribution.scss # 1064 行样式
    └── ...

src/views/monitoring/
├── WatchlistManagement.vue
├── RiskDashboard.vue
└── styles/
    ├── WatchlistManagement.scss
    └── RiskDashboard.scss
```

### 2.3 强制规则

| 规则 | 说明 |
|------|------|
| 新建组件必须创建 `styles/` 目录 | 组件创建时同步创建，否则 CR 不通过 |
| `.vue` 的 `<style>` 块仅含 `@import` | 禁止在 `<style>` 中直接写 CSS |
| 单个 SCSS 文件不超过 500 行 | 超过时拆分为 `_variables.scss`、`_mixins.scss`、`_layout.scss` 等 |
| 共享目录的 `styles/` 使用组件名命名 | 如 `src/views/styles/EnhancedDashboard.scss` |

---

## 三、Vue 组件中的样式引用

### 3.1 标准写法（唯一允许的方式）

```vue
<!-- ✅ 正确：style 块仅含 @import -->
<style lang="scss" scoped>
@import './styles/ComponentName.scss';
</style>
```

### 3.2 禁止的写法

```vue
<!-- ❌ 禁止：内联 style 属性 -->
<template>
  <div style="color: red; margin: 10px">...</div>
</template>

<!-- ❌ 禁止：:style 动态绑定（除例外场景） -->
<template>
  <div :style="{ color: themeColor, fontSize: '14px' }">...</div>
</template>

<!-- ❌ 禁止：在 <style> 中直接写 CSS -->
<style lang="scss" scoped>
.component-card {
  background: #1a1a2e;
  border-radius: 8px;
  /* 这些应该在 styles/ComponentName.scss 中 */
}
</style>
```

### 3.3 动态样式的正确处理

```vue
<!-- ✅ 正确：通过类名切换实现动态样式 -->
<template>
  <div :class="['card', { 'card--active': isActive, 'card--error': hasError }]">
    ...
  </div>
</template>

<!-- ✅ 正确：CSS 变量实现动态值 -->
<template>
  <div class="chart-container" :style="{ '--chart-height': chartHeight + 'px' }">
    <!-- 仅传递 CSS 变量值，实际样式在 SCSS 中 -->
  </div>
</template>
```

对应 SCSS：

```scss
// styles/ComponentName.scss
.chart-container {
  height: var(--chart-height, 400px); // 使用 CSS 变量，带默认值
}

.card {
  background: var(--artdeco-card-bg);
  border-radius: 8px;
  transition: all 0.3s ease;

  &--active {
    border-color: var(--artdeco-primary);
    box-shadow: 0 0 12px rgb(0 123 255 / 30%);
  }

  &--error {
    border-color: var(--artdeco-danger);
  }
}
```

### 3.4 例外场景（需注释说明）

仅以下场景允许使用 `:style` 绑定：

```vue
<!-- ✅ 允许：后端返回的动态定位/尺寸值 -->
<div
  class="stock-marker"
  :style="{ left: stock.x + 'px', top: stock.y + 'px' }"
>
  <!-- 例外说明：stock.x/y 为实时计算的图表坐标，无法预定义在 SCSS 中 -->
</div>

<!-- ✅ 允许：用户自定义颜色 -->
<div
  class="user-tag"
  :style="{ '--tag-color': userConfig.tagColor }"
>
  <!-- 例外说明：tagColor 为用户自定义值，通过 CSS 变量传递 -->
</div>
```

---

## 四、SCSS 编码规范

### 4.1 变量化

```scss
// ❌ 禁止硬编码
.panel-header {
  color: #e0e0e0;
  font-size: 14px;
  padding: 16px;
}

// ✅ 使用设计令牌或组件变量
.panel-header {
  color: var(--artdeco-text-primary);
  font-size: var(--font-size-sm);
  padding: var(--spacing-md);
}
```

### 4.2 嵌套层级（最多 3 层）

```scss
// ✅ 正确：3 层以内
.capital-flow {
  .flow-header {
    .header-title { ... } // 第 3 层，上限
  }
}

// ❌ 禁止：超过 3 层
.capital-flow {
  .flow-header {
    .header-title {
      .title-icon { ... } // 第 4 层，禁止
    }
  }
}

// ✅ 正确：用 BEM 命名扁平化
.capital-flow__header-title-icon { ... }
```

### 4.3 选择器命名

采用 BEM + 组件前缀：

```scss
// 组件根类名 = 组件名（kebab-case）
.artdeco-capital-flow {           // Block
  &__header { ... }               // Element
  &__chart { ... }
  &__chart--loading { ... }       // Modifier
  &__chart--error { ... }
}
```

### 4.4 禁止事项

| 禁止 | 原因 | 替代方案 |
|------|------|----------|
| `!important` | 破坏级联，难以维护 | 提高选择器特异性或用 CSS 变量 |
| `body`/`html`/`*` 全局选择器 | 全局污染 | 放在 `src/styles/` 全局文件中 |
| `@import` 引用其他组件的 SCSS | 组件耦合 | 提取为共享 mixin 或设计令牌 |
| 在 SCSS 中写 `clip: rect(...)` | 已废弃 | 使用 `clip-path: inset(...)` |
| 空 SCSS 注释 `//` | Stylelint 报错 | 删除或添加注释内容 |

### 4.5 Shorthand 属性规则

**先写 shorthand，再写 longhand 覆盖**，避免 `declaration-block-no-shorthand-property-overrides`：

```scss
// ❌ 错误：longhand 被 shorthand 覆盖，longhand 无效
.card {
  padding-bottom: 20px;    // 这行无效，被下面的 padding 覆盖
  padding: 16px;
}

// ✅ 正确：先 shorthand，再 longhand 覆盖
.card {
  padding: 16px;
  padding-bottom: 20px;    // 有效覆盖
}

// ✅ 正确：只用 shorthand
.card {
  padding: 16px 16px 20px;
}
```

### 4.6 @keyframes 规则

```scss
// ❌ 禁止：重复的关键帧选择器
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  50% { opacity: 0.6; }   // 重复的 50%，禁止
  100% { opacity: 1; }
}

// ✅ 正确：每个百分比只出现一次
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
```

---

## 五、Stylelint 配置

项目使用以下 Stylelint 配置（`web/frontend/.stylelintrc.json`），所有提交必须通过检查：

```json
{
  "extends": [
    "stylelint-config-standard-scss",
    "stylelint-config-recommended-vue"
  ],
  "plugins": ["stylelint-scss"],
  "rules": {
    "scss/at-rule-no-unknown": [true, {
      "ignoreAtRules": ["tailwind", "apply", "layer", "unlayer", "include", "mixin", "use"]
    }],
    "selector-pseudo-class-no-unknown": [true, {
      "ignorePseudoClasses": ["deep", "slotted", "global"]
    }],
    "selector-pseudo-element-no-unknown": [true, {
      "ignorePseudoElements": ["v-deep", "v-slotted", "v-global"]
    }],
    "color-function-notation": "modern",
    "alpha-value-notation": "percentage"
  }
}
```

**运行检查：**

```bash
cd web/frontend
npx stylelint "src/**/*.{vue,scss,css}"        # 检查
npx stylelint "src/**/*.{vue,scss,css}" --fix   # 自动修复
```

---

## 六、开发流程

### 6.1 新建组件

```bash
# 1. 创建组件目录和样式目录
mkdir -p src/components/feature/NewComponent/styles

# 2. 创建 SCSS 文件
touch src/components/feature/NewComponent/styles/NewComponent.scss

# 3. 创建 Vue 组件，style 块仅含 @import
```

### 6.2 修改现有组件样式

1. 找到组件对应的 `styles/ComponentName.scss`
2. 在 SCSS 文件中修改，**禁止**在 `.vue` 中添加内联样式"临时修复"
3. 运行 `npx stylelint` 验证

### 6.3 提交前检查清单

- [ ] `.vue` 文件的 `<style>` 块是否仅含 `@import`
- [ ] 是否有新增的内联 `style` 属性
- [ ] SCSS 嵌套是否超过 3 层
- [ ] 是否有硬编码的颜色/间距值
- [ ] `npx stylelint` 是否零错误通过
- [ ] 新组件是否创建了 `styles/` 目录

### 6.4 Code Review 关注点

| 检查项 | 严重级别 |
|--------|----------|
| `.vue` 中出现内联 `style` 属性 | 🔴 阻断 |
| `<style>` 块中直接写 CSS（非 @import） | 🔴 阻断 |
| 使用 `!important` | 🟡 警告（需注释说明） |
| SCSS 嵌套超过 3 层 | 🟡 警告 |
| 硬编码颜色/间距值 | 🟡 警告 |
| 缺少 `styles/` 目录 | 🔴 阻断 |
| Stylelint 报错 | 🔴 阻断 |

---

## 七、从本次审核中总结的经验教训

### 7.1 为什么内联 CSS 会失控

本次审核发现 25 个组件超过 1000 行，其中 60-70% 是内联 CSS。根本原因：

- 开发初期没有建立 `styles/` 目录约定，样式直接写在 `<style>` 块中
- 组件迭代时不断追加样式，没有拆分意识
- 缺少 Stylelint 检查，错误累积到 4639 个

### 7.2 提取成本 vs 预防成本

| 指标 | 事后提取 | 事前规范 |
|------|----------|----------|
| 涉及文件 | 47 个组件 + 47 个 SCSS | 每个组件 1 个 SCSS |
| 耗时 | 数小时批量处理 | 每个组件多 30 秒 |
| 风险 | CSS 语法错误、样式丢失 | 几乎为零 |
| Stylelint 修复 | 4639 → 0（多轮迭代） | 始终为 0 |

**结论：从第一个组件开始就遵守规范，成本远低于事后修复。**

### 7.3 大组件的拆分策略

当组件超过 500 行时，按以下优先级拆分：

1. **CSS 提取**（收益最大）：将 `<style>` 内容提取到 `styles/ComponentName.scss`
2. **Composable 提取**（逻辑复用）：将可复用逻辑提取到 `composables/useXxx.ts`
3. **配置提取**：将常量、配置对象提取到 `config/xxxConfig.ts`
4. **子组件拆分**（最后考虑）：仅当模板超过 300 行且有明确的功能边界时

---

## 八、附录

### A. 本项目已提取的 SCSS 文件清单

```
src/components/artdeco/advanced/styles/   # 6 个 ArtDeco 高级组件
src/views/artdeco-pages/styles/           # ArtDecoDashboard, ArtDecoSettings
src/views/demo/styles/                    # FreqtradeDemo, TdxpyDemo
src/views/market/styles/                  # Etf, Tdx, Technical
src/views/monitoring/styles/              # RiskDashboard, WatchlistManagement
src/views/styles/                         # EnhancedDashboard, StockDetail, monitor 等
```

### B. 本项目已提取的 Composables

```
src/composables/useKLineData.ts           # K 线数据管理
src/composables/useKLineControls.ts       # K 线图表控制
src/composables/useDashboardCharts.ts     # 仪表盘图表初始化
src/composables/useDashboardWatchlist.ts  # 自选股操作
src/components/technical/config/klineChartConfig.ts  # K 线配置常量
```

### C. 相关工具命令

```bash
# Stylelint 检查
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"

# Stylelint 自动修复
cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}" --fix

# 查找内联 style（人工检查）
grep -rn 'style="' src/ --include="*.vue" | grep -v '<style'

# 查找超过 500 行的组件
find src/ -name "*.vue" -exec sh -c 'l=$(wc -l < "$1"); [ "$l" -ge 500 ] && echo "$l $1"' _ {} \; | sort -rn

# 查找 <style> 块超过 3 行的组件（疑似未提取）
for f in $(find src/ -name "*.vue"); do
  n=$(sed -n '/<style/,/<\/style>/p' "$f" | wc -l)
  [ "$n" -gt 3 ] && echo "$n $f"
done | sort -rn
```
