# ArtDeco 标准页面模板使用指南

> **版本**: v1.0
> **适用**: ArtDeco v3.1 Governance Baseline
> **目标**: 统一所有 Vue 页面的开发规范，解决页面完成度参差不齐的问题

---

## 1. 快速开始

### 1.1 基础用法

最简单的使用方式：

```vue
<template>
  <ArtDecoPageTemplate :page-config="pageConfig">
    <template #content>
      <!-- 你的页面内容 -->
      <div>页面内容</div>
    </template>
  </ArtDecoPageTemplate>
</template>

<script setup lang="ts">
import ArtDecoPageTemplate from '@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue'

const pageConfig = {
  title: '页面标题',
  subtitle: '页面副标题',
  apiUrl: '/api/v1/your-endpoint',
  permission: 'artdeco:yourpage:view'
}
</script>
```

### 1.2 完整示例

参考 `ExampleRiskManagement.vue` 了解完整实现：

```vue
<template>
  <ArtDecoPageTemplate
    :page-config="pageConfig"
    :stats="stats"
    @data-loaded="handleDataLoaded"
  >
    <!-- 头部操作按钮 -->
    <template #header-actions>
      <ArtDecoButton @click="exportData">导出</ArtDecoButton>
    </template>

    <!-- 核心内容区 -->
    <template #content="{ data, loading, activeTab, refresh }">
      <div v-if="activeTab === 'overview'">概览内容</div>
      <div v-if="activeTab === 'detail'">详情内容</div>
    </template>
  </ArtDecoPageTemplate>
</template>
```

---

## 2. 页面配置 (ArtDecoPageConfig)

### 2.1 配置项说明

| 属性 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `title` | string | ✅ | 页面标题 | `'风险管理中心'` |
| `subtitle` | string | ❌ | 页面副标题 | `'实时监控投资组合风险'` |
| `apiUrl` | string | ❌ | API 端点地址 | `'/api/v1/risk'` |
| `apiMethod` | string | ❌ | 请求方法 | `'GET'` / `'POST'` |
| `apiParams` | object | ❌ | 请求参数 | `{ limit: 10 }` |
| `permission` | string | ✅ | 权限标识 | `'artdeco:risk:view'` |
| `skeleton` | object | ❌ | 骨架屏配置 | `{ columns: 4, rows: 3 }` |
| `emptyMessage` | string | ❌ | 空数据提示 | `'暂无数据'` |
| `showStatus` | boolean | ❌ | 显示状态指示器 | `true` |
| `showRefresh` | boolean | ❌ | 显示刷新按钮 | `true` |
| `showStats` | boolean | ❌ | 显示统计卡片区 | `false` |
| `showTabs` | boolean | ❌ | 显示标签页 | `false` |
| `cacheTime` | number | ❌ | 缓存时间(ms) | `300000` (5分钟) |

### 2.2 配置示例

```typescript
const pageConfig = {
  // 基础信息
  title: '风险管理中心',
  subtitle: '实时监控投资组合风险，设置止损策略',

  // 状态显示
  showStatus: true,
  statusText: '监控中',
  statusType: 'success',

  // 功能开关
  showRefresh: true,
  showStats: true,
  showTabs: true,

  // API 配置
  apiUrl: '/api/v1/risk/management',
  apiMethod: 'GET',
  apiParams: { date: new Date().toISOString() },

  // UI 配置
  skeleton: { columns: 4, rows: 3 },
  emptyMessage: '暂无风险数据',

  // 权限
  permission: 'artdeco:risk:view',

  // 性能优化
  cacheTime: 300000  // 5分钟
}
```

---

## 3. 插槽 (Slots)

### 3.1 可用插槽列表

| 插槽名 | 作用域参数 | 说明 |
|--------|------------|------|
| `#header-actions` | - | 头部操作按钮区 |
| `#stats` | - | 自定义统计卡片区 |
| `#tabs` | - | 自定义标签页导航 |
| `#content` | `{ data, loading, activeTab, refresh }` | 核心内容区 |
| `#footer` | - | 页面底部 |

### 3.2 使用示例

#### 头部操作按钮
```vue
<template #header-actions>
  <ArtDecoButton variant="outline" size="sm" @click="exportData">
    <ArtDecoIcon name="download" />
    导出
  </ArtDecoButton>
  <ArtDecoButton variant="solid" size="sm" @click="openSettings">
    设置
  </ArtDecoButton>
</template>
```

#### 核心内容区（带作用域参数）
```vue
<template #content="{ data, loading, activeTab, refresh }">
  <!-- 使用传入的数据 -->
  <div v-if="activeTab === 'overview'">
    <div v-for="item in data?.list" :key="item.id">
      {{ item.name }}
    </div>
  </div>

  <!-- 使用刷新方法 -->
  <ArtDecoButton @click="refresh">刷新数据</ArtDecoButton>
</template>
```

---

## 4. 事件 (Events)

### 4.1 可用事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `@tab-change` | `tabKey: string` | 标签页切换时触发 |
| `@data-loaded` | `data: any` | 数据加载完成时触发 |
| `@data-error` | `error: Error` | 数据加载失败时触发 |

### 4.2 使用示例

```vue
<ArtDecoPageTemplate
  :page-config="pageConfig"
  @tab-change="handleTabChange"
  @data-loaded="handleDataLoaded"
  @data-error="handleDataError"
>
</ArtDecoPageTemplate>

<script setup>
const handleTabChange = (tabKey) => {
  console.log('切换到标签页:', tabKey)
  // 执行标签页切换逻辑
}

const handleDataLoaded = (data) => {
  console.log('数据加载完成:', data)
  // 处理加载的数据
}

const handleDataError = (error) => {
  console.error('数据加载失败:', error)
  // 处理错误
}
</script>
```

