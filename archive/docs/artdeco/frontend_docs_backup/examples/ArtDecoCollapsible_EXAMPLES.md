# ArtDecoCollapsible 使用示例

## 概述

`ArtDecoCollapsible` 是一个可折叠面板组件，用于实现**渐进式信息披露（Progressive Disclosure）**，减少页面认知负荷。

## 基础用法

### 1. 简单折叠面板

```vue
<script setup lang="ts">
import { ref } from 'vue'
import ArtDecoCollapsible from '@/components/artdeco/base/ArtDecoCollapsible.vue'

const isExpanded = ref(false)
</script>

<template>
  <ArtDecoCollapsible
    title="技术指标概览"
    v-model="isExpanded"
  >
    <div class="indicators-grid">
      <!-- RSI指标 -->
      <ArtDecoStatCard label="RSI(14)" :value="65.23" />

      <!-- MACD指标 -->
      <ArtDecoStatCard label="MACD" :value="0.52" />

      <!-- KDJ指标 -->
      <ArtDecoStatCard label="KDJ-K" :value="78.45" />

      <!-- 布林带指标 -->
      <ArtDecoStatCard label="BOLL-UB" :value="125.67" />

      <!-- 威廉指标 -->
      <ArtDecoStatCard label="WR(14)" :value="23.45" />

      <!-- 均线系统 -->
      <ArtDecoStatCard label="MA5" :value="118.92" />
    </div>
  </ArtDecoCollapsible>
</template>
```

### 2. Dashboard 优化示例（减少36个数据点到12个）

**优化前** (所有数据同时显示):
```vue
<template>
  <div class="dashboard">
    <!-- 6个主要统计卡片 -->
    <ArtDecoStatCard label="上证指数" :value="3245.67" />
    <ArtDecoStatCard label="深证成指" :value="10234.56" />
    <ArtDecoStatCard label="创业板指" :value="2456.78" />
    <ArtDecoStatCard label="北向资金" :value="45.67" />
    <ArtDecoStatCard label="涨跌家数" value="2456/1892" />
    <ArtDecoStatCard label="成交金额" :value="8945.23" />

    <!-- 18个技术指标（同时显示） -->
    <div class="indicators-grid">
      <ArtDecoStatCard label="RSI(14)" :value="65.23" />
      <ArtDecoStatCard label="MACD" :value="0.52" />
      <ArtDecoStatCard label="KDJ-K" :value="78.45" />
      <ArtDecoStatCard label="KDJ-D" :value="72.34" />
      <ArtDecoStatCard label="KDJ-J" :value="6.11" />
      <ArtDecoStatCard label="BOLL-UB" :value="125.67" />
      <ArtDecoStatCard label="BOLL-MB" :value="118.92" />
      <ArtDecoStatCard label="BOLL-LB" :value="112.17" />
      <ArtDecoStatCard label="WR(14)" :value="23.45" />
      <ArtDecoStatCard label="WR(28)" :value="12.34" />
      <ArtDecoStatCard label="CCI" :value="156.78" />
      <ArtDecoStatCard label="ATR(14)" :value="8.92" />
      <ArtDecoStatCard label="MA5" :value="118.92" />
      <ArtDecoStatCard label="MA10" :value="116.78" />
      <ArtDecoStatCard label="MA20" :value="114.56" />
      <ArtDecoStatCard label="MA60" :value="108.34" />
      <ArtDecoStatCard label="EMA5" :value="119.12" />
      <ArtDecoStatCard label="EMA10" :value="117.45" />
    </div>
  </div>
</template>
```

