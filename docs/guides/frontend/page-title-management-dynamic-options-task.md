# 前端路由优化 - Page Title Management 动态选项任务方案

## 任务概述

**任务名称**: 页面标题管理动态选项实现
**优先级**: 高
**预计时间**: 3-4小时
**风险等级**: 中等（涉及路由和组件集成）
**依赖项**: Vue Router, 现有的路由配置

## 任务背景

当前页面标题管理系统较为基础：
- ✅ 路由配置中有静态title设置
- ✅ 路由守卫中有基本的标题更新逻辑
- ❌ 缺少动态标题管理功能
- ❌ 缺少Meta标签管理
- ❌ 缺少用户状态相关的标题定制
- ❌ 缺少面包屑导航标题支持

目标：实现完整的动态页面标题管理系统，支持基于用户状态、数据内容和导航上下文的智能标题管理。

## 当前状态分析

### 已有的标题管理
- **路由Meta配置**: 所有路由都有静态title设置
- **路由守卫**: 基本的标题更新逻辑 `document.title = ${title} - MyStocks Platform`
- **覆盖范围**: 77个路由配置都有title设置

### 缺失的功能需求

#### 1. **动态标题生成**
基于用户状态、数据内容、路由参数的智能标题

#### 2. **Meta标签管理**
完整的SEO Meta标签支持（description, keywords, og:*等）

#### 3. **标题模板系统**
支持变量插值和条件渲染的标题模板

#### 4. **面包屑标题集成**
与面包屑导航系统的标题同步

#### 5. **用户个性化**
基于用户偏好和角色的标题定制

## 实施步骤

### 步骤1: 创建标题管理服务
**目标**: 实现核心的标题管理逻辑
**文件位置**: `web/frontend/src/services/titleManager.ts`

```typescript
interface TitleConfig {
  title: string
  subtitle?: string
  separator?: string
  suffix?: string
  dynamic?: boolean
}

interface MetaConfig {
  description?: string
  keywords?: string[]
  author?: string
  ogTitle?: string
  ogDescription?: string
  ogImage?: string
  ogType?: string
}

class TitleManager {
  private defaultConfig: TitleConfig = {
    title: 'MyStocks',
    subtitle: '',
    separator: ' - ',
    suffix: 'Platform',
    dynamic: false
  }

  private metaTags: MetaConfig = {}

  // 设置页面标题
  setTitle(config: Partial<TitleConfig> | string): void {
    const finalConfig = typeof config === 'string'
      ? { ...this.defaultConfig, title: config }
      : { ...this.defaultConfig, ...config }

    const parts = [
      finalConfig.title,
      finalConfig.subtitle,
      finalConfig.suffix
    ].filter(Boolean)

    const title = parts.join(finalConfig.separator)
    document.title = title
  }

  // 设置Meta标签
  setMeta(config: MetaConfig): void {
    this.metaTags = { ...this.metaTags, ...config }

    // 更新或创建meta标签
    this.updateMetaTag('description', config.description)
    this.updateMetaTag('keywords', config.keywords?.join(', '))
    this.updateMetaTag('author', config.author)

    // Open Graph
    this.updateMetaTag('og:title', config.ogTitle, 'property')
    this.updateMetaTag('og:description', config.ogDescription, 'property')
    this.updateMetaTag('og:image', config.ogImage, 'property')
    this.updateMetaTag('og:type', config.ogType, 'property')
  }

  private updateMetaTag(name: string, content?: string, attribute: string = 'name'): void {
    if (!content) return

    let element = document.querySelector(`meta[${attribute}="${name}"]`) as HTMLMetaElement
    if (!element) {
      element = document.createElement('meta')
      element.setAttribute(attribute, name)
      document.head.appendChild(element)
    }
    element.content = content
  }

  // 重置为默认标题
  reset(): void {
    this.setTitle(this.defaultConfig)
    this.setMeta({})
  }
}

export const titleManager = new TitleManager()
```

### 步骤2: 实现动态标题生成器
**目标**: 支持变量插值和条件逻辑的标题模板
**文件位置**: `web/frontend/src/services/titleGenerator.ts`

```typescript
interface TitleContext {
  user?: {
    username?: string
    role?: string
  }
  route?: {
    params: Record<string, string>
    query: Record<string, string>
    name?: string
  }
  data?: Record<string, any>
}

class TitleGenerator {
  // 模板变量替换
  generate(template: string, context: TitleContext = {}): string {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return this.getValue(key, context) || match
    })
  }

  private getValue(key: string, context: TitleContext): string | undefined {
    // 用户相关
    if (key.startsWith('user.')) {
      const userKey = key.split('.')[1]
      return context.user?.[userKey as keyof typeof context.user]
    }

    // 路由参数
    if (key.startsWith('route.')) {
      const routeKey = key.split('.')[1]
      if (routeKey === 'params') return JSON.stringify(context.route?.params)
      if (routeKey === 'query') return JSON.stringify(context.route?.query)
      return context.route?.[routeKey as keyof typeof context.route]
    }

    // 数据字段
    if (key.startsWith('data.')) {
      const dataKey = key.split('.')[1]
      return context.data?.[dataKey]
    }

    // 预定义变量
    const predefined = {
      app: 'MyStocks',
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString()
    }

    return predefined[key as keyof typeof predefined]
  }

  // 条件标题生成
  generateConditional(
    conditions: Array<{ condition: (context: TitleContext) => boolean, template: string }>,
    context: TitleContext
  ): string {
    for (const { condition, template } of conditions) {
      if (condition(context)) {
        return this.generate(template, context)
      }
    }
    return 'MyStocks'
  }
}

export const titleGenerator = new TitleGenerator()
```

### 步骤3: 增强路由标题管理
**目标**: 在路由配置中支持动态标题模板
**文件位置**: `web/frontend/src/router/index.ts`

```typescript
// 扩展路由Meta类型
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    breadcrumb?: string
    requiresAuth?: boolean
    titleTemplate?: string  // 新增：标题模板
    titleContext?: (route: RouteLocationNormalized) => TitleContext  // 新增：上下文生成器
    metaConfig?: MetaConfig  // 新增：Meta配置
  }
}

// 增强的路由守卫
router.beforeEach(async (to, from, next) => {
  // 认证检查
  const authStore = useAuthStore()
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // 网络状态检查
  if (to.meta.requiresNetwork !== false && !navigator.onLine) {
    next({ name: 'networkError' })
    return
  }

  // 动态标题设置
  await updatePageTitle(to)

  next()
})

async function updatePageTitle(route: RouteLocationNormalized): Promise<void> {
  const meta = route.meta

  if (meta.titleTemplate) {
    // 使用动态标题模板
    const context = meta.titleContext ? meta.titleContext(route) : {}
    const title = titleGenerator.generate(meta.titleTemplate, context)
    titleManager.setTitle({ title, dynamic: true })
  } else if (meta.title) {
    // 使用静态标题
    titleManager.setTitle(meta.title)
  } else {
    // 使用默认标题
    titleManager.reset()
  }

  // 设置Meta标签
  if (meta.metaConfig) {
    titleManager.setMeta(meta.metaConfig)
  }
}
```

### 步骤4: 创建标题Composable
**目标**: 提供Vue组件中使用动态标题的便捷方式
**文件位置**: `web/frontend/src/composables/usePageTitle.ts`

```typescript
import { watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { titleManager, titleGenerator } from '@/services/titleManager'
import type { TitleConfig, MetaConfig, TitleContext } from '@/services/titleManager'

export function usePageTitle() {
  const route = useRoute()

  // 设置页面标题
  const setTitle = (config: Partial<TitleConfig> | string) => {
    titleManager.setTitle(config)
  }

  // 设置Meta标签
  const setMeta = (config: MetaConfig) => {
    titleManager.setMeta(config)
  }

  // 生成动态标题
  const generateTitle = (template: string, context?: TitleContext) => {
    return titleGenerator.generate(template, context)
  }

  // 基于数据更新标题
  const updateTitleFromData = (
    data: any,
    template: string,
    dataKey: string = 'name'
  ) => {
    if (data && data[dataKey]) {
      const title = titleGenerator.generate(template, {
        data: { [dataKey]: data[dataKey] }
      })
      setTitle(title)
    }
  }

  // 监听数据变化自动更新标题
  const watchDataForTitle = (
    dataRef: Ref<any>,
    template: string,
    dataKey: string = 'name'
  ) => {
    watch(dataRef, (newData) => {
      updateTitleFromData(newData, template, dataKey)
    }, { immediate: true })
  }

  // 重置标题
  const resetTitle = () => {
    titleManager.reset()
  }

  return {
    setTitle,
    setMeta,
    generateTitle,
    updateTitleFromData,
    watchDataForTitle,
    resetTitle
  }
}
```

### 步骤5: 集成到路由配置
**目标**: 为关键路由添加动态标题模板
**文件位置**: `web/frontend/src/router/index.ts`

```typescript
// 股票详情页 - 动态标题
{
  path: 'stock-detail/:symbol',
  name: 'stock-detail',
  component: () => import('@/views/StockDetail.vue'),
  props: true,
  meta: {
    title: '股票详情',
    icon: 'Document',
    titleTemplate: '{{data.symbol}} - 股票详情',
    titleContext: (route) => ({
      data: { symbol: route.params.symbol }
    }),
    metaConfig: {
      description: '查看股票详细信息、技术指标和历史数据',
      keywords: ['股票', '行情', '技术分析', 'K线图']
    }
  }
},

// 用户仪表盘 - 个性化标题
{
  path: 'dashboard',
  name: 'dashboard',
  component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
  meta: {
    title: '仪表盘',
    icon: 'Odometer',
    titleTemplate: '{{user.username}}的仪表盘 - MyStocks',
    titleContext: () => ({
      user: { username: '访客' } // 实际会从store获取
    }),
    metaConfig: {
      description: '个人投资仪表盘，查看市场概览和投资组合',
      keywords: ['仪表盘', '投资组合', '市场概览']
    }
  }
},

// 策略详情页 - 基于数据的动态标题
{
  path: 'strategy/:id',
  name: 'strategy-detail',
  component: () => import('@/views/StrategyDetail.vue'),
  meta: {
    title: '策略详情',
    icon: 'Management',
    titleTemplate: '{{data.name}} - 量化策略',
    titleContext: async (route) => {
      // 这里可以异步获取策略数据
      try {
        const strategyData = await getStrategyById(route.params.id)
        return { data: { name: strategyData.name } }
      } catch {
        return { data: { name: '未知策略' } }
      }
    }
  }
}
```

### 步骤6: Vue组件集成示例
**目标**: 演示如何在Vue组件中使用动态标题
**文件位置**: `web/frontend/src/views/StockDetail.vue`

```vue
<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePageTitle } from '@/composables/usePageTitle'

const route = useRoute()
const { updateTitleFromData, watchDataForTitle, setMeta } = usePageTitle()

const stockData = ref(null)

// 页面加载时设置标题
onMounted(async () => {
  const symbol = route.params.symbol
  stockData.value = await fetchStockData(symbol)

  // 更新标题为股票名称
  updateTitleFromData(stockData.value, '{{data.name}} ({{data.symbol}}) - 股票详情')

  // 设置Meta标签
  setMeta({
    description: `查看${stockData.value.name}(${stockData.value.symbol})的实时行情、技术指标和历史数据`,
    keywords: ['股票', stockData.value.name, stockData.value.symbol, '技术分析'],
    ogTitle: `${stockData.value.name}股票详情 - MyStocks`,
    ogDescription: `${stockData.value.name}实时股价、K线图和技术指标分析`,
    ogType: 'website'
  })
})

// 监听股票数据变化，自动更新标题
watchDataForTitle(stockData, '{{data.name}}({{data.symbol}}) - 股票详情')
</script>
```

## 测试验证

### 功能测试
- [ ] **静态标题**: 路由配置的静态标题正确显示
- [ ] **动态标题**: 基于数据的标题正确生成和更新
- [ ] **Meta标签**: SEO Meta标签正确设置
- [ ] **模板变量**: 变量插值功能正常工作
- [ ] **条件标题**: 条件渲染标题功能正常

### 集成测试
- [ ] **路由守卫**: 导航时标题自动更新
- [ ] **组件集成**: usePageTitle composable正常工作
- [ ] **数据监听**: 数据变化时标题自动更新
- [ ] **用户状态**: 用户登录状态影响标题显示

### SEO测试
- [ ] **页面标题**: document.title正确设置
- [ ] **Meta description**: description标签正确设置
- [ ] **Open Graph**: 社交媒体分享标签正确设置
- [ ] **搜索引擎**: 标题在浏览器标签页正确显示

## 验收标准

### 功能验收
- [ ] 页面标题根据路由和数据动态更新
- [ ] Meta标签为SEO优化正确设置
- [ ] 标题模板系统支持变量插值
- [ ] Vue组件可以方便地控制页面标题

### 用户体验验收
- [ ] 标题清晰准确反映页面内容
- [ ] 浏览器标签页显示有意义的标题
- [ ] 社交媒体分享显示正确的预览信息

### 技术验收
- [ ] TypeScript类型定义完整
- [ ] 标题管理系统与路由系统正确集成
- [ ] 性能影响最小（非阻塞操作）

---

*文档创建时间*: 2026-01-12
*预计完成时间*: 2026-01-13 (4小时内)
*负责人*: Claude Code
*审查人*: 项目维护者