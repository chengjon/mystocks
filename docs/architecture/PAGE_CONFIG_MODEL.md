# 前端扩展配置模型架构文档

**最后更新**: 2026-01-28
**版本**: 2.0
**状态**: ✅ 生产就绪

---

## 概述

本文档描述前端配置系统的扩展模型，支持：
- 标准页面配置（`page` 类型）
- 单体组件多 Tab 配置（`monolithic` 类型）
- 类型安全的配置访问
- 自动化的配置生成和验证

### 设计目标

1. **消除硬编码** - 所有 API 端点和 WebSocket 频道集中管理
2. **类型安全** - TypeScript 编译时检查配置访问
3. **易于维护** - 单点配置变更影响所有使用处
4. **自动化** - 配置生成和验证脚本

---

## 架构设计

### 配置模型

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAGE_CONFIG                                  │
│              (统一配置入口点)                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐   │
│  │  PAGE_CONFIGS   │    │     MONOLITHIC_CONFIGS          │   │
│  │  (标准页面)     │    │     (单体组件多Tab)             │   │
│  │                 │    │                                 │   │
│  │  - dashboard    │    │  - market-fund-flow           │   │
│  │  - trading-*    │    │    └─ tabs:                   │   │
│  │  - risk-*       │    │      - fund-flow             │   │
│  │  - system-*     │    │      - etf                   │   │
│  │                 │    │      - concepts              │   │
│  └─────────────────┘    │      - lhb                    │   │
│                        │      - auction                │   │
│                        │      - institution           │   │
│                        └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 配置类型

| 类型 | 接口 | 用途 |
|------|------|------|
| `page` | `StandardPageConfig` | 单页面路由 |
| `monolithic` | `MonolithicPageConfig` | 多 Tab 组件 |

---

## 文件结构

```
web/frontend/src/
├── config/
│   └── pageConfig.ts          # 统一配置入口
├── types/
│   └── pageConfig.ts         # 类型定义
├── router/
│   └── index.ts             # 路由定义
└── views/
    └── artdeco-pages/       # ArtDeco 组件
```

### 核心文件

| 文件 | 职责 |
|------|------|
| `config/pageConfig.ts` | 配置对象、辅助函数、类型导出 |
| `types/pageConfig.ts` | TypeScript 类型定义 |
| `router/index.ts` | 路由定义（配置来源） |

---

## 类型定义

### 联合类型

```typescript
type PageConfig = StandardPageConfig | MonolithicPageConfig
```

### 标准页面配置

```typescript
interface StandardPageConfig {
  type: 'page'
  routePath: string
  title: string
  description?: string
  apiEndpoint: string
  wsChannel: string
  component: string
  requiresAuth: boolean
}
```

### 单体组件配置

```typescript
interface MonolithicPageConfig {
  type: 'monolithic'
  routePath: string
  title: string
  description?: string
  component: string
  tabs: TabConfig[]
  requiresAuth: boolean
}

interface TabConfig {
  id: string
  label?: string
  apiEndpoint?: string
  wsChannel?: string
}
```

---

## 使用模式

### 模式 1：标准页面

```
路由: /market/realtime → name: market-realtime
       ↓
配置: PAGE_CONFIG['market-realtime'] (StandardPageConfig)
       ↓
组件: ArtDecoMarketQuotes.vue
       ↓
API: /api/market/realtime
       ↓
WS: market:realtime
```

### 模式 2：单体组件

```
路由: /market/fund-flow → name: market-fund-flow, meta.activeTab: fund-flow
       ↓
配置: PAGE_CONFIG['market-fund-flow'] (MonolithicPageConfig)
       ↓
组件: ArtDecoMarketData.vue
       ↓
Tab: config.tabs.find(t => t.id === 'fund-flow')
       ↓
API: /api/market/fund-flow
       ↓
WS: market:fund-flow
```

---

## 辅助函数

### getPageConfig

```typescript
function getPageConfig(routeName: string): PageConfig | undefined
```

获取路由的配置，不存在返回 `undefined`。

### getTabConfig

```typescript
function getTabConfig(routeName: string, tabId: string): TabConfig | undefined
```

获取单体组件特定 Tab 的配置。

### isMonolithicConfig

```typescript
function isMonolithicConfig(config: PageConfig): config is MonolithicPageConfig
```

类型守卫，判断是否为单体组件配置。

### isStandardConfig

```typescript
function isStandardConfig(config: PageConfig): config is StandardPageConfig
```

类型守卫，判断是否为标准页面配置。

### isRouteName

```typescript
function isRouteName(name: string): name is keyof typeof PAGE_CONFIG
```

类型守卫，检查字符串是否为有效的路由名称。

---

## 工具脚本

### 配置生成