**优化后** (使用可折叠面板，默认只显示关键数据):
```vue
<script setup lang="ts">
import { ref } from 'vue'
import ArtDecoCollapsible from '@/components/artdeco/base/ArtDecoCollapsible.vue'
import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'

// 默认展开关键指标面板
const criticalIndicatorsExpanded = ref(true)
const technicalIndicatorsExpanded = ref(false)
const movingAveragesExpanded = ref(false)

// 关键指标（默认显示）
const criticalIndicators = [
  { label: 'RSI(14)', value: 65.23 },
  { label: 'MACD', value: 0.52 },
  { label: 'KDJ-K', value: 78.45 }
]

// 完整技术指标（可折叠）
const allIndicators = [
  ...criticalIndicators,
  { label: 'KDJ-D', value: 72.34 },
  { label: 'KDJ-J', value: 6.11 },
  { label: 'BOLL-UB', value: 125.67 },
  { label: 'BOLL-MB', value: 118.92 },
  { label: 'BOLL-LB', value: 112.17 },
  { label: 'WR(14)', value: 23.45 },
  { label: 'WR(28)', value: 12.34 },
  { label: 'CCI', value: 156.78 }
]
</script>

<template>
  <div class="dashboard-optimized">
    <!-- 6个主要统计卡片（始终显示） -->
    <div class="primary-stats">
      <ArtDecoStatCard label="上证指数" :value="3245.67" />
      <ArtDecoStatCard label="深证成指" :value="10234.56" />
      <ArtDecoStatCard label="创业板指" :value="2456.78" />
      <ArtDecoStatCard label="北向资金" :value="45.67" />
      <ArtDecoStatCard label="涨跌家数" value="2456/1892" />
      <ArtDecoStatCard label="成交金额" :value="8945.23" />
    </div>

    <!-- 关键技术指标（默认展开） -->
    <ArtDecoCollapsible
      title="关键指标"
      v-model="criticalIndicatorsExpanded"
    >
      <div class="indicators-grid">
        <ArtDecoStatCard
          v-for="indicator in criticalIndicators"
          :key="indicator.label"
          :label="indicator.label"
          :value="indicator.value"
        />
      </div>
    </ArtDecoCollapsible>

    <!-- 完整技术指标（默认折叠） -->
    <ArtDecoCollapsible
      title="完整技术指标"
      v-model="technicalIndicatorsExpanded"
    >
      <div class="indicators-grid">
        <ArtDecoStatCard
          v-for="indicator in allIndicators"
          :key="indicator.label"
          :label="indicator.label"
          :value="indicator.value"
        />
      </div>
    </ArtDecoCollapsible>

    <!-- 均线系统（默认折叠） -->
    <ArtDecoCollapsible
      title="均线系统"
      v-model="movingAveragesExpanded"
    >
      <div class="indicators-grid">
        <ArtDecoStatCard label="MA5" :value="118.92" />
        <ArtDecoStatCard label="MA10" :value="116.78" />
        <ArtDecoStatCard label="MA20" :value="114.56" />
        <ArtDecoStatCard label="MA60" :value="108.34" />
        <ArtDecoStatCard label="EMA5" :value="119.12" />
        <ArtDecoStatCard label="EMA10" :value="117.45" />
      </div>
    </ArtDecoCollapsible>
  </div>
</template>

<style scoped>
.dashboard-optimized {
  .primary-stats {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-4);
  }

  .indicators-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: var(--artdeco-spacing-3);
  }
}
</style>
```

### 3. 受控模式（完全由父组件控制）

```vue
<script setup lang="ts">
import { ref } from 'vue'

const expandAll = ref(false)

const expandAllPanels = () => {
  expandAll.value = true
}

const collapseAllPanels = () => {
  expandAll.value = false
}
</script>

<template>
  <div>
    <!-- 控制按钮 -->
    <div class="controls">
      <button @click="expandAllPanels">全部展开</button>
      <button @click="collapseAllPanels">全部折叠</button>
    </div>

    <!-- 所有面板受控 -->
    <ArtDecoCollapsible title="面板1" :expanded="expandAll">
      内容1...
    </ArtDecoCollapsible>

    <ArtDecoCollapsible title="面板2" :expanded="expandAll">
      内容2...
    </ArtDecoCollapsible>

    <ArtDecoCollapsible title="面板3" :expanded="expandAll">
      内容3...
    </ArtDecoCollapsible>
  </div>
</template>
```

### 4. 自定义标题插槽

```vue
<template>
  <ArtDecoCollapsible>
    <template #title>
      <div class="custom-title">
        <span class="icon">📊</span>
        <span class="text">自定义标题</span>
        <span class="badge">新</span>
      </div>
    </template>

    <div>面板内容...</div>
  </ArtDecoCollapsible>
</template>

<style scoped>
.custom-title {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  .icon {
    font-size: 20px;
  }

  .badge {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 12px;
  }
}
</style>
```

### 5. 嵌套折叠面板

