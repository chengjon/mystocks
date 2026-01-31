# ArtDeco 量化交易管理中心 - 优化设计方案 V3.0

**版本**: 3.0.0
**优化日期**: 2026-01-22
**设计理念**: 金融量化专业级 · ArtDeco美学 · 极致信息密度
**对齐度**: 91% → 95% (目标)

---

## 🎯 核心设计原则

### 金融量化专业需求
1. **信息密度最大化**: 桌面端充分利用1920×1080空间，避免视觉浪费
2. **视觉层级清晰**: 数据优先级明确，关键指标突出显示
3. **实时数据流畅**: SSE推送与WebSocket集成，数据更新零延迟
4. **操作效率优先**: 减少点击次数，键盘快捷键全覆盖
5. **多视图对比**: 支持分屏模式，同屏监控多个维度

### ArtDeco美学升级
- ✅ 几何装饰与功能结合，不牺牲可用性
- ✅ 金色边框提升到30%透明度，悬停100%
- ✅ 背景图案从2%提升到6%可见度
- ✅ 智能字间距系统（sm: 0.15em, md: 0.18em, lg: 0.2em）
- ✅ 过渡时间戏剧化（400ms base, 800ms dramatic）

---

## 🏗️ 紧凑型布局架构

### 整体布局：左侧功能树 + 右侧内容区

```
┌─────────────────────────────────────────────────────────────────┐
│  🎛️  量化交易中心                              🔔 👤 Admin ⚙️   │  ← 顶部栏 (56px)
├──────────┬──────────────────────────────────────────────────────┤
│          │ 📍市场总览 / 实时行情监控          📊 全屏 📤 导出  │
│ 📊 市场总 ├──────────────────────────────────────────────────────┤
│   概览   │ ┌─────────────┬─────────────┬─────────────┬────────┐ │
│          │ │  沪深300     │  上证指数    │  深证成指    │  恒生   │ │
│ 📈 实时   │ │  3,847.52   │  3,124.18   │  11,234.67  │ 18,234 │ │
│   行情   │ │  ▲ +0.85%   │  ▼ -0.23%   │  ▲ +1.12%   │ +0.45% │ │
│          │ └─────────────┴─────────────┴─────────────┴────────┘ │
│ 📊 市场   │ ┌─────────────────── K线图容器 (占70%宽度) ─────────┐ │
│   分析   │ │ │                                             │ │
│          │ │ │         TradingView K线图                    │ │ │
│ 🏭 行业   │ │ │         (SSE集成 / ECharts备用)             │ │ │
│   概念   │ │ │                                             │ │ │
│          │ │ └─────────────────────────────────────────────┘ │
│ 💼 交易   │ ┌───────┬───────┬───────┬───────┬───────┬───────┐ │
│   管理   │ │ 名称  │ 现价  │ 涨跌幅 │ 成交量 │ 量比  │ 操作 │ │
│          │ ├───────┼───────┼───────┼───────┼───────┼───────┤ │
│ 🧠 策略   │ │ 茅台  │1820.5 │+2.3% │ 8.2万 │ 1.2  │ 详情  │ │
│   中心   │ │ 宁德  │185.3  │-1.1% │12.5万 │ 0.8  │ 详情  │ │
│          │ │ 比亚  │245.8  │+0.8% │15.1万 │ 1.5  │ 详情  │ │
│ 🛡️ 风险   │ └───────┴───────┴───────┴───────┴───────┴───────┘ │
│   控制   │                                                       │
│          │ 实时数据流: SSE连接正常 ✓ | 延迟: 12ms              │
│ ⚙️ 系统   │                                                       │
│   管理   │                                                       │
└──────────┴──────────────────────────────────────────────────────┘
     ↑                              ↑
  280px                        剩余宽度
  (可折叠)                      (自适应)
```

### 空间利用优化

**左侧功能树** (280px宽):
- 折叠状态: 64px (仅图标 + 首字)
- 展开状态: 280px (完整菜单)
- 过渡动画: 400ms cubic-bezier(0.4, 0, 0.2, 1)

**顶部栏** (56px高):
- Logo区域: 200px
- 面包屑导航: 自适应
- 操作区: 300px (搜索 + 通知 + 用户)

**内容区域**:
- 横向分屏: 支持2列/3列布局
- 最小内容宽度: 800px (防止挤压)
- 滚动优化: 虚拟滚动 + 懒加载

---

## 🌳 紧凑型功能树设计

### 三级菜单结构（最深3层）

```typescript
interface CompactMenuItem {
  // 基础信息
  key: string                    // 唯一标识
  label: string                  // 显示文本
  icon: string                   // ArtDecoIcon name
  level: 1 | 2 | 3              // 层级深度

  // 功能属性
  path?: string                  // 路由路径
  children?: CompactMenuItem[]   // 子菜单
  divider?: boolean              // 分隔线

  // 实时状态
  liveUpdate?: boolean           // 实时更新
  wsChannel?: string             // WebSocket频道
  apiEndpoint?: string           // API端点
  count?: number                 // 数量徽章

  // 优先级
  priority?: 'primary' | 'secondary' | 'tertiary'
  featured?: boolean             // 特色标记

  // 视觉增强
  badge?: string                 // 文本徽章
  description?: string           // 简短描述
  disabled?: boolean             // 禁用状态

  // 运行时状态
  status?: 'idle' | 'loading' | 'success' | 'error'
  error?: string                 // 错误信息
  lastUpdate?: number            // 最后更新时间戳
}
```