---

## 5. 方法暴露 (Expose)

模板组件暴露了以下方法，可通过 `ref` 调用：

```vue
<template>
  <ArtDecoPageTemplate ref="pageRef" :page-config="pageConfig">
    <!-- 内容 -->
  </ArtDecoPageTemplate>

  <button @click="manualRefresh">手动刷新</button>
</template>

<script setup>
import { ref } from 'vue'

const pageRef = ref()

const manualRefresh = () => {
  // 调用模板暴露的刷新方法
  pageRef.value?.refresh()
}

// 可访问的属性和方法：
// - pageRef.value.refresh()    // 刷新数据
// - pageRef.value.pageData     // 页面数据
// - pageRef.value.loading      // 加载状态
// - pageRef.value.hasError     // 错误状态
// - pageRef.value.activeTab    // 当前标签页
</script>
```

---

## 6. 样式规范

### 6.1 必须导入的样式

```vue
<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

// 你的样式
</style>
```

### 6.2 常用 SCSS 变量

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `--artdeco-gold-primary` | 主金色 | `#D4AF37` |
| `--artdeco-bg-global` | 全局背景色 | `#0A0A0A` |
| `--artdeco-bg-card` | 卡片背景色 | `#141414` |
| `--artdeco-fg-primary` | 主文字色 | `#F2F0E4` |
| `--artdeco-fg-muted` | 次要文字色 | `#A0A0A0` |
| `--artdeco-rise` | 上涨/盈利色（红） | `#FF5252` |
| `--artdeco-down` | 下跌/亏损色（绿） | `#00E676` |
| `--artdeco-spacing-4` | 间距 | `16px` |

### 6.3 金融颜色规范（A股标准）

```scss
// 盈利/上涨 - 红色
.profit { color: var(--artdeco-rise); }

// 亏损/下跌 - 绿色
.loss { color: var(--artdeco-down); }
```

---

## 7. 最佳实践

### 7.1 页面创建流程

1. **复制模板文件**
   ```bash
   cp _templates/ArtDecoPageTemplate.vue YourPage.vue
   ```

2. **配置页面参数**
   ```typescript
   const pageConfig = {
     title: '你的页面标题',
     subtitle: '页面副标题',
     apiUrl: '/api/v1/your-api',
     permission: 'artdeco:yourpage:view'
   }
   ```

3. **实现内容区**
   ```vue
   <template #content="{ data }">
     <!-- 你的业务逻辑 -->
   </template>
   ```

4. **添加路由配置**（在 `MenuConfig.ts`）
   ```typescript
   {
     path: 'your-page',
     name: 'your-page',
     component: () => import('@/views/artdeco-pages/YourPage.vue'),
     meta: {
       title: '你的页面标题',
       requiresAuth: true,
       api: '/api/v1/your-api'
     }
   }
   ```

### 7.2 性能优化建议

1. **使用缓存**
   ```typescript
   const pageConfig = {
     cacheTime: 300000  // 5分钟缓存，减少 API 调用
   }
   ```

2. **延迟加载大数据**
   ```vue
   <template #content="{ data }">
     <VirtualList :data="data.list" :item-height="50">
       <template #item="{ item }">
         <ListItem :data="item" />
       </template>
     </VirtualList>
   </template>
   ```

3. **分页处理**
   ```vue
   <template #content="{ data, refresh }">
     <DataTable :data="data.list" />
     <Pagination
       :total="data.total"
       @change="(page) => { currentPage = page; refresh() }"
     />
   </template>
   ```

---

## 8. 完整示例：风险管理页面

参见：`src/views/artdeco-pages/_templates/ExampleRiskManagement.vue`

关键特性：
- ✅ 8个统计卡片（Web3 DeFi 风格）
- ✅ 自定义标签页导航
- ✅ 行业分布可视化
- ✅ 进度条组件
- ✅ 风险预警表格
- ✅ 响应式布局

---

## 9. 常见问题

### Q: 如何禁用自动数据加载？
**A**: 不设置 `apiUrl` 即可

```typescript
const pageConfig = {
  title: '静态页面',
  permission: 'artdeco:page:view'
  // 不设置 apiUrl
}
```

### Q: 如何自定义空数据状态？
**A**: 使用 `#content` 插槽自定义

```vue
<template #content="{ data }">
  <div v-if="!data || data.length === 0" class="custom-empty">
    <ArtDecoIcon name="inbox" size="xl" />
    <p>自定义空数据提示</p>
  </div>
  <div v-else><!-- 正常内容 --></div>
</template>
```

### Q: 如何处理多个 API 请求？
**A**: 在父组件中处理，通过 `refresh` 方法触发

```vue
<script setup>
import { ref } from 'vue'

const customData = ref()

const fetchMultipleApis = async () => {
  const [res1, res2] = await Promise.all([
    api.get('/api/data1'),
    api.get('/api/data2')
  ])
  customData.value = { ...res1.data, ...res2.data }
}
</script>
```

---

## 10. 相关文档

- [ArtDeco Master Index](./ARTDECO_MASTER_INDEX.md) - 设计系统总览
- [ArtDeco Component Guide](./ARTDECO_COMPONENT_GUIDE.md) - 组件开发指南
- [ArtDeco Grid Reference](./ARTDECO_GRID_QUICK_REFERENCE.md) - 网格系统

---

**维护者**: Frontend Architecture Team
**最后更新**: 2026-02-23
**治理口径**: ArtDeco v3.1 Governance Baseline