```vue
<script setup lang="ts">
import { ref } from 'vue'

const outerExpanded = ref(false)
const innerExpanded1 = ref(false)
const innerExpanded2 = ref(false)
</script>

<template>
  <ArtDecoCollapsible title="父级面板" v-model="outerExpanded">
    <!-- 父级内容 -->
    <p>这是父级面板的内容</p>

    <!-- 子级面板1 -->
    <ArtDecoCollapsible title="子级面板 1" v-model="innerExpanded1">
      <p>子级面板1的内容</p>
    </ArtDecoCollapsible>

    <!-- 子级面板2 -->
    <ArtDecoCollapsible title="子级面板 2" v-model="innerExpanded2">
      <p>子级面板2的内容</p>
    </ArtDecoCollapsible>
  </ArtDecoCollapsible>
</template>
```

### 6. 禁用状态

```vue
<template>
  <ArtDecoCollapsible
    title="禁用的面板"
    :disabled="true"
  >
    <div>此面板无法展开/折叠</div>
  </ArtDecoCollapsible>
</template>
```

### 7. 监听展开/折叠事件

```vue
<script setup lang="ts">
import { ref } from 'vue'

const isExpanded = ref(false)

const handleExpand = () => {
  console.log('面板展开了')
  // 可以在这里加载面板数据
}

const handleCollapse = () => {
  console.log('面板折叠了')
  // 可以在这里释放资源
}

const handleToggle = (expanded: boolean) => {
  console.log('面板状态:', expanded ? '展开' : '折叠')
}
</script>

<template>
  <ArtDecoCollapsible
    title="事件监听示例"
    v-model="isExpanded"
    @expand="handleExpand"
    @collapse="handleCollapse"
    @toggle="handleToggle"
  >
    <div>内容区域</div>
  </ArtDecoCollapsible>
</template>
```

### 8. 自定义动画速度

```vue
<script setup lang="ts">
import { ref } from 'vue'

const isExpanded = ref(false)
const slowAnimation = 500 // 500ms
const fastAnimation = 150 // 150ms
</script>

<template>
  <!-- 慢速动画 -->
  <ArtDecoCollapsible
    title="慢速动画"
    v-model="isExpanded"
    :duration="slowAnimation"
  >
    <div>内容区域</div>
  </ArtDecoCollapsible>

  <!-- 快速动画 -->
  <ArtDecoCollapsible
    title="快速动画"
    v-model="isExpanded"
    :duration="fastAnimation"
  >
    <div>内容区域</div>
  </ArtDecoCollapsible>
</template>
```

## 无障碍性特性

`ArtDecoCollapsible` 组件完全符合WCAG 2.1 AA标准：

### 1. 键盘导航

- **Tab**: 聚焦到折叠面板头部
- **Enter / Space**: 切换展开/折叠状态
- **焦点环**: 清晰的金色焦点环指示当前聚焦元素

```vue
<!-- 键盘操作示例 -->
<ArtDecoCollapsible title="键盘可访问" v-model="expanded">
  <div>使用Tab键聚焦，Enter/Space切换</div>
</ArtDecoCollapsible>
```

### 2. ARIA标签

组件自动生成以下ARIA标签：

- `role="button"`: 头部按钮角色
- `tabindex="0"`: 可通过Tab键访问
- `aria-expanded`: 当前展开状态
- `aria-controls`: 关联的内容区域ID
- `role="region"`: 内容区域角色
- `aria-labelledby`: 关联的头部ID

```html
<!-- 生成的HTML结构 -->
<div class="artdeco-collapsible">
  <div
    class="artdeco-collapsible-header"
    role="button"
    tabindex="0"
    aria-expanded="true"
    aria-controls="collapsible-content-xxx"
  >
    <div class="artdeco-collapsible-title">标题</div>
  </div>

  <div
    id="collapsible-content-xxx"
    class="artdeco-collapsible-content"
    role="region"
    aria-labelledby="collapsible-header-xxx"
  >
    <div>内容区域</div>
  </div>
</div>
```

### 3. 屏幕阅读器支持

屏幕阅读器会朗读：
- 聚焦时: "标题，按钮，展开"
- 切换时: "展开" 或 "折叠"
- 内容: 面板内的所有内容

### 4. 减少动画支持

对于偏好减少动画的用户，面板展开/折叠动画会自动禁用：

```css
@media (prefers-reduced-motion: reduce) {
  /* 所有动画过渡被禁用 */
}
```

## 最佳实践

### 1. 何时使用可折叠面板

✅ **推荐使用场景**：
- 信息密度高的页面（如Dashboard）
- 次要信息或高级功能
- 大段文本内容
- 可选的配置选项
- 详细帮助文档