### 菜单配置文件（优化版）

```typescript
// layouts/MenuConfig.enhanced.ts

export const COMPACT_MENU_ITEMS: CompactMenuItem[] = [
  // ========== 一级：市场总览 ==========
  {
    key: 'market',
    label: '市场总览',
    icon: 'chart-line',
    level: 1,
    priority: 'primary',
    children: [
      {
        key: 'market-realtime',
        label: '实时行情',
        icon: 'activity',
        level: 2,
        path: '/market/realtime',
        liveUpdate: true,
        wsChannel: 'market:realtime',
        badge: 'LIVE',
        description: 'SSE实时推送',
        children: [
          {
            key: 'market-indices',
            label: '市场指数',
            icon: 'trending-up',
            level: 3,
            path: '/market/realtime/indices',
            apiEndpoint: '/api/market/realtime/indices'
          },
          {
            key: 'stock-rankings',
            label: '股票排行',
            icon: 'bar-chart',
            level: 3,
            path: '/market/realtime/rankings',
            count: 3842,
            apiEndpoint: '/api/market/rankings/stocks'
          },
          {
            key: 'volume-stats',
            label: '成交统计',
            icon: 'pie-chart',
            level: 3,
            path: '/market/realtime/volume',
            apiEndpoint: '/api/market/statistics/volume'
          }
        ]
      },
      {
        key: 'market-analysis',
        label: '市场分析',
        icon: 'line-chart',
        level: 2,
        path: '/market/analysis',
        children: [
          {
            key: 'technical-indicators',
            label: '技术指标',
            icon: 'zap',
            level: 3,
            path: '/market/analysis/indicators',
            apiEndpoint: '/api/indicators/calculate'
          },
          {
            key: 'capital-flow',
            label: '资金流向',
            icon: 'arrow-right-circle',
            level: 3,
            path: '/market/analysis/capital-flow',
            apiEndpoint: '/api/market/capital-flow'
          },
          {
            key: 'longhubang',
            label: '龙虎榜',
            icon: 'award',
            level: 3,
            path: '/market/analysis/longhubang',
            featured: true,
            apiEndpoint: '/api/market/longhubang'
          }
        ]
      },
      {
        key: 'industry-concept',
        label: '行业概念',
        icon: 'layers',
        level: 2,
        path: '/market/sector',
        children: [
          {
            key: 'industry-sectors',
            label: '行业板块',
            icon: 'grid',
            level: 3,
            path: '/market/sector/industries',
            apiEndpoint: '/api/market/industries'
          },
          {
            key: 'concept-themes',
            label: '概念题材',
            icon: 'hash',
            level: 3,
            path: '/market/sector/concepts',
            apiEndpoint: '/api/market/concepts'
          },
          {
            key: 'sector-comparison',
            label: '板块对比',
            icon: 'git-compare',
            level: 3,
            path: '/market/sector/comparison',
            apiEndpoint: '/api/analysis/compare-sectors'
          }
        ]
      }
    ]
  },

  // ========== 一级：交易管理 ==========
  {
    key: 'trading',
    label: '交易管理',
    icon: 'briefcase',
    level: 1,
    priority: 'primary',
    children: [
      {
        key: 'trading-signals',
        label: '交易信号',
        icon: 'radio',
        level: 2,
        path: '/trading/signals',
        badge: 'AI',
        description: '智能信号生成',
        children: [
          {
            key: 'signal-overview',
            label: '信号概览',
            icon: 'eye',
            level: 3,
            path: '/trading/signals/overview',
            count: 12,
            apiEndpoint: '/api/signals/overview'
          },
          {
            key: 'signal-details',
            label: '信号详情',
            icon: 'file-text',
            level: 3,
            path: '/trading/signals/details',
            apiEndpoint: '/api/signals/{id}/details'
          },
          {
            key: 'signal-history',
            label: '历史信号',
            icon: 'clock',
            level: 3,
            path: '/trading/signals/history',
            apiEndpoint: '/api/signals/history'
          }
        ]
      },
      {
        key: 'trading-history',
        label: '交易历史',
        icon: 'history',
        level: 2,
        path: '/trading/history',
        children: [
          {
            key: 'order-records',
            label: '订单记录',
            icon: 'file',
            level: 3,
            path: '/trading/history/orders',
            apiEndpoint: '/api/trade/orders'
          },
          {
            key: 'trade-records',
            label: '成交记录',
            icon: 'check-circle',
            level: 3,
            path: '/trading/history/trades',
            apiEndpoint: '/api/trade/trades'
          },
          {
            key: 'trade-stats',
            label: '交易统计',
            icon: 'bar-chart-2',
            level: 3,
            path: '/trading/history/stats',
            apiEndpoint: '/api/trade/statistics'
          }
        ]
      },
      {
        key: 'position-monitor',
        label: '持仓监控',
        icon: 'target',
        level: 2,
        path: '/trading/position',
        liveUpdate: true,
        wsChannel: 'position:updates',
        children: [
          {
            key: 'current-positions',
            label: '当前持仓',
            icon: 'dollar-sign',
            level: 3,
            path: '/trading/position/current',
            apiEndpoint: '/api/trade/positions'
          },
          {
            key: 'pnl-analysis',
            label: '盈亏分析',
            icon: 'trending-up',
            level: 3,
            path: '/trading/position/pnl',
            apiEndpoint: '/api/trade/pnl-analysis'
          },
          {
            key: 'risk-metrics',
            label: '风险指标',
            icon: 'shield',
            level: 3,
            path: '/trading/position/risk',
            apiEndpoint: '/api/risk/position-metrics'
          }
        ]
      },
      {
        key: 'performance',
        label: '绩效分析',
        icon: 'analytics',
        level: 2,
        path: '/trading/performance',
        children: [
          {
            key: 'return-curve',
            label: '收益曲线',
            icon: 'activity',
            level: 3,
            path: '/trading/performance/returns',
            apiEndpoint: '/api/performance/returns'
          },
          {
            key: 'attribution',
            label: '归因分析',
            icon: 'git-branch',
            level: 3,
            path: '/trading/performance/attribution',
            apiEndpoint: '/api/analysis/attribution'
          },
          {
            key: 'performance-metrics',
            label: '绩效指标',
            icon: 'crosshair',
            level: 3,
            path: '/trading/performance/metrics',
            apiEndpoint: '/api/performance/metrics'
          }
        ]
      }
    ]
  },

  // ========== 一级：策略中心 ==========
  {
    key: 'strategy',
    label: '策略中心',
    icon: 'cpu',
    level: 1,
    priority: 'primary',
    children: [
      {
        key: 'strategy-management',
        label: '策略管理',
        icon: 'settings',
        level: 2,
        path: '/strategy/management',
        children: [
          {
            key: 'strategy-list',
            label: '策略列表',
            icon: 'list',
            level: 3,
            path: '/strategy/management/list',
            count: 8,
            apiEndpoint: '/api/strategy/list'
          },
          {
            key: 'strategy-create',
            label: '创建策略',
            icon: 'plus-circle',
            level: 3,
            path: '/strategy/management/create',
            apiEndpoint: '/api/strategy/create'
          },
          {
            key: 'strategy-config',
            label: '策略配置',
            icon: 'sliders',
            level: 3,
            path: '/strategy/management/config',
            apiEndpoint: '/api/strategy/{id}/config'
          }
        ]
      },
      {
        key: 'backtest',
        label: '回测分析',
        icon: 'experiment',
        level: 2,
        path: '/strategy/backtest',
        badge: 'GPU',
        description: 'GPU加速回测',
        children: [
          {
            key: 'backtest-setup',
            label: '回测设置',
            icon: 'sliders',
            level: 3,
            path: '/strategy/backtest/setup',
            apiEndpoint: '/api/backtest/setup'
          },
          {
            key: 'backtest-results',
            label: '回测结果',
            icon: 'bar-chart',
            level: 3,
            path: '/strategy/backtest/results',
            apiEndpoint: '/api/backtest/{id}/results'
          },
          {
            key: 'backtest-report',
            label: '回测报告',
            icon: 'file-text',
            level: 3,
            path: '/strategy/backtest/report',
            apiEndpoint: '/api/backtest/{id}/report'
          }
        ]
      },
      {
        key: 'optimization',
        label: '策略优化',
        icon: 'tune',
        level: 2,
        path: '/strategy/optimization',
        children: [
          {
            key: 'parameter-opt',
            label: '参数优化',
            icon: 'sliders',
            level: 3,
            path: '/strategy/optimization/parameters',
            apiEndpoint: '/api/optimization/parameters'
          },
          {
            key: 'risk-adjust',
            label: '风险调整',
            icon: 'shield',
            level: 3,
            path: '/strategy/optimization/risk',
            apiEndpoint: '/api/optimization/risk-adjust'
          },
          {
            key: 'performance-eval',
            label: '性能评估',
            icon: 'award',
            level: 3,
            path: '/strategy/optimization/performance',
            apiEndpoint: '/api/optimization/performance'
          }
        ]
      }
    ]
  },

  // ========== 一级：风险控制 ==========
  {
    key: 'risk',
    label: '风险控制',
    icon: 'shield',
    level: 1,
    priority: 'secondary',
    children: [
      {
        key: 'risk-monitor',
        label: '风险监控',
        icon: 'eye',
        level: 2,
        path: '/risk/monitor',
        liveUpdate: true,
        wsChannel: 'risk:alerts',
        children: [
          {
            key: 'risk-overview',
            label: '风险概览',
            icon: 'layout',
            level: 3,
            path: '/risk/monitor/overview',
            apiEndpoint: '/api/risk/overview'
          },
          {
            key: 'risk-trends',
            label: '风险趋势',
            icon: 'trending-up',
            level: 3,
            path: '/risk/monitor/trends',
            apiEndpoint: '/api/risk/trends'
          },
          {
            key: 'risk-alerts',
            label: '风险预警',
            icon: 'alert-triangle',
            level: 3,
            path: '/risk/monitor/alerts',
            count: 3,
            apiEndpoint: '/api/risk/alerts'
          }
        ]
      },
      {
        key: 'announcement',
        label: '公告监控',
        icon: 'bell',
        level: 2,
        path: '/risk/announcement',
        children: [
          {
            key: 'announcement-list',
            label: '公告列表',
            icon: 'list',
            level: 3,
            path: '/risk/announcement/list',
            apiEndpoint: '/api/announcements/list'
          },
          {
            key: 'announcement-filter',
            label: '公告筛选',
            icon: 'filter',
            level: 3,
            path: '/risk/announcement/filter',
            apiEndpoint: '/api/announcements/filter'
          },
          {
            key: 'announcement-analysis',
            label: '公告分析',
            icon: 'brain',
            level: 3,
            path: '/risk/announcement/analysis',
            badge: 'NLP',
            apiEndpoint: '/api/analysis/announcements'
          }
        ]
      },
      {
        key: 'risk-alerts',
        label: '风险告警',
        icon: 'alert-circle',
        level: 2,
        path: '/risk/alerts',
        children: [
          {
            key: 'alert-center',
            label: '告警中心',
            icon: 'command',
            level: 3,
            path: '/risk/alerts/center',
            count: 5,
            apiEndpoint: '/api/risk/alerts/center'
          },
          {
            key: 'alert-rules',
            label: '告警规则',
            icon: 'settings',
            level: 3,
            path: '/risk/alerts/rules',
            apiEndpoint: '/api/risk/alerts/rules'
          },
          {
            key: 'alert-history',
            label: '告警历史',
            icon: 'clock',
            level: 3,
            path: '/risk/alerts/history',
            apiEndpoint: '/api/risk/alerts/history'
          }
        ]
      }
    ]
  },

  // ========== 一级：系统管理 ==========
  {
    key: 'system',
    label: '系统管理',
    icon: 'server',
    level: 1,
    priority: 'tertiary',
    divider: true,
    children: [
      {
        key: 'monitoring-dashboard',
        label: '监控面板',
        icon: 'layout',
        level: 2,
        path: '/system/monitoring',
        children: [
          {
            key: 'system-status',
            label: '系统状态',
            icon: 'activity',
            level: 3,
            path: '/system/monitoring/status',
            apiEndpoint: '/api/monitoring/system-status'
          },
          {
            key: 'performance-metrics',
            label: '性能指标',
            icon: 'zap',
            level: 3,
            path: '/system/monitoring/performance',
            apiEndpoint: '/api/monitoring/performance'
          },
          {
            key: 'data-quality',
            label: '数据质量',
            icon: 'check-square',
            level: 3,
            path: '/system/monitoring/data-quality',
            apiEndpoint: '/api/monitoring/data-quality'
          }
        ]
      },
      {
        key: 'data-management',
        label: '数据管理',
        icon: 'database',
        level: 2,
        path: '/system/data',
        children: [
          {
            key: 'data-import',
            label: '数据导入',
            icon: 'upload',
            level: 3,
            path: '/system/data/import',
            apiEndpoint: '/api/data/import'
          },
          {
            key: 'data-export',
            label: '数据导出',
            icon: 'download',
            level: 3,
            path: '/system/data/export',
            apiEndpoint: '/api/data/export'
          },
          {
            key: 'data-cleanup',
            label: '数据清理',
            icon: 'trash-2',
            level: 3,
            path: '/system/data/cleanup',
            apiEndpoint: '/api/data/cleanup'
          }
        ]
      },
      {
        key: 'system-settings',
        label: '系统设置',
        icon: 'settings',
        level: 2,
        path: '/system/settings',
        children: [
          {
            key: 'general-settings',
            label: '通用设置',
            icon: 'sliders',
            level: 3,
            path: '/system/settings/general'
          },
          {
            key: 'ui-settings',
            label: '界面设置',
            icon: 'layout',
            level: 3,
            path: '/system/settings/ui'
          },
          {
            key: 'security-settings',
            label: '安全设置',
            icon: 'lock',
            level: 3,
            path: '/system/settings/security'
          }
        ]
      }
    ]
  }
]
```

