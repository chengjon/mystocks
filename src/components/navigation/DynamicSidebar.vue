<template>
  <!-- Dynamic Sidebar Container -->
  <aside
    class="dynamic-sidebar"
    :class="sidebarClasses"
    :style="sidebarStyle"
    role="navigation"
    aria-label="Domain navigation"
  >
    <!-- Domain Header -->
    <div class="domain-header">
      <div class="domain-info">
        <el-icon class="domain-icon" size="20">
          <component :is="currentDomainConfig.icon" />
        </el-icon>
        <div class="domain-text">
          <h3 class="domain-title">{{ currentDomainConfig.title }}</h3>
          <p class="domain-subtitle">{{ currentDomainConfig.subtitle }}</p>
        </div>
      </div>
      <el-button
        v-if="!isCollapsed"
        type="text"
        size="small"
        class="domain-switcher"
        @click="showDomainSwitcher = true"
      >
        切换
      </el-button>
    </div>

    <!-- Search/Filter Bar -->
    <div v-if="!isCollapsed && currentDomainConfig.searchable" class="sidebar-search">
      <el-input
        v-model="searchQuery"
        placeholder="搜索页面..."
        size="small"
        clearable
        prefix-icon="Search"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Menu Items -->
    <div class="sidebar-menu-container">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        background-color="transparent"
        text-color="var(--color-text-secondary)"
        active-text-color="var(--color-primary-400)"
        class="dynamic-sidebar-menu"
        @select="handleMenuSelect"
      >
        <template v-for="menuItem in filteredMenuItems" :key="menuItem.id">
          <!-- Submenu -->
          <el-sub-menu v-if="menuItem.children && menuItem.children.length > 0" :index="menuItem.id">
            <template #title>
              <el-icon v-if="menuItem.icon" size="16">
                <component :is="menuItem.icon" />
              </el-icon>
              <span>{{ menuItem.title }}</span>
              <el-badge
                v-if="menuItem.badge"
                :value="menuItem.badge"
                class="menu-badge"
              />
            </template>
            <el-menu-item
              v-for="child in menuItem.children"
              :key="child.id"
              :index="child.id"
            >
              <el-icon v-if="child.icon" size="14">
                <component :is="child.icon" />
              </el-icon>
              <template #title>{{ child.title }}</template>
              <el-badge
                v-if="child.badge"
                :value="child.badge"
                class="menu-badge"
              />
            </el-menu-item>
          </el-sub-menu>

          <!-- Single Menu Item -->
          <el-menu-item v-else :index="menuItem.id">
            <el-icon v-if="menuItem.icon" size="16">
              <component :is="menuItem.icon" />
            </el-icon>
            <template #title>{{ menuItem.title }}</template>
            <el-badge
              v-if="menuItem.badge"
              :value="menuItem.badge"
              class="menu-badge"
            />
          </el-menu-item>
        </template>
      </el-menu>
    </div>

    <!-- Domain Switcher Modal -->
    <el-dialog
      v-model="showDomainSwitcher"
      title="切换功能域"
      width="400px"
      center
    >
      <div class="domain-grid">
        <div
          v-for="domain in domainConfigs"
          :key="domain.id"
          class="domain-card"
          :class="{ active: domain.id === currentDomain }"
          @click="switchDomain(domain.id)"
        >
          <el-icon class="domain-card-icon" size="24">
            <component :is="domain.icon" />
          </el-icon>
          <h4 class="domain-card-title">{{ domain.title }}</h4>
          <p class="domain-card-subtitle">{{ domain.subtitle }}</p>
        </div>
      </div>
    </el-dialog>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search,
  Monitor,
  TrendCharts,
  DataAnalysis,
  Setting,
  Money,
  ShoppingCart,
  Warning,
  Management,
  Histogram,
  List,
  Tickets,
  Grid,
  Document
} from '@element-plus/icons-vue'

// Types
interface MenuItem {
  id: string
  title: string
  icon?: any
  badge?: string | number
  children?: MenuItem[]
  path?: string
  action?: () => void
}

interface DomainConfig {
  id: string
  title: string
  subtitle: string
  icon: any
  searchable: boolean
  menuItems: MenuItem[]
}

// Props & Emits
const props = defineProps<{
  currentDomain: string
  isCollapsed: boolean
  collapsedWidth?: number
  expandedWidth?: number
}>()

const emit = defineEmits<{
  'domain-switch': [domainId: string]
  'menu-select': [menuId: string, menuItem: MenuItem]
  'collapse-toggle': []
}>()