❌ **不推荐使用场景**：
- 关键操作按钮（不要折叠"提交"按钮）
- 必读的警告信息
- 简短内容（折叠的价值不大）
- 需要频繁切换的状态

### 2. 默认状态选择

**默认展开**（`defaultExpanded: true`）：
- 关键指标和核心数据
- 用户首次访问时最重要的内容
- 需要快速访问的信息

**默认折叠**（`defaultExpanded: false`）：
- 高级功能和配置
- 详细文档和说明
- 次要数据和历史记录

### 3. 分组策略

按**重要性**和**使用频率**分组：

```vue
<template>
  <!-- 第一优先级：关键指标（默认展开） -->
  <ArtDecoCollapsible title="核心指标" :default-expanded="true">
    <ArtDecoStatCard label="RSI(14)" :value="65.23" />
    <ArtDecoStatCard label="MACD" :value="0.52" />
    <ArtDecoStatCard label="KDJ-K" :value="78.45" />
  </ArtDecoCollapsible>

  <!-- 第二优先级：扩展指标（默认折叠） -->
  <ArtDecoCollapsible title="扩展指标">
    <ArtDecoStatCard label="WR(14)" :value="23.45" />
    <ArtDecoStatCard label="CCI" :value="156.78" />
    <ArtDecoStatCard label="ATR(14)" :value="8.92" />
  </ArtDecoCollapsible>

  <!-- 第三优先级：高级设置（默认折叠） -->
  <ArtDecoCollapsible title="高级配置">
    <ArtDecoStatCard label="EMV(14)" :value="12.34" />
    <ArtDecoStatCard label="VR(26)" :value="45.67" />
    <ArtDecoStatCard label="BRAR(26)" :value="23.45" />
  </ArtDecoCollapsible>
</template>
```

### 4. 性能优化

**懒加载面板内容**：

```vue
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAria } from '@/composables/useAria'

const { liveRegion } = useAria()

const isExpanded = ref(false)
const data = ref(null)
const loading = ref(false)

// 仅在面板展开时加载数据
watch(isExpanded, async (newValue) => {
  if (newValue && !data.value) {
    loading.value = true
    try {
      data.value = await fetchIndicatorsData()
    } finally {
      loading.value = false
    }
  }
})
</script>

<template>
  <ArtDecoCollapsible title="懒加载指标" v-model="isExpanded">
    <div v-if="loading" v-bind="liveRegion('加载中...', 'polite').value">
      加载中...
    </div>
    <div v-else-if="data" v-bind="liveRegion('指标数据', 'polite').value">
      <ArtDecoStatCard
        v-for="item in data"
        :key="item.id"
        :label="item.label"
        :value="item.value"
      />
    </div>
    <div v-else>
      点击展开加载数据
    </div>
  </ArtDecoCollapsible>
</template>
```

## API 参考

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `''` | 面板标题 |
| `defaultExpanded` | `boolean` | `false` | 初始展开状态（非受控） |
| `expanded` | `boolean` | `undefined` | 受控模式：展开状态 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `duration` | `number` | `300` | 动画持续时间（ms） |

### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `update:expanded` | `(value: boolean)` | 展开状态变化 |
| `toggle` | `(value: boolean)` | 切换事件 |
| `expand` | `-` | 展开事件 |
| `collapse` | `-` | 折叠事件 |

### Slots

| 插槽 | 说明 |
|------|------|
| `default` | 面板内容 |
| `title` | 自定义标题 |

## 样式定制

组件使用ArtDeco设计令牌，完全可定制：

```scss
// 覆盖默认样式
.artdeco-collapsible {
  // 自定义边框
  --artdeco-border-color: #333;

  // 自定义背景
  --artdeco-bg-elevated: #0f0f0f;

  // 自定义间距
  --artdeco-spacing-3: 12px;
  --artdeco-spacing-4: 16px;

  // 自定义动画
  --artdeco-transition-base: 250ms;
  --artdeco-transition-slow: 500ms;
}
```

## 浏览器兼容性

- ✅ Chrome 86+
- ✅ Firefox 85+
- ✅ Safari 15.4+
- ✅ Edge 86+

## 总结

`ArtDecoCollapsible` 组件提供了一个优雅、无障碍、性能优化的方式来实现渐进式信息披露，有效减少页面认知负荷。