---

## 🎨 ArtDeco组件增强设计

### 紧凑型菜单项组件 (CompactMenuItem.vue)

```vue
<template>
  <div
    class="compact-menu-item"
    :class="{
      'compact-menu-item--active': isActive,
      'compact-menu-item--live': liveUpdate,
      'compact-menu-item--featured': featured,
      'compact-menu-item--disabled': disabled,
      'compact-menu-item--expanded': expanded,
      [`priority-${priority}`]: priority
    }"
    :style="{
      paddingLeft: `${level * 16 + 12}px`
    }"
  >
    <!-- 菜单项主体 -->
    <div
      class="menu-item-content"
      @click="handleClick"
      @mouseenter="handleHover"
      @mouseleave="handleLeave"
    >
      <!-- 图标 -->
      <div class="menu-icon">
        <ArtDecoIcon
          :name="icon"
          :size="level === 1 ? 'md' : 'sm'"
          :animated="liveUpdate && status === 'loading'"
        />

        <!-- 实时状态指示器 -->
        <span
          v-if="liveUpdate"
          class="live-indicator"
          :class="`status-${status || 'idle'}`"
        ></span>
      </div>

      <!-- 文本内容 -->
      <div class="menu-text">
        <span class="menu-label">{{ label }}</span>
        <span v-if="description" class="menu-description">
          {{ description }}
        </span>
      </div>

      <!-- 右侧元数据 -->
      <div class="menu-meta">
        <!-- 徽章 -->
        <ArtDecoBadge
          v-if="badge"
          :text="badge"
          :variant="badgeVariant"
          size="sm"
        />

        <!-- 数量 -->
        <span v-if="count" class="menu-count">
          {{ formatCount(count) }}
        </span>

        <!-- 展开/折叠箭头 -->
        <ArtDecoIcon
          v-if="hasChildren"
          name="chevron-right"
          size="xs"
          class="expand-icon"
          :class="{ rotated: expanded }"
        />
      </div>

      <!-- 错误状态 -->
      <ArtDecoBadge
        v-if="error"
        variant="danger"
        text="!"
        size="sm"
        class="error-badge"
        @click.stop="handleRetry"
      />
    </div>

    <!-- 子菜单 (折叠式展开) -->
    <transition
      name="slide-expand"
      @enter="handleEnter"
      @after-enter="handleAfterEnter"
      @leave="handleLeave"
    >
      <div v-if="expanded && hasChildren" class="menu-children">
        <CompactMenuItem
          v-for="child in children"
          :key="child.key"
          v-bind="child"
          :level="level + 1"
          @select="handleChildSelect"
        />
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'

interface Props {
  key: string
  label: string
  icon: string
  level: number
  path?: string
  children?: CompactMenuItem[]
  badge?: string
  count?: number
  liveUpdate?: boolean
  featured?: boolean
  disabled?: boolean
  priority?: 'primary' | 'secondary' | 'tertiary'
  description?: string
  status?: 'idle' | 'loading' | 'success' | 'error'
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  level: 1,
  disabled: false
})

const emit = defineEmits<{
  select: [item: Props]
  expand: [key: string, expanded: boolean]
  retry: [key: string]
}>()

const expanded = ref(false)
const isActive = ref(false)

const hasChildren = computed(() => props.children && props.children.length > 0)
const badgeVariant = computed(() => {
  if (props.badge === 'LIVE') return 'success'
  if (props.badge === 'GPU') return 'primary'
  if (props.badge === 'AI' || props.badge === 'NLP') return 'secondary'
  return 'default'
})

function handleClick() {
  if (props.disabled) return

  if (hasChildren.value) {
    expanded.value = !expanded.value
    emit('expand', props.key, expanded.value)
  } else if (props.path) {
    emit('select', props)
  }
}

function handleChildSelect(child: Props) {
  emit('select', child)
}

function formatCount(count: number): string {
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`
  return count.toString()
}