// Composables
const route = useRoute()
const router = useRouter()

// State
const searchQuery = ref('')
const showDomainSwitcher = ref(false)

// Domain Configurations
const domainConfigs = ref<DomainConfig[]>([
  {
    id: 'market',
    title: '市场数据',
    subtitle: '实时行情与技术分析',
    icon: TrendCharts,
    searchable: true,
    menuItems: [
      {
        id: 'market-realtime',
        title: '实时行情',
        icon: Monitor,
        path: '/market/realtime'
      },
      {
        id: 'market-technical',
        title: '技术分析',
        icon: DataAnalysis,
        path: '/market/technical'
      },
      {
        id: 'market-tdx',
        title: 'TDX行情',
        icon: TrendCharts,
        path: '/market/tdx'
      },
      {
        id: 'market-capital-flow',
        title: '资金流向',
        icon: Money,
        path: '/market/capital-flow'
      },
      {
        id: 'market-etf',
        title: 'ETF市场',
        icon: ShoppingCart,
        path: '/market/etf'
      },
      {
        id: 'market-concepts',
        title: '概念分析',
        icon: Grid,
        path: '/market/concepts'
      },
      {
        id: 'market-auction',
        title: '拍卖分析',
        icon: Histogram,
        path: '/market/auction'
      },
      {
        id: 'market-lhb',
        title: '龙虎榜',
        icon: Warning,
        path: '/market/lhb'
      }
    ]
  },
  {
    id: 'selection',
    title: '选股工具',
    subtitle: '智能筛选与组合管理',
    icon: Search,
    searchable: true,
    menuItems: [
      {
        id: 'selection-watchlist',
        title: '自选股管理',
        icon: List,
        path: '/selection/watchlist'
      },
      {
        id: 'selection-portfolio',
        title: '投资组合',
        icon: Grid,
        path: '/selection/portfolio'
      },
      {
        id: 'selection-activity',
        title: '交易活动',
        icon: Tickets,
        path: '/selection/activity'
      },
      {
        id: 'selection-screener',
        title: '股票筛选器',
        icon: Search,
        path: '/selection/screener'
      },
      {
        id: 'selection-industry',
        title: '行业板块',
        icon: DataAnalysis,
        path: '/selection/industry'
      },
      {
        id: 'selection-concept',
        title: '概念板块',
        icon: Grid,
        path: '/selection/concept'
      }
    ]
  },
  {
    id: 'strategy',
    title: '量化策略',
    subtitle: '策略开发与回测',
    icon: Management,
    searchable: false,
    menuItems: [
      {
        id: 'strategy-management',
        title: '策略管理',
        icon: Management,
        path: '/strategy/management'
      },
      {
        id: 'strategy-backtest',
        title: '策略回测',
        icon: Histogram,
        path: '/strategy/backtest'
      }
    ]
  },
  {
    id: 'trading',
    title: '交易执行',
    subtitle: '订单管理与执行',
    icon: Tickets,
    searchable: false,
    menuItems: [
      {
        id: 'trading-orders',
        title: '交易订单',
        icon: Tickets,
        path: '/trading/orders'
      },
      {
        id: 'trading-positions',
        title: '持仓管理',
        icon: Grid,
        path: '/trading/positions'
      },
      {
        id: 'trading-history',
        title: '交易历史',
        icon: Document,
        path: '/trading/history'
      },
      {
        id: 'trading-execution',
        title: '订单执行',
        icon: ShoppingCart,
        path: '/trading/execution'
      }
    ]
  },
  {
    id: 'risk',
    title: '风险监控',
    subtitle: '风险评估与预警',
    icon: Warning,
    searchable: false,
    menuItems: [
      {
        id: 'risk-overview',
        title: '风险概览',
        icon: Monitor,
        path: '/risk/overview'
      },
      {
        id: 'risk-positions',
        title: '持仓风险',
        icon: Warning,
        path: '/risk/positions'
      },
      {
        id: 'risk-portfolio',
        title: '组合风险',
        icon: Grid,
        path: '/risk/portfolio'
      },
      {
        id: 'risk-alerts',
        title: '风险预警',
        icon: Warning,
        path: '/risk/alerts'
      }
    ]
  },
  {
    id: 'settings',
    title: '系统设置',
    subtitle: '配置与个性化',
    icon: Setting,
    searchable: false,
    menuItems: [
      {
        id: 'settings-general',
        title: '通用设置',
        icon: Setting,
        path: '/settings/general'
      },
      {
        id: 'settings-theme',
        title: '主题设置',
        icon: Setting,
        path: '/settings/theme'
      },
      {
        id: 'settings-notifications',
        title: '通知设置',
        icon: Setting,
        path: '/settings/notifications'
      },
      {
        id: 'settings-security',
        title: '安全设置',
        icon: Setting,
        path: '/settings/security'
      }
    ]
  }
])

// Computed Properties
const currentDomainConfig = computed(() => {
  return domainConfigs.value.find(config => config.id === props.currentDomain) || domainConfigs.value[0]
})

const filteredMenuItems = computed(() => {
  if (!searchQuery.value.trim()) {
    return currentDomainConfig.value.menuItems
  }

  const query = searchQuery.value.toLowerCase()
  return currentDomainConfig.value.menuItems.filter(item => {
    const matchesTitle = item.title.toLowerCase().includes(query)
    const matchesChildren = item.children?.some(child =>
      child.title.toLowerCase().includes(query)
    )
    return matchesTitle || matchesChildren
  })
})

const sidebarClasses = computed(() => ({
  'is-collapsed': props.isCollapsed
}))

const sidebarStyle = computed(() => ({
  width: props.isCollapsed
    ? `${props.collapsedWidth || 64}px`
    : `${props.expandedWidth || 280}px`
}))

const activeMenu = computed(() => {
  // Find active menu based on current route
  for (const menuItem of currentDomainConfig.value.menuItems) {
    if (menuItem.path === route.path) {
      return menuItem.id
    }
    if (menuItem.children) {
      const activeChild = menuItem.children.find(child => child.path === route.path)
      if (activeChild) {
        return activeChild.id
      }
    }
  }
  return ''
})

// Methods
const switchDomain = (domainId: string) => {
  emit('domain-switch', domainId)
  showDomainSwitcher.value = false
}

const handleMenuSelect = (menuId: string) => {
  const menuItem = findMenuItem(menuId)
  if (menuItem) {
    emit('menu-select', menuId, menuItem)

    if (menuItem.path) {
      router.push(menuItem.path)
    } else if (menuItem.action) {
      menuItem.action()
    }
  }
}

const findMenuItem = (menuId: string): MenuItem | null => {
  for (const menuItem of currentDomainConfig.value.menuItems) {
    if (menuItem.id === menuId) {
      return menuItem
    }
    if (menuItem.children) {
      const child = menuItem.children.find(c => c.id === menuId)
      if (child) return child
    }
  }
  return null
}

// Watch for route changes
watch(() => route.path, () => {
  // Update search query when route changes
  searchQuery.value = ''
})

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault()
    // Could emit command palette event here
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

// Cleanup
const cleanup = () => {
  document.removeEventListener('keydown', handleKeydown)
}

// Expose cleanup for parent components
defineExpose({ cleanup })
</script>

<style scoped lang="scss">
.dynamic-sidebar {
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-primary);
  display: flex;
  flex-direction: column;
  height: 100vh;
  transition: width var(--animation-duration-normal) var(--animation-timing-ease);
  overflow: hidden;
}

.domain-header {
  padding: var(--component-padding-md);
  border-bottom: 1px solid var(--color-border-secondary);
  background: linear-gradient(135deg, var(--color-bg-tertiary) 0%, var(--color-bg-secondary) 100%);
  flex-shrink: 0;

  .domain-info {
    display: flex;
    align-items: center;
    gap: var(--component-gap-sm);

    .domain-icon {
      color: var(--color-primary-400);
      flex-shrink: 0;
    }

    .domain-text {
      flex: 1;
      min-width: 0;

      .domain-title {
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-semibold);
        color: var(--color-text-primary);
        margin: 0 0 var(--spacing-1) 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .domain-subtitle {
        font-size: var(--font-size-xs);
        color: var(--color-text-tertiary);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }

  .domain-switcher {
    color: var(--color-primary-400);
    font-size: var(--font-size-xs);
    padding: var(--spacing-1);
    margin-left: auto;
    flex-shrink: 0;

    &:hover {
      color: var(--color-primary-300);
      background-color: var(--color-surface-hover);
    }
  }
}

.sidebar-search {
  padding: var(--component-padding-sm);
  border-bottom: 1px solid var(--color-border-tertiary);
  flex-shrink: 0;

  :deep(.el-input) {
    .el-input__wrapper {
      background-color: var(--color-surface-primary);
      border-color: var(--color-border-secondary);

      &:hover {
        border-color: var(--color-border-primary);
      }

      &:focus-within {
        border-color: var(--color-border-focus);
        box-shadow: var(--component-shadow-input-focus);
      }
    }

    .el-input__inner {
      color: var(--color-text-primary);
      background-color: transparent;

      &::placeholder {
        color: var(--color-text-tertiary);
      }
    }
  }
}

.sidebar-menu-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.dynamic-sidebar-menu {
  border-right: none;
  padding: var(--component-padding-sm) 0;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    margin: 0 var(--component-padding-sm);
    border-radius: var(--component-radius-button);
    height: var(--button-height-md);
    line-height: var(--button-height-md);
    transition: all var(--animation-duration-fast) var(--animation-timing-ease);

    &:hover {
      background-color: var(--color-surface-hover);
      color: var(--color-text-primary);
    }

    &:focus {
      background-color: var(--color-surface-hover);
      outline: none;
    }
  }

  :deep(.el-menu-item.is-active) {
    background-color: var(--color-primary-600);
    color: var(--color-text-primary);
    font-weight: var(--font-weight-medium);

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 60%;
      background-color: var(--color-primary-400);
      border-radius: 0 2px 2px 0;
    }
  }

  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      margin: 0 var(--component-padding-sm);
      border-radius: var(--component-radius-button);
      height: var(--button-height-md);
      line-height: var(--button-height-md);
    }

    .el-menu {
      background-color: var(--color-surface-secondary);

      .el-menu-item {
        padding-left: 48px !important;
        margin: 0 var(--component-padding-sm);
        height: 44px;
        line-height: 44px;

        &:hover {
          background-color: var(--color-surface-hover);
        }

        &.is-active {
          background-color: var(--color-primary-600);
          color: var(--color-text-primary);
        }
      }
    }
  }

  :deep(.el-icon) {
    font-size: 16px;
    width: 16px;
    height: 16px;
    margin-right: var(--component-gap-sm);
  }

  .menu-badge {
    margin-left: auto;
  }
}

.domain-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--component-gap-md);

  .domain-card {
    padding: var(--component-padding-md);
    border: 1px solid var(--color-border-secondary);
    border-radius: var(--component-radius-card);
    background-color: var(--color-surface-primary);
    cursor: pointer;
    transition: all var(--animation-duration-fast) var(--animation-timing-ease);
    text-align: center;

    &:hover {
      border-color: var(--color-primary-400);
      background-color: var(--color-surface-hover);
    }

    &.active {
      border-color: var(--color-primary-500);
      background-color: var(--color-primary-600);
      color: var(--color-text-primary);

      .domain-card-title {
        color: var(--color-text-primary);
      }

      .domain-card-subtitle {
        color: var(--color-text-secondary);
      }
    }

    .domain-card-icon {
      color: var(--color-primary-400);
      margin-bottom: var(--component-gap-sm);

      .active & {
        color: var(--color-text-primary);
      }
    }

    .domain-card-title {
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-semibold);
      color: var(--color-text-primary);
      margin: 0 0 var(--spacing-1) 0;
    }

    .domain-card-subtitle {
      font-size: var(--font-size-sm);
      color: var(--color-text-tertiary);
      margin: 0;
    }
  }
}

/* Collapsed state */
.dynamic-sidebar.is-collapsed {
  .domain-header {
    .domain-text,
    .domain-switcher {
      display: none;
    }

    .domain-icon {
      margin: 0 auto;
    }
  }

  .sidebar-search {
    display: none;
  }

  .dynamic-sidebar-menu {
    :deep(.el-menu--collapse) {
      .el-menu-item,
      .el-sub-menu__title {
        padding: 0;
        justify-content: center;

        .el-icon {
          margin-right: 0;
        }

        span {
          display: none;
        }
      }
    }
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dynamic-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: var(--z-index-modal);
    box-shadow: var(--shadow-xl);
  }

  .domain-grid {
    grid-template-columns: 1fr;
  }
}

/* Accessibility improvements */
@media (prefers-contrast: high) {
  .dynamic-sidebar {
    border-right: 2px solid var(--color-border-primary);
  }

  .domain-header {
    border-bottom: 2px solid var(--color-border-secondary);
  }
}

@media (prefers-reduced-motion: reduce) {
  .dynamic-sidebar,
  .domain-header,
  .dynamic-sidebar-menu :deep(.el-menu-item),
  .dynamic-sidebar-menu :deep(.el-sub-menu__title),
  .domain-card {
    transition: none;
  }
}

/* Print styles */
@media print {
  .dynamic-sidebar {
    display: none;
  }
}
</style>