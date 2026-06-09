# 前端手工测试修改记录 (2026-04-19)

> Dashboard 页面手工测试过程中，用户提出的 UI 修改需求及实施记录。

---

## 修改 1：移除侧边栏 MYSTOCKS 边框

**需求**：左侧导航栏顶部的 MYSTOCKS 文字带有一个金色边框，要求去掉。

**文件**：`web/frontend/src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue`

**位置**：第 170 行，`.brand-icon-frame` 样式块

**修改方法**：将 `border: 2px solid var(--artdeco-gold-primary)` 改为 `border: none`

```scss
// 修改前
.brand-icon-frame {
    border: 2px solid var(--artdeco-gold-primary);
    ...
}

// 修改后
.brand-icon-frame {
    border: none;
    ...
}
```

```
【修改要求】去掉左侧导航栏顶部 MYSTOCKS 文字的金色边框
【AI 修改方式】将 .brand-icon-frame 的 border 属性从 2px solid 改为 none
【回归风险点】所有使用 ArtDecoCollapsibleSidebar 的页面（当前仅 ArtDecoLayoutEnhanced 布局）
【回归检查项】1) 侧边栏 MYSTOCKS 区域视觉无边框 2) 侧边栏折叠/展开动画正常 3) 侧边栏导航菜单点击跳转正常
【后端是否受影响】否
```

---

## 修改 2：首行 Header 显示市场摘要数据

**需求**：Dashboard 页面首行原本显示无用的 "MyStocks ArtDeco" 文字。用户要求将该行替换为市场摘要信息：市场震荡、策略运行中数量、收益金额、时间戳、刷新数据按钮。

### 2a. 新建共享状态 composable

**文件**：`web/frontend/src/composables/useHeaderSummary.ts`（新建）

**作用**：提供模块级共享响应式状态，让 Dashboard composable 写入数据、Layout header 读取数据。

```ts
// 核心状态
const marketStatus = ref('')
const activeStrategiesCount: Ref<number | null> = ref(null)
const todayPnLValue = ref('¥0.00')
const currentTime = ref('')
const refreshing = ref(false)

// 导出 update() 用于写入，refresh() 用于触发刷新
```

### 2b. Dashboard composable 同步数据到共享状态

**文件**：`web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`

**修改 1** — 添加导入（第 3 行附近）：

```ts
import { useHeaderSummary } from '@/composables/useHeaderSummary'
```

**修改 2** — 在 `watch(activeFlowTab, ...)` 之前添加同步逻辑：

```ts
const headerSummary = useHeaderSummary()
headerSummary.setRefreshFn(refreshData)

watch(
  [marketStatus, activeStrategiesCount, todayPnLValue, currentTime, refreshing],
  () => {
    headerSummary.update({
      marketStatus: marketStatus.value,
      activeStrategiesCount: activeStrategiesCount.value,
      todayPnLValue: todayPnLValue.value,
      currentTime: currentTime.value,
      refreshing: refreshing.value,
    })
  },
  { immediate: true }
)
```

### 2c. Layout Header 读取并显示摘要数据

**文件**：`web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`

**修改 1** — 添加导入（script 区域）：

```ts
import { useHeaderSummary } from '@/composables/useHeaderSummary'

const headerSummary = useHeaderSummary()
```

**修改 2** — 为 `<ArtDecoHeader>` 添加 `#actions` 插槽内容（使用 ArtDeco 组件保持视觉一致性）：

```html
<ArtDecoHeader ...>
  <template #actions>
    <div v-if="headerSummary.marketStatus.value" class="header-metrics">
      <ArtDecoBadge variant="primary" pulse>
        <ArtDecoIcon name="activity" />
        {{ headerSummary.activeStrategiesCount.value ?? 0 }} 策略运行中
      </ArtDecoBadge>
      <ArtDecoBadge variant="success" pulse>
        <ArtDecoIcon name="trending-up" />
        {{ headerSummary.todayPnLValue.value }}
      </ArtDecoBadge>
    </div>
    <div v-if="headerSummary.marketStatus.value" class="time-refresh">
      <div class="time-display">
        <ArtDecoIcon name="clock" />
        <span class="time-value">{{ headerSummary.currentTime.value }}</span>
      </div>
      <ArtDecoButton variant="outline" size="sm"
        @click="headerSummary.refresh()" :loading="headerSummary.refreshing.value">
        <template #icon><ArtDecoIcon name="refresh" /></template>
        刷新数据
      </ArtDecoButton>
    </div>
  </template>
</ArtDecoHeader>
```

> **设计决策**：最初使用纯 `<span>` 元素，用户反馈目标位置文字没有带格式迁移。改为使用 `ArtDecoBadge`、`ArtDecoButton`、`ArtDecoIcon` 组件实现平移，保持与设计系统一致的视觉效果。

**修改 3** — 添加样式（scoped style 区域末尾），最终版本使用 `:deep()` 穿透子组件样式：