**脚本**: `scripts/tools/generate-page-config.js`

```bash
# 预览生成
npm run generate-page-config -- --dry-run

# 生成并备份当前配置
npm run generate-page-config
```

### 配置验证

**脚本**: `scripts/hooks/check-page-config.mjs`

```bash
# 验证（失败时退出）
npm run validate-page-config -- --fail

# 详细输出
npm run validate-page-config -- --verbose
```

### 预提交钩子

```yaml
# .pre-commit-config.yaml
- id: page-config-validator
  entry: bash -c "cd web/frontend && node ../../scripts/hooks/check-page-config.mjs --warn || true"
  language: system
  files: ^web/frontend/src/(router/|config/)/
  stages: [pre-commit]
```

---

## 组件集成

### 在 Vue 组件中使用

```vue
<script setup lang="ts">
import { getPageConfig, isMonolithicConfig } from '@/config/pageConfig'
import { useRoute } from 'vue-router'

const route = useRoute()
const config = getPageConfig(route.name as string)

if (config) {
  if (isMonolithicConfig(config)) {
    // 使用 config.tabs
    const activeTab = config.tabs.find(t => t.id === route.meta.activeTab)
  } else {
    // 使用 config.apiEndpoint
    const data = await fetchData(config.apiEndpoint)
  }
}
</script>
```

### 在 Store 中使用

```typescript
import { PAGE_CONFIG, getPageConfig } from '@/config/pageConfig'
import { defineStore } from 'pinia'

export const useMarketStore = defineStore('market', {
  actions: {
    async fetchData(routeName: string) {
      const config = getPageConfig(routeName)
      if (config?.apiEndpoint) {
        return await apiClient.get(config.apiEndpoint)
      }
    }
  }
})
```

---

## 配置覆盖

### 计算公式

```
覆盖率 = (已配置路由数 / 总路由数) × 100%
```

### 当前状态

| 指标 | 数值 |
|------|------|
| 总路由数 | 33 |
| 已配置路由 | 8 |
| 覆盖率 | 24% |

### 提升覆盖率的计划

1. 运行配置生成脚本：`npm run generate-page-config`
2. 验证配置：`npm run validate-page-config`
3. 手动补充缺失的 API/WebSocket 配置

---

## 与现有系统的集成

### 与 Router 集成

- 路由定义在 `router/index.ts`
- 配置从路由 `name` 属性派生
- 支持 `meta.activeTab` 用于单体组件

### 与 Services 集成

```typescript
import { getPageConfig } from '@/config/pageConfig'

class MarketService {
  async getData(routeName: string) {
    const config = getPageConfig(routeName)
    if (config?.apiEndpoint) {
      return this.client.get(config.apiEndpoint)
    }
    throw new Error('No API endpoint configured')
  }
}
```

### 与 WebSocket 集成

```typescript
import { getPageConfig } from '@/config/pageConfig'
import { useWebSocket } from '@/composables/useWebSocket'

function useMarketWebSocket(routeName: string) {
  const config = getPageConfig(routeName)
  const { subscribe } = useWebSocket()
  
  if (config?.wsChannel) {
    return subscribe(config.wsChannel)
  }
}
```

---

## 最佳实践

### 1. 添加新路由

1. 在 `router/index.ts` 添加路由（设置 `name`）
2. 运行 `npm run generate-page-config`
3. 验证 `npm run validate-page-config`
4. 提交更改

### 2. 修改 API 端点

1. 更新 `scripts/tools/generate-page-config.js` 中的 `CONFIG.routeConfigMap`
2. 重新生成配置
3. 验证

### 3. 添加新单体组件

1. 在 `router/index.ts` 添加路由
2. 在 `CONFIG.monolithicTabs` 添加 Tab 配置
3. 生成并验证

---

## 常见问题

### Q: 路由名称与配置键名不一致？

A: 确保路由的 `name` 属性与配置键名完全一致。配置键名来自路由的 `name`。

### Q: 单体组件的 Tab 切换？

A: 确保路由的 `meta.activeTab` 正确定义，并在组件中使用它来查找对应的 Tab 配置。

### Q: 验证失败怎么办？

A: 1. 运行 `npm run generate-page-config` 重新生成
2. 检查 `scripts/tools/generate-page-config.js` 中的配置映射
3. 手动补充缺失配置

---

## 相关文档

- [使用指南](../guides/PAGE_CONFIG_USAGE_GUIDE.md)
- [路由配置](../guides/ROUTER_SIMPLIFICATION_EXPLANATION.md)
- [配置生成脚本](../../scripts/tools/generate-page-config.js)
- [验证脚本](../../scripts/hooks/check-page-config.mjs)

---

**维护者**: Frontend Team
**问题反馈**: 请创建 Issue 或联系架构师
