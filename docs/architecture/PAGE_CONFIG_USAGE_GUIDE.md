# 前端页面配置系统使用指南

## 📖 快速导航

- **[配置生成](#配置生成)** - 生成和更新页面配置
- **[配置验证](#配置验证)** - 验证配置与路由一致性
- **[类型定义](#类型定义)** - TypeScript 类型参考
- **[使用示例](#使用示例)** - 组件中如何使用配置
- **[工具脚本](#工具脚本)** - 开发和 CI/CD 工具

---

## 概述

前端页面配置系统 (`web/frontend/src/config/pageConfig.ts`) 提供：
- 集中化的路由配置管理
- API 端点和 WebSocket 频道统一配置
- 单体组件（monolithic）的多 Tab 配置
- 类型安全的配置访问

### 配置类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `page` | 标准页面配置 | 单页面路由 |
| `monolithic` | 单体组件配置 | 多 Tab 组件（如 ArtDecoMarketData） |

---

## 配置生成

### 自动生成配置

从路由配置自动生成页面配置：

```bash
cd web/frontend

# 预览生成（不写入文件）
npm run generate-page-config -- --dry-run

# 显示与当前配置的差异
npm run generate-page-config -- --diff

# 生成并写入文件
npm run generate-page-config
```

### 生成脚本选项

| 选项 | 说明 |
|------|------|
| `--dry-run` | 预览生成结果，不写入文件 |
| `--diff` | 显示与当前配置的差异 |
| `--verbose` | 显示详细输出 |
| `--help` | 显示帮助信息 |

---

## 配置验证

### 验证命令

```bash
cd web/frontend

# 验证配置（失败时退出）
npm run validate-page-config -- --fail

# 详细输出
npm run validate-page-config -- --verbose

# JSON 输出（适合 CI/CD）
npm run validate-page-config -- --json
```

### 验证检查项

1. **路由覆盖检查** - 所有路由必须有对应配置
2. **必需字段检查** - 配置必须包含 `apiEndpoint`, `wsChannel`, `component`
3. **重复路由检查** - 检测重复的路由定义
4. **残留配置检查** - 检测已删除路由的配置残留

### 退出码

| 码 | 含义 |
|----|------|
| 0 | 验证通过 |
| 1 | 验证错误（配置缺失、字段缺失） |
| 2 | 仅警告（无错误） |
| 3 | 致命错误（文件不存在等） |

---

## 类型定义

### PageConfigType

```typescript
type PageConfigType = 'page' | 'monolithic'
```

### TabConfig

```typescript
interface TabConfig {
  /** Tab 唯一标识符 */
  id: string
  /** Tab 显示标签（可选） */
  label?: string
  /** API 端点 */
  apiEndpoint?: string
  /** WebSocket 频道 */
  wsChannel?: string
}
```

### StandardPageConfig（标准页面配置）

```typescript
interface StandardPageConfig {
  /** 配置类型：标准页面 */
  type: 'page'
  /** 路由路径 */
  routePath: string
  /** 页面标题 */
  title: string
  /** 页面描述（可选） */
  description?: string
  /** API 端点 */
  apiEndpoint: string
  /** WebSocket 频道 */
  wsChannel: string
  /** 组件路径 */
  component: string
  /** 是否需要认证 */
  requiresAuth: boolean
}
```

### MonolithicPageConfig（单体组件配置）

```typescript
interface MonolithicPageConfig {
  /** 配置类型：单体组件 */
  type: 'monolithic'
  /** 路由路径 */
  routePath: string
  /** 页面标题 */
  title: string
  /** 页面描述（可选） */
  description?: string
  /** 组件路径 */
  component: string
  /** Tab 配置列表 */
  tabs: TabConfig[]
  /** 是否需要认证 */
  requiresAuth: boolean
}
```

### PageConfig（联合类型）

```typescript
type PageConfig = StandardPageConfig | MonolithicPageConfig
```

---

## 使用示例

### 基本用法

```typescript
import { PAGE_CONFIG, getPageConfig, isRouteName } from '@/config/pageConfig'

// 通过路由名称获取配置
const config = getPageConfig('market-realtime')

if (config) {
  console.log('API Endpoint:', config.apiEndpoint)
  console.log('WebSocket Channel:', config.wsChannel)
}

// 类型守卫
if (isRouteName('market-realtime')) {
  // TypeScript 知道这里 config 存在
  const config = PAGE_CONFIG['market-realtime']
}
```

### 单体组件 Tab 配置

```typescript
import { PAGE_CONFIG, isMonolithicConfig, getTabConfig } from '@/config/pageConfig'

const config = PAGE_CONFIG['market-fund-flow']

if (isMonolithicConfig(config)) {
  // config 是 MonolithicPageConfig 类型
  console.log('Component:', config.component)
  console.log('Tabs:', config.tabs)
  
  // 获取特定 Tab 的配置
  const tabConfig = getTabConfig('market-fund-flow', 'fund-flow')
  if (tabConfig) {
    console.log('Tab API:', tabConfig.apiEndpoint)
    console.log('Tab WS:', tabConfig.wsChannel)
  }
}
```

### 在组件中使用

```vue
<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { PAGE_CONFIG, getPageConfig, isMonolithicConfig } from '@/config/pageConfig'
import { useRoute } from 'vue-router'
import { marketService } from '@/services/marketService'

const route = useRoute()
const routeName = route.name as string

// 获取当前路由的配置
const config = getPageConfig(routeName)

const data = ref<any>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// 根据配置加载数据
const loadData = async () => {
  if (!config) {
    error.value = 'Configuration not found'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    if (isMonolithicConfig(config)) {
      // 单体组件：从 Tab 配置获取 API
      const activeTab = route.meta.activeTab
      const tabConfig = config.tabs.find(t => t.id === activeTab)
      
      if (tabConfig?.apiEndpoint) {
        data.value = await marketService.fetchFromEndpoint(tabConfig.apiEndpoint)
      }
    } else {
      // 标准页面：从配置获取 API
      if (config.apiEndpoint) {
        data.value = await marketService.fetchFromEndpoint(config.apiEndpoint)
      }
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
```

### WebSocket 订阅

```typescript
import { PAGE_CONFIG, getPageConfig } from '@/config/pageConfig'
import { useWebSocket } from '@/composables/useWebSocket'

const config = getPageConfig('market-realtime')

if (config) {
  // 使用配置的 WebSocket 频道
  const { subscribe, unsubscribe } = useWebSocket()
  
  // 订阅实时数据
  subscribe(config.wsChannel, (data) => {
    console.log('Received:', data)
  })
  
  // 离开时取消订阅
  onUnmounted(() => {
    unsubscribe(config.wsChannel)
  })
}
```

---

## 预提交钩子

配置验证已集成到预提交钩子中：

```yaml
# .pre-commit-config.yaml
- id: page-config-validator
  name: Page Configuration Validator
  entry: bash -c "cd web/frontend && node ../../scripts/hooks/check-page-config.mjs --warn || true"
  language: system
  files: ^web/frontend/src/(router/|config/)/
  stages: [pre-commit]
  always_run: true
```

### 钩子行为

- **检测到问题**：输出警告，不阻塞提交
- **文件不存在**：输出错误，不阻塞提交
- **验证通过**：静默通过

---

## 工具脚本

### 文件位置

| 脚本 | 路径 |
|------|------|
| 配置生成 | `scripts/dev/tools/generate-page-config.js` |
| 配置验证 | `scripts/hooks/check-page-config.mjs` |

### 直接运行

```bash
# 生成配置
node scripts/dev/tools/generate-page-config.js --dry-run

# 验证配置
node scripts/hooks/check-page-config.mjs --fail --verbose
```

---

## 最佳实践

### 1. 添加新路由时

1. 在 `router/index.ts` 添加路由定义
2. 运行 `npm run generate-page-config` 生成配置
3. 运行 `npm run validate-page-config` 验证
4. 提交更改

### 2. 修改 API 端点时

1. 更新对应路由的 API 端点配置
2. 运行验证确保配置完整
3. 提交更改

### 3. 添加新单体组件时

1. 在 `scripts/dev/tools/generate-page-config.js` 的 `CONFIG.routeConfigMap` 中添加配置
2. 在 `CONFIG.monolithicTabs` 中添加 Tab 配置
3. 生成并验证配置

---

## 常见问题

### Q: 配置生成后报错 "Configuration not found"

**A**: 确保路由名称与配置键名一致。路由名称来自 `router/index.ts` 中的 `name` 字段。

### Q: 单体组件的 Tab 切换不工作

**A**: 确保在路由的 `meta.activeTab` 中正确定义 Tab ID，并在组件中使用 `route.meta.activeTab` 获取当前 Tab。

### Q: 验证提示 "Missing Configurations"

**A**: 运行 `npm run generate-page-config` 重新生成配置，然后检查生成的配置是否正确。

---

## 相关文档

- [路由配置文档](../../web/frontend/src/router/index.ts)
- [ArtDeco 组件集成指南](../guides/frontend/mystocks-artdeco-integration-fix.md)
- [TypeScript 最佳实践](../guides/typescript/Typescript_BEST_PRACTICES.md)

---

**最后更新**: 2026-01-28
**版本**: 1.0
**状态**: ✅ 生产就绪