```scss
.header-metrics {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-6);

  :deep(.artdeco-badge) {
    border: none;
    background: transparent;
  }
}

.time-refresh {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);

  :deep(.artdeco-button) {
    border: none;
    background: transparent;

    .artdeco-button__icon {
      margin-right: 0 !important;
      padding-right: 0 !important;
    }
  }

  .time-display {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-1);
  }

  .time-value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-gold-primary);
    font-weight: 600;
  }
}
```

> **技术说明**：最初使用 `.artdeco-badge` / `.artdeco-button` 直接选择器，但由于 Vue scoped CSS 的隔离机制，父组件的 scoped 选择器无法穿透到子组件内部元素。改用 `:deep()` 后 margin 生效，但 padding 仍被子组件样式覆盖，因此最终加 `!important` 确保 padding 归零。

### 2d. 移除 "MyStocks ArtDeco" 文字

**文件**：`web/frontend/src/components/artdeco/core/ArtDecoHeader.vue`

**位置**：第 5 行，`<div class="logo" v-else>` 内

**修改方法**：清空文字内容

```html
<!-- 修改前 -->
<div class="logo" v-else>MyStocks ArtDeco</div>

<!-- 修改后 -->
<div class="logo" v-else></div>
```

```
【修改要求】将 Dashboard 的市场摘要信息（市场状态、策略数、收益、时间、刷新按钮）平移到 Layout 首行 header，替换原有 "MyStocks ArtDeco" 文字；源位置清除
【AI 修改方式】1) 新建 useHeaderSummary.ts 模块级共享状态 composable 2) Dashboard composable watch 同步数据到共享状态 3) Layout header #actions 插槽读取共享状态并渲染 ArtDecoBadge/ArtDecoButton 组件 4) 清空 ArtDecoHeader logo 文字 5) Dashboard 的 ArtDecoHeader 改为自闭合（清除 #actions 插槽）
【回归风险点】1) 所有使用 ArtDecoLayoutEnhanced 布局的页面 header 均会显示摘要数据（marketStatus 为空时不显示） 2) ArtDecoHeader 被 layout 和 dashboard 共用，清空 logo 文字影响所有未传 title 的 header 实例 3) useHeaderSummary 模块级状态在 SPA 路由切换时持续存在，离开 Dashboard 后数据可能过期
【回归检查项】1) Dashboard 页面首行显示策略数/收益/时间/刷新按钮，样式无边框 2) Dashboard QUANTIX header 区域无重复摘要数据 3) 刷新按钮点击后数据更新 4) 从 Dashboard 导航到其他页面（如 /market、/watchlist）后 header 摘要仍显示（因共享状态未清除，属预期行为） 5) 其他使用 core/ArtDecoHeader 且未传 title 的页面不会显示多余文字
【后端是否受影响】否（纯前端状态同步，后端 API 调用未变）
```

---

## 修改 3：清除平移元素的边框和背景

**需求**：平移到 header 的 Badge 和 Button 元素带有边框，与 header 风格不协调，需要去除。

**文件**：`web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`

**位置**：scoped style 区域，`.header-metrics` 和 `.time-refresh` 内

**修改方法**：使用 `:deep()` 穿透子组件 scoped 样式：

```scss
// Badge 边框清除
.header-metrics {
  :deep(.artdeco-badge) {
    border: none;
    background: transparent;
  }
}

// Button 边框清除 + 图标间距调整
.time-refresh {
  :deep(.artdeco-button) {
    border: none;
    background: transparent;

    .artdeco-button__icon {
      margin-right: 0 !important;
      padding-right: 0 !important;
    }
  }
}
```

**技术要点**：
- Vue scoped CSS 无法直接选中子组件内部元素，必须使用 `:deep()` 穿透
- `.artdeco-button__icon` 的 `padding-right` 由 ArtDecoButton 组件自身 scoped 样式设置（12px），`:deep()` 穿透后仍被覆盖，最终需要 `!important` 才能生效
- 验证方式：浏览器 DevTools 检查 `getComputedStyle(icon).paddingRight` 从 `"12px"` 变为 `"0px"`

```
【修改要求】去除平移到 header 的 Badge 和 Button 元素的边框和背景，缩小刷新图标与"刷新数据"文字间距
【AI 修改方式】使用 :deep() 穿透子组件 scoped 样式，设置 border:none + background:transparent；图标间距使用 !important 覆盖子组件默认 padding-right:12px
【回归风险点】1) :deep() 选择器仅作用于 Layout 内的 .header-metrics 和 .time-refresh 容器，不影响其他页面使用 ArtDecoBadge/ArtDecoButton 的场景 2) !important 可能被未来更高优先级样式覆盖
【回归检查项】1) Dashboard header badge 无边框无背景 2) 刷新按钮无边框无背景 3) 刷新图标与文字紧邻（无多余间距） 4) 其他页面（如 /market）的 ArtDecoBadge/ArtDecoButton 样式不受影响（保留默认边框）
【后端是否受影响】否
```

---

## 修改 4：清除 Dashboard 源位置的摘要数据

**需求**：平移后，Dashboard 的 QUANTIX header 区域不再显示重复的市场摘要信息。

**文件**：`web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`

