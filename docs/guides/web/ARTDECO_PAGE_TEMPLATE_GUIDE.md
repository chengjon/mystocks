# ArtDeco 标准页面模板使用指南

> **状态**: 2026-04-01 已按当前代码复核
> **适用**: 使用 `ArtDecoPageTemplate.vue` 的标准工作台页面
> **目标**: 说明模板化工作台何时使用、如何接入，以及它与其他页面承载模式的边界

---

## 1. 先明确边界

`ArtDecoPageTemplate.vue` 是当前 ArtDeco 页面体系中的 **一种** 承载模式，不是所有页面的唯一模板。

当前运行时并存三种模式：

1. **模板化工作台**
   例如 `ArtDecoRiskManagement.vue`
2. **直接 Tab 容器**
   例如 `ArtDecoMarketData.vue`
3. **功能树驱动总控容器**
   例如 `ArtDecoTradingCenter.vue`

### 1.1 什么时候适合用模板

适合以下场景：

- 页面需要统一的 `header / stats / tabs / content / footer` 节奏
- 页面数据加载可以通过单一 `pageConfig` 驱动
- 页面属于标准工作台，而不是总控台或高度定制容器

### 1.2 什么时候不该硬套模板

不适合以下场景：

- 页面本身是总控入口，需要功能树或复杂 orchestration
- 页面历史上已经形成稳定的直接 Tab 容器形态
- 页面需要双态承载（独立路由态 + 内嵌态）且模板反而增加复杂度

---

## 2. 最小可用示例

```vue
<template>
  <ArtDecoPageTemplate
    :page-config="pageConfig"
    :stats="stats"
    :tabs="tabs"
    default-tab="overview"
    @data-loaded="handleDataLoaded"
    @tab-change="handleTabChange"
  >
    <template #header-actions>
      <ArtDecoButton variant="outline" size="sm" @click="handleExport">
        导出
      </ArtDecoButton>
    </template>

    <template #content="{ activeTab, data }">
      <OverviewPanel v-if="activeTab === 'overview'" :data="data" />
      <DetailPanel v-else :data="data" />
    </template>
  </ArtDecoPageTemplate>
</template>

<script setup lang="ts">
import ArtDecoPageTemplate from '@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue'

const pageConfig = {
  title: '风险管理中心',
  subtitle: '实时监控投资组合风险与预警状态',
  showStatus: true,
  showRefresh: true,
  showStats: true,
  showTabs: true,
  showTraceId: true,
  apiUrl: '/api/risk/overview',
  permission: '',
  cacheTime: 300000,
}
</script>
```

---

## 3. `ArtDecoPageConfig` 当前字段

当前源码定义见：
`web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts`

| 字段 | 类型 | 作用 |
|------|------|------|
| `title` | `string` | 页面标题 |
| `subtitle` | `string` | 页面副标题 |
| `showStatus` | `boolean` | 是否显示状态位 |
| `statusText` | `string` | 自定义状态文本 |
| `statusType` | `success / warning / error / info` | 状态样式 |
| `showRefresh` | `boolean` | 是否显示默认刷新按钮 |
| `showStats` | `boolean` | 是否启用统计区 |
| `showTabs` | `boolean` | 是否启用 tabs 区 |
| `showTraceId` | `boolean` | 是否显示 `REQ_ID` |
| `apiUrl` | `string` | 数据接口地址 |
| `apiMethod` | `GET / POST` | 请求方法 |
| `apiParams` | `Record<string, unknown>` | 请求参数 |
| `skeleton` | `{ columns?, rows? }` | 骨架屏配置 |
| `emptyMessage` | `string` | 空数据提示 |
| `permission` | `string` | 权限标识；可为空字符串 |
| `cacheTime` | `number` | 缓存时间（ms） |

---

## 4. 插槽与事件

### 4.1 可用插槽

| 插槽 | 用途 |
|------|------|
| `header-actions` | 头部操作区 |
| `stats` | 自定义统计区 |
| `tabs` | 自定义 tabs rail |
| `content` | 主内容区 |
| `footer` | 页面底部 |

### 4.2 `#content` 作用域参数

`#content` 当前会拿到：

- `data`
- `loading`
- `activeTab`
- `refresh`

### 4.3 可用事件

| 事件 | 参数 |
|------|------|
| `tab-change` | `tabKey: string` |
| `data-loaded` | `data: unknown` |
| `data-error` | `error: Error` |

---

## 5. 样式规则

### 5.1 新代码写法

```scss
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-grid.scss' as *;
```

不要在新代码里继续扩散：

- `@import '@/styles/artdeco-tokens'`
- 硬编码颜色 / 间距 / 阴影 / 过渡

### 5.2 A 股语义颜色

```scss
.profit {
  color: var(--artdeco-rise);
}

.loss {
  color: var(--artdeco-down);
}
```

---

## 6. 页面接入流程

1. 先判断该页面是否真的适合模板化工作台。
2. 创建页面文件，并在其中 `import ArtDecoPageTemplate`。
3. 定义 `pageConfig`、`stats`、`tabs`。
4. 通过插槽实现领域内容，不要直接改模板内部。
5. 在路由中接入，必要时再补 `pageConfig.ts` 元信息。

### 6.1 不建议的做法

- 复制模板文件并直接改模板本体
- 把页面专属逻辑塞进模板公共层
- 为了套模板而牺牲页面原本更合适的承载模式

---

## 7. Do / Don't

### 推荐

- 用模板承载标准工作台页面
- 用 `tabs shell -> content shell` 维持页面节奏
- 让页面代码负责业务内容，模板负责壳层
- 用 `cacheTime` 控制重复拉取节奏

### 避免

- 把所有 ArtDeco 页面都强行模板化
- 在模板页里继续写旧 `@import`
- 把总控台页面误改成模板页
- 把模板页误当成组件目录治理文档

---

## 8. 相关文档

- [ARTDECO_START_HERE](./ARTDECO_START_HERE.md)
- [ARTDECO_MASTER_INDEX](./ARTDECO_MASTER_INDEX.md)
- [ARTDECO_FINTECH_UNIFIED_SPEC](./ARTDECO_FINTECH_UNIFIED_SPEC.md)
- [ARTDECO_COMPONENT_GUIDE](./ARTDECO_COMPONENT_GUIDE.md)
- [ARTDECO_GRID_QUICK_REFERENCE](./ARTDECO_GRID_QUICK_REFERENCE.md)
- [ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT](./ARTDECO_FINTECH_PAGE_COMPOSITION_AUDIT.md)

---

**维护者**: Frontend Architecture Team
**最后更新**: 2026-04-01
**治理口径**: ArtDeco Fintech 当前统一规格