function handleRetry() {
  emit('retry', props.key)
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.compact-menu-item {
  // ArtDeco设计系统优化
  border-left: 2px solid transparent;
  transition: all var(--artdeco-transition-base) var(--artdeco-ease-in-out);

  // 悬停效果
  &:hover {
    background: rgba(212, 175, 55, 0.08); // 8% gold tint
    border-left-color: var(--artdeco-gold-primary);

    .menu-icon {
      transform: scale(1.1);
    }
  }

  // 激活状态
  &--active {
    background: rgba(212, 175, 55, 0.12); // 12% gold tint
    border-left-color: var(--artdeco-gold-primary);
    border-left-width: 3px;

    .menu-label {
      color: var(--artdeco-gold-primary);
      font-weight: 600;
    }
  }

  // 实时更新状态
  &--live {
    .live-indicator {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      margin-left: 4px;

      &.status-idle {
        background: var(--artdeco-fg-muted);
      }

      &.status-loading {
        background: var(--artdeco-gold-primary);
        animation: pulse 1.5s ease-in-out infinite;
      }

      &.status-success {
        background: var(--artdeco-success);
      }

      &.status-error {
        background: var(--artdeco-error);
      }
    }
  }

  // 特色标记
  &--featured {
    .menu-label {
      position: relative;

      &::after {
        content: '✦';
        position: absolute;
        right: -16px;
        top: -2px;
        color: var(--artdeco-gold-primary);
        font-size: 10px;
      }
    }
  }

  // 优先级样式
  &.priority-primary {
    .menu-label {
      font-weight: 600;
      color: var(--artdeco-fg-primary);
    }
  }

  &.priority-secondary {
    .menu-label {
      font-weight: 500;
      color: var(--artdeco-fg-muted);
    }
  }

  &.priority-tertiary {
    .menu-label {
      font-weight: 400;
      color: var(--artdeco-fg-subtle);
    }
  }
}

.menu-item-content {
  display: flex;
  align-items: center;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  cursor: pointer;
  user-select: none;
  position: relative;

  // ArtDeco几何装饰（顶级菜单）
  .compact-menu-item[level="1"] > &::before {
    content: '';
    position: absolute;
    left: 4px;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 4px;
    background: var(--artdeco-gold-primary);
    opacity: 0;
    transition: opacity var(--artdeco-transition-base);
  }

  .compact-menu-item--active > &::before {
    opacity: 1;
  }
}

.menu-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: var(--artdeco-spacing-3);
  transition: transform var(--artdeco-transition-base);

  svg {
    fill: currentColor;
  }
}

.menu-text {
  flex: 1;
  min-width: 0;
}

.menu-label {
  display: block;
  font-size: var(--artdeco-text-sm); // 14px
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color var(--artdeco-transition-base);

  // 智能字间距（根据level）
  .compact-menu-item[level="1"] & {
    letter-spacing: 0.18em; // 中等字间距
  }

  .compact-menu-item[level="2"] & {
    letter-spacing: 0.15em; // 较窄字间距
  }

  .compact-menu-item[level="3"] & {
    letter-spacing: 0.12em; // 最窄字间距
  }
}

.menu-description {
  display: block;
  font-size: var(--artdeco-text-xs); // 12px
  color: var(--artdeco-fg-subtle);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-meta {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  margin-left: var(--artdeco-spacing-2);
}

.menu-count {
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-gold-primary);
  background: rgba(212, 175, 55, 0.15);
  padding: 2px 6px;
  border-radius: var(--artdeco-radius-sm);
  min-width: 24px;
  text-align: center;
}

.expand-icon {
  transition: transform var(--artdeco-transition-base);

  &.rotated {
    transform: rotate(90deg);
  }
}

.error-badge {
  margin-left: var(--artdeco-spacing-2);
  cursor: pointer;

  &:hover {
    transform: scale(1.1);
  }
}

// 子菜单容器
.menu-children {
  overflow: hidden;
}

// 过渡动画
.slide-expand-enter-active,
.slide-expand-leave-active {
  transition: all var(--artdeco-transition-base) var(--artdeco-ease-in-out);
}

.slide-expand-enter-from,
.slide-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-expand-enter-to,
.slide-expand-leave-from {
  max-height: 500px;
  opacity: 1;
}

// 脉冲动画
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.9);
  }
}
</style>
```

---

## 📊 量化专用数据展示组件

### K线图卡片 (ArtDecoKLineCard.vue)

**设计要点**:
- 占内容区70%宽度
- 集成TradingView Widget (或ECharts备用)
- 实时数据推送（SSE）
- 技术指标叠加（MA、MACD、KDJ等）
- 时间周期切换（1min/5min/15min/30min/1hour/1day）

```vue
<template>
  <ArtDecoCard
    class="kline-card"
    :variant="hasFullscreen ? 'flat' : 'elevated'"
  >
    <template #header>
      <div class="kline-header">
        <div class="kline-title">
          <ArtDecoIcon name="trending-up" size="sm" />
          <h3>{{ symbol }} K线图</h3>
          <ArtDecoBadge
            :text="currentPeriod"
            variant="outline"
            size="sm"
          />
        </div>

        <!-- 周期切换器 -->
        <div class="period-selector">
          <ArtDecoButton
            v-for="period in periods"
            :key="period.value"
            :variant="currentPeriod === period.value ? 'solid' : 'outline'"
            size="sm"
            @click="changePeriod(period.value)"
          >
            {{ period.label }}
          </ArtDecoButton>
        </div>

        <!-- 工具栏 -->
        <div class="kline-toolbar">
          <ArtDecoButton
            variant="outline"
            size="sm"
            @click="toggleFullscreen"
          >
            <ArtDecoIcon :name="hasFullscreen ? 'minimize' : 'maximize'" />
          </ArtDecoButton>
          <ArtDecoButton
            variant="outline"
            size="sm"
            @click="openIndicators"
          >
            <ArtDecoIcon name="sliders" />
          </ArtDecoButton>
          <ArtDecoButton
            variant="outline"
            size="sm"
            @click="exportChart"
          >
            <ArtDecoIcon name="download" />
          </ArtDecoButton>
        </div>
      </div>
    </template>

    <!-- K线图容器 -->
    <div class="kline-container" ref="klineContainer">
      <!-- TradingView Widget (优先) -->
      div
        id="tradingview-widget"
        v-if="useTradingView"
      ></div>

      <!-- ECharts备用 -->
      div
        id="echarts-kline"
        v-else
        ref="echartsContainer"
        style="width: 100%; height: 100%;"
      ></div>

      <!-- 加载状态 -->
      <div v-if="loading" class="kline-loading">
        <ArtDecoLoader size="lg" />
        <p>加载K线数据...</p>
      </div>
    </div>

    <!-- 实时数据栏 -->
    <div class="kline-status-bar">
      <div class="status-item">
        <span class="label">现价:</span>
        <span
          class="value"
          :class="priceChangeClass"
        >{{ currentPrice }}</span>
      </div>
      <div class="status-item">
        <span class="label">涨跌:</span>
        <span
          class="value"
          :class="priceChangeClass"
        >{{ priceChange }} ({{ priceChangePercent }}%)</span>
      </div>
      <div class="status-item">
        <span class="label">成交量:</span>
        <span class="value">{{ volume }}</span>
      </div>
      <div class="status-item">
        <span class="label">更新:</span>
        <span class="value">{{ lastUpdateTime }}</span>
        <ArtDecoBadge
          v-if="isLive"
          text="LIVE"
          variant="success"
          size="xs"
        />
      </div>
    </div>
  </ArtDecoCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
import ArtDecoLoader from '@/components/artdeco/base/ArtDecoLoader.vue'

interface Props {
  symbol: string
  defaultPeriod?: string
  useTradingView?: boolean
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultPeriod: '1day',
  useTradingView: true,
  height: '600px'
})

const emit = defineEmits<{
  periodChange: [period: string]
  fullscreenToggle: []
  export: []
}>()

const loading = ref(true)
const hasFullscreen = ref(false)
const currentPeriod = ref(props.defaultPeriod)
const isLive = ref(true)

// K线数据
const currentPrice = ref('0.00')
const priceChange = ref('+0.00')
const priceChangePercent = ref('0.00')
const volume = ref('0')
const lastUpdateTime = ref('--:--:--')

const priceChangeClass = computed(() => {
  const change = parseFloat(priceChangePercent.value)
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
})

const periods = [
  { label: '1分', value: '1min' },
  { label: '5分', value: '5min' },
  { label: '15分', value: '15min' },
  { label: '30分', value: '30min' },
  { label: '1小时', value: '1hour' },
  { label: '日线', value: '1day' },
  { label: '周线', value: '1week' },
  { label: '月线', value: '1month' }
]

function changePeriod(period: string) {
  currentPeriod.value = period
  emit('periodChange', period)
  loadKlineData()
}

function toggleFullscreen() {
  hasFullscreen.value = !hasFullscreen.value
  emit('fullscreenToggle')
}

function openIndicators() {
  // 打开技术指标配置面板
}

function exportChart() {
  emit('export')
}

async function loadKlineData() {
  loading.value = true
  try {
    // 调用API获取K线数据
    // const data = await api.getKlineData(props.symbol, currentPeriod.value)
    // 更新图表
  } finally {
    loading.value = false
  }
}

// SSE实时数据推送
let eventSource: EventSource | null = null

function connectSSE() {
  eventSource = new EventSource(`/api/market/realtime/kline/${props.symbol}`)

  eventSource.addEventListener('message', (event) => {
    const data = JSON.parse(event.data)
    // 更新K线数据
    currentPrice.value = data.price.toFixed(2)
    priceChange.value = data.change.toFixed(2)
    priceChangePercent.value = data.changePercent.toFixed(2)
    volume.value = formatVolume(data.volume)
    lastUpdateTime.value = formatTime(data.timestamp)
  })

  eventSource.addEventListener('error', () => {
    isLive.value = false
  })
}

onMounted(() => {
  loadKlineData()
  connectSSE()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.kline-card {
  height: v-bind(height);
  display: flex;
  flex-direction: column;
}

.kline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);
}

.kline-title {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  h3 {
    font-size: var(--artdeco-text-base);
    font-weight: 600;
    color: var(--artdeco-fg-primary);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin: 0;
  }
}

.period-selector {
  display: flex;
  gap: var(--artdeco-spacing-2);

  .artdeco-button {
    min-width: 50px;
    padding: 0 var(--artdeco-spacing-3);
  }
}

.kline-toolbar {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.kline-container {
  flex: 1;
  position: relative;
  background: var(--artdeco-bg-card);
  overflow: hidden;
}

.kline-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-4);
  background: rgba(10, 10, 11, 0.8);

  p {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }
}

.kline-status-bar {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-6);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: rgba(212, 175, 55, 0.05);
  border-top: 1px solid var(--artdeco-border-default);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  .label {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
  }

  .value {
    font-size: var(--artdeco-text-sm);
    font-weight: 600;
    font-family: var(--artdeco-font-mono);
    color: var(--artdeco-fg-primary);

    &.text-up {
      color: var(--artdeco-up);
    }

    &.text-down {
      color: var(--artdeco-down);
    }

    &.text-flat {
      color: var(--artdeco-flat);
    }
  }
}
</style>
```

---

## 📐 信息密度优化规范

### 间距系统（紧凑型）

```scss
// 紧凑型间距系统 (基于ArtDeco tokens)
$spacing-compact: (
  'xs': 4px,   // 元素内部紧凑间距
  'sm': 8px,   // 小元素间距
  'md': 12px,  // 中等元素间距
  'lg': 16px,  // 大元素间距
  'xl': 24px,  // 区块间距
);

// 应用示例
.compact-card {
  padding: var(--spacing-md); // 12px (vs 标准的16px)
  gap: var(--spacing-sm);     // 8px (vs 标准的12px)
}

.compact-list {
  .list-item {
    padding: var(--spacing-sm) var(--spacing-md); // 8px 12px
    margin-bottom: var(--spacing-xs); // 4px
  }
}
```

### 字体大小（金融专用）

```scss
// 金融数据专用字体大小
$font-sizes-financial: (
  'ticker-lg': 20px,    // 大屏股票代码
  'ticker-md': 16px,    // 标准股票代码
  'ticker-sm': 14px,    // 紧凑股票代码

  'price-lg': 24px,     // 大屏价格显示
  'price-md': 18px,     // 标准价格显示
  'price-sm': 16px,     // 紧凑价格显示

  'percent-lg': 16px,   // 大屏涨跌幅
  'percent-md': 14px,   // 标准涨跌幅
  'percent-sm': 12px,   // 紧凑涨跌幅

  'volume-lg': 14px,    // 大屏成交量
  'volume-md': 12px,    // 标准成交量
  'volume-sm': 11px,    // 紧凑成交量
);

// 应用示例
.financial-data {
  .ticker-code {
    font-size: map-get($font-sizes-financial, 'ticker-md');
    font-weight: 600;
    font-family: var(--artdeco-font-mono);
  }

  .current-price {
    font-size: map-get($font-sizes-financial, 'price-lg');
    font-weight: 700;
    font-family: var(--artdeco-font-mono);
  }

  .change-percent {
    font-size: map-get($font-sizes-financial, 'percent-md');
    font-weight: 600;
    font-family: var(--artdeco-font-mono);
  }
}
```

### 表格行高（紧凑型）

```scss
// 金融表格行高系统
$table-rows-compact: (
  'xs': 32px,  // 超紧凑（仅数据）
  'sm': 40px,  // 紧凑（数据+图标）
  'md': 48px,  // 标准（数据+图标+操作）
  'lg': 56px,  // 宽松（多行数据）
);

// 应用示例
.financial-table {
  .table-row {
    height: map-get($table-rows-compact, 'md'); // 48px
    padding: 0 var(--spacing-md);

    &.compact {
      height: map-get($table-rows-compact, 'sm'); // 40px
      padding: 0 var(--spacing-sm);
    }

    &.ultra-compact {
      height: map-get($table-rows-compact, 'xs'); // 32px
      padding: 0 var(--spacing-sm);
    }
  }
}
```

---

## 🎯 实施路线图

### Phase 1: 基础架构 (Week 1)
- [ ] 创建紧凑型菜单组件系统
- [ ] 实现三级菜单折叠/展开逻辑
- [ ] 集成WebSocket实时数据推送
- [ ] 优化左侧功能树布局

### Phase 2: 数据展示组件 (Week 2)
- [ ] 实现K线图卡片（TradingView集成）
- [ ] 创建实时行情列表组件
- [ ] 开发技术指标叠加功能
- [ ] 实现多时间周期切换

### Phase 3: 信息密度优化 (Week 3)
- [ ] 应用紧凑型间距系统
- [ ] 实施金融专用字体大小
- [ ] 优化表格行高和间距
- [ ] 调整视觉层级和对比度

### Phase 4: 高级功能 (Week 4)
- [ ] 实现分屏多视图模式
- [ ] 添加键盘快捷键系统
- [ ] 开发自定义仪表板功能
- [ ] 实现数据导出和报告生成

---

## 📏 性能指标

### 加载性能
- **首屏时间**: < 2秒
- **菜单响应**: < 100ms
- **数据更新**: < 50ms (SSE推送)
- **交互延迟**: < 16ms (60fps)

### 内存使用
- **初始加载**: < 50MB
- **运行时峰值**: < 200MB
- **虚拟滚动**: 仅渲染可见区域

### 网络优化
- **数据压缩**: Gzip/Brotli
- **增量更新**: WebSocket diff推送
- **缓存策略**: Service Worker + IndexedDB

---

## ✅ 验收标准

### 功能完整性
- [ ] 所有6个一级菜单可正常展开/折叠
- [ ] 三级子菜单层级结构清晰
- [ ] 实时数据推送无延迟
- [ ] SSE连接自动重连

### 视觉质量
- [ ] ArtDeco设计系统一致性
- [ ] 边框透明度30%，悬停100%
- [ ] 背景图案可见度6%
- [ ] 智能字间距系统生效

### 用户体验
- [ ] 键盘导航完整支持
- [ ] 屏幕阅读器友好
- [ ] WCAG AA级对比度
- [ ] 触摸目标≥44×44px

### 性能要求
- [ ] 首屏加载<2秒
- [ ] 菜单切换<100ms
- [ ] 数据更新<50ms
- [ ] 内存占用<200MB

---

**文档版本**: 3.0.0
**最后更新**: 2026-01-22
**维护者**: UI/UX Pro Max + ArtDeco设计系统
**状态**: ✅ 待实施