**修改方法**：将 `<ArtDecoHeader>` 从含 `#actions` 插槽的块元素改为自闭合标签：

```html
<!-- 修改前 -->
<ArtDecoHeader
    title="QUANTIX"
    subtitle="实时 洞察 策略 执行"
    :show-status="true"
    :status-text="marketStatus"
    :status-type="marketStatusType"
>
  <template #actions>
    <!-- 市场摘要、策略数、收益、时间、刷新按钮 -->
  </template>
</ArtDecoHeader>

<!-- 修改后 -->
<ArtDecoHeader
    title="QUANTIX"
    subtitle="实时 洞察 策略 执行"
    :show-status="true"
    :status-text="marketStatus"
    :status-type="marketStatusType"
/>
```

```
【修改要求】平移完成后，清除 Dashboard QUANTIX header 区域的重复市场摘要信息
【AI 修改方式】将 ArtDecoHeader 从含 #actions 插槽的块元素改为自闭合标签，不再传入 actions 插槽内容
【回归风险点】1) ArtDecoDashboard.vue 的 #actions 插槽被清除，如果其他代码引用了该插槽内容则受影响（当前无） 2) QUANTIX header 仍保留 title/subtitle/show-status/status-text/status-type 属性，这些功能未变
【回归检查项】1) Dashboard 页面 QUANTIX header 仅显示标题、副标题和市场状态指示器 2) QUANTIX header 右侧无多余的策略数/收益/时间信息 3) 首行 Layout header 正常显示平移后的摘要数据
【后端是否受影响】否
```

---

## 关键架构发现

在本次修改过程中发现：

| 文件路径 | 实际内容 | 说明 |
|---------|---------|------|
| `components/artdeco/core/ArtDecoHeader.vue` | 通用 header（title/subtitle/actions 插槽） | 116 行，被 layout 和 dashboard 共同使用 |
| `components/layout/ArtDecoHeader.vue` | 核心 header（搜索/通知/用户菜单） | 238 行，含侧边栏切换按钮 |

**注意**：两个文件名与内容的对应关系与直觉相反 — `core/` 目录下的是简单通用 header，`layout/` 目录下的是功能完整的核心 header。修改时需注意区分。

---

## 外部评审发现分析与结论

### Finding 1 (High): ArtDecoHeader 空 logo 块回归风险

**评审意见**：ArtDecoHeader 无 title 时渲染空 `<div>`，影响所有不传 title 的调用点。

**分析结论：实际风险低于评审判断，非回归问题。**

逐文件排查全部 40+ 处 `ArtDecoHeader` 调用：

| 调用位置 | 是否传 title | 走哪条分支 |
|---------|-------------|-----------|
| 所有 view 级页面（Dashboard/Market/Trading/Risk/Strategy/Data/System 等） | 是（显式 `title="xxx"`） | `v-if="title"` → `<h1>` |
| `src/layouts/ArtDecoLayoutEnhanced.vue:9` | 否（有意设计） | `v-else` → 空 `<div class="logo">` |

- 评审提到的 "many other no-title usages across views" **与实际 grep 结果不符**，不存在其他无 title 的调用点
- Layout header 不传 title 是有意设计：左侧空出，右侧 `#actions` 插槽显示市场摘要数据
- 空 `<div class="logo">` 在 Layout 场景下不影响视觉（左侧被 `#actions` 内容占据）

**预存问题（非本次引入）**：Layout 传了 `:unread-count` 和 `:user-name` 给 `core/ArtDecoHeader`，但该组件 props 只有 `title/subtitle/showStatus/statusText/statusType`，这些 prop 被静默忽略。说明 Layout 可能应该使用 `layout/ArtDecoHeader.vue`（带搜索/通知/用户菜单的完整版）。

### Finding 2 (Medium): Lighthouse 审计脚本路由过期

**评审意见**：`scripts/run-lighthouse-audits.sh` 中的路由与当前 `router/index.ts` 不匹配，审计 404 页面。

**分析结论：预存问题，与本次修改无关。**

本次修改涉及 6 个文件，均未触及 `src/router/index.ts` 或 `scripts/run-lighthouse-audits.sh`。路由别名不匹配是历史遗留问题，不归入本次修改的回归范围。

> 建议单独创建技术债条目跟踪 Lighthouse 脚本路由同步问题。

---

## 涉及文件汇总

| 文件 | 操作 |
|------|------|
| `src/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue` | 编辑（移除 MYSTOCKS 边框） |
| `src/composables/useHeaderSummary.ts` | 新建（共享响应式状态 composable） |
| `src/views/artdeco-pages/composables/useArtDecoDashboard.ts` | 编辑（添加 headerSummary 同步） |
| `src/layouts/ArtDecoLayoutEnhanced.vue` | 编辑（添加摘要显示 + `:deep()` 样式穿透） |
| `src/components/artdeco/core/ArtDecoHeader.vue` | 编辑（清空 logo 文字） |
| `src/views/artdeco-pages/ArtDecoDashboard.vue` | 编辑（清除源位置摘要数据） |

所有文件路径相对于 `web/frontend/`。
