<template>
  <el-container class="market-layout">
    <!-- Sidebar Navigation (inherited from MainLayout) -->
    <el-aside
      :width="sidebarWidth"
      class="layout-sidebar"
      :class="{ 'is-collapsed': isCollapsed }"
    >
      <!-- Logo Area -->
      <div class="sidebar-logo">
        <transition name="logo-fade">
          <h1 v-if="!isCollapsed" class="logo-text">MyStocks</h1>
          <h1 v-else class="logo-text-short">MS</h1>
        </transition>
      </div>

      <!-- Menu Items -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        background-color="transparent"
        text-color="var(--text-secondary)"
        active-text-color="var(--color-primary)"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- Dashboard -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <!-- Market Data -->
        <el-sub-menu index="market">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>市场行情</span>
          </template>
          <el-menu-item index="/market">
            <template #title>实时行情</template>
          </el-menu-item>
          <el-menu-item index="/tdx-market">
            <template #title>TDX行情</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Market Analysis -->
        <el-sub-menu index="market-data">
          <template #title>
            <el-icon><DataLine /></el-icon>
            <span>市场数据</span>
          </template>
          <el-menu-item index="/market-data/fund-flow">
            <el-icon><Money /></el-icon>
            <template #title>资金流向</template>
          </el-menu-item>
          <el-menu-item index="/market-data/etf">
            <el-icon><TrendCharts /></el-icon>
            <template #title>ETF行情</template>
          </el-menu-item>
          <el-menu-item index="/market-data/chip-race">
            <el-icon><ShoppingCart /></el-icon>
            <template #title>竞价抢筹</template>
          </el-menu-item>
          <el-menu-item index="/market-data/lhb">
            <el-icon><Flag /></el-icon>
            <template #title>龙虎榜</template>
          </el-menu-item>
          <el-menu-item index="/market-data/wencai">
            <el-icon><Search /></el-icon>
            <template #title>问财筛选</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Stocks -->
        <el-menu-item index="/stocks">
          <el-icon><Grid /></el-icon>
          <template #title>股票管理</template>
        </el-menu-item>

        <!-- Analysis -->
        <el-menu-item index="/analysis">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>

        <!-- Technical -->
        <el-menu-item index="/technical">
          <el-icon><DataLine /></el-icon>
          <template #title>技术分析</template>
        </el-menu-item>

        <!-- Indicators -->
        <el-menu-item index="/indicators">
          <el-icon><Grid /></el-icon>
          <template #title>指标库</template>
        </el-menu-item>

        <!-- Risk -->
        <el-menu-item index="/risk">
          <el-icon><Warning /></el-icon>
          <template #title>风险监控</template>
        </el-menu-item>

        <!-- Announcement -->
        <el-menu-item index="/announcement">
          <el-icon><Document /></el-icon>
          <template #title>公告监控</template>
        </el-menu-item>

        <!-- Realtime -->
        <el-menu-item index="/realtime">
          <el-icon><Monitor /></el-icon>
          <template #title>实时监控</template>
        </el-menu-item>

        <!-- Trade -->
        <el-menu-item index="/trade">
          <el-icon><Tickets /></el-icon>
          <template #title>交易管理</template>
        </el-menu-item>

        <!-- Strategy -->
        <el-menu-item index="/strategy">
          <el-icon><Management /></el-icon>
          <template #title>策略管理</template>
        </el-menu-item>

        <!-- Backtest -->
        <el-menu-item index="/backtest">
          <el-icon><Histogram /></el-icon>
          <template #title>回测分析</template>
        </el-menu-item>

        <!-- Tasks -->
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <template #title>任务管理</template>
        </el-menu-item>

        <!-- Settings -->
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main Container -->
    <el-container class="layout-main-container">
      <!-- Top Navigation Bar -->
      <el-header class="layout-header">
        <div class="header-left">
          <!-- Collapse Toggle -->
          <el-icon
            class="collapse-toggle"
            @click="toggleSidebar"
          >
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>

          <!-- Breadcrumb -->
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="{ path: item.path }"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- Notifications -->
          <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="header-action">
            <el-icon><Bell /></el-icon>
          </el-badge>

          <!-- User Dropdown -->
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-dropdown">
              <el-avatar :size="32" class="user-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>个人信息</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings" divided>
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Market-Specific Toolbar -->
      <div class="market-toolbar">
        <!-- Time Period Selector -->
        <div class="toolbar-group">
          <span class="toolbar-label">时间周期:</span>
          <el-radio-group v-model="selectedPeriod" size="small" @change="handlePeriodChange">
            <el-radio-button label="1m">分时</el-radio-button>
            <el-radio-button label="5m">5分</el-radio-button>
            <el-radio-button label="15m">15分</el-radio-button>
            <el-radio-button label="30m">30分</el-radio-button>
            <el-radio-button label="1h">60分</el-radio-button>
            <el-radio-button label="1d">日K</el-radio-button>
            <el-radio-button label="1w">周K</el-radio-button>
            <el-radio-button label="1M">月K</el-radio-button>
          </el-radio-group>
        </div>

        <!-- Data Refresh -->
        <div class="toolbar-group">
          <el-button
            :loading="isRefreshing"
            :icon="Refresh"
            size="small"
            @click="handleRefresh"
          >
            刷新数据
          </el-button>
        </div>

        <!-- Data Export -->
        <div class="toolbar-group">
          <el-dropdown trigger="click" @command="handleExport">
            <el-button :icon="Download" size="small">
              导出数据
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">
                  <el-icon><Document /></el-icon>
                  <span>导出为 CSV</span>
                </el-dropdown-item>
                <el-dropdown-item command="excel">
                  <el-icon><Tickets /></el-icon>
                  <span>导出为 Excel</span>
                </el-dropdown-item>
                <el-dropdown-item command="json">
                  <el-icon><DataLine /></el-icon>
                  <span>导出为 JSON</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Real-time Update Indicator -->
        <div class="toolbar-group toolbar-right">
          <div class="realtime-indicator" :class="{ 'is-active': isRealtime }">
            <div class="indicator-dot"></div>
            <span class="indicator-text">
              {{ isRealtime ? '实时更新中' : '已暂停' }}
            </span>
            <el-switch
              v-model="isRealtime"
              size="small"
              inline-prompt
              active-text="开"
              inactive-text="关"
              @change="handleRealtimeToggle"
            />
          </div>
        </div>
      </div>

      <!-- Market Overview Panel -->
      <div class="market-overview">
        <el-row :gutter="16">
          <!-- Index Overview -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">上证指数</div>
              <div class="card-value">{{ marketOverview.shIndex }}</div>
              <div :class="['card-change', getChangeClass(marketOverview.shIndexChange)]">
                <el-icon v-if="marketOverview.shIndexChange > 0"><CaretTop /></el-icon>
                <el-icon v-else-if="marketOverview.shIndexChange < 0"><CaretBottom /></el-icon>
                <span>{{ marketOverview.shIndexChange }}%</span>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">深证成指</div>
              <div class="card-value">{{ marketOverview.szIndex }}</div>
              <div :class="['card-change', getChangeClass(marketOverview.szIndexChange)]">
                <el-icon v-if="marketOverview.szIndexChange > 0"><CaretTop /></el-icon>
                <el-icon v-else-if="marketOverview.szIndexChange < 0"><CaretBottom /></el-icon>
                <span>{{ marketOverview.szIndexChange }}%</span>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">创业板指</div>
              <div class="card-value">{{ marketOverview.cyIndex }}</div>
              <div :class="['card-change', getChangeClass(marketOverview.cyIndexChange)]">
                <el-icon v-if="marketOverview.cyIndexChange > 0"><CaretTop /></el-icon>
                <el-icon v-else-if="marketOverview.cyIndexChange < 0"><CaretBottom /></el-icon>
                <span>{{ marketOverview.cyIndexChange }}%</span>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">涨跌统计</div>
              <div class="card-value-mini">
                <span class="text-up">{{ marketOverview.upCount }}涨</span>
                <span class="text-divider">/</span>
                <span class="text-down">{{ marketOverview.downCount }}跌</span>
              </div>
              <div class="card-sub">{{ marketOverview.flatCount }}平</div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">市场热度</div>
              <div class="card-value">{{ marketOverview.heat }}</div>
              <div class="card-sub">成交额: {{ marketOverview.amount }}亿</div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="4">
            <div class="overview-card">
              <div class="card-title">涨跌停</div>
              <div class="card-value-mini">
                <span class="text-up">{{ marketOverview.limitUp }}</span>
                <span class="text-divider">/</span>
                <span class="text-down">{{ marketOverview.limitDown }}</span>
              </div>
              <div class="card-sub">涨停 / 跌停</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Area -->
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
// @ts-nocheck

import { ref, computed, watch, onMounted, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// ============================================
// 类型定义
// ============================================

/**
 * 面包屑导航项
 */
interface BreadcrumbItem {
  path: string
  title: string
}

/**
 * 用户命令类型
 */
type UserCommand = 'profile' | 'settings' | 'logout'

/**
 * 市场概览数据
 */
interface MarketOverview {
  shIndex: string
  shIndexChange: number
  szIndex: string
  szIndexChange: number
  cyIndex: string
  cyIndexChange: number
  upCount: number
  downCount: number
  flatCount: number
  heat: string
  amount: string
  limitUp: number
  limitDown: number
}

/**
 * 涨跌样式类
 */
type ChangeClass = 'text-up' | 'text-down' | 'text-flat'

// ============================================
// Composables
// ============================================
const route = useRoute()
const router = useRouter()

// ============================================
// State
// ============================================
const isCollapsed: Ref<boolean> = ref(false)
const notificationCount: Ref<number> = ref(0)
const username: Ref<string> = ref('Admin')

// Market-specific state
const selectedPeriod: Ref<string> = ref('1d')
const isRefreshing: Ref<boolean> = ref(false)
const isRealtime: Ref<boolean> = ref(true)
const refreshInterval: Ref<NodeJS.Timeout | null> = ref(null)

// Market overview data
const marketOverview: Ref<MarketOverview> = ref({
  shIndex: '3,245.67',
  shIndexChange: 1.23,
  szIndex: '10,876.54',
  szIndexChange: -0.56,
  cyIndex: '2,345.89',
  cyIndexChange: 2.34,
  upCount: 2345,
  downCount: 1876,
  flatCount: 234,
  heat: '高',
  amount: '8,765',
  limitUp: 56,
  limitDown: 12
})

// ============================================
// Computed Properties
// ============================================
const sidebarWidth: ComputedRef<string> = computed((): string => {
  return isCollapsed.value ? '64px' : '220px'
})

const activeMenu: ComputedRef<string> = computed((): string => {
  return route.path
})

const breadcrumbs: ComputedRef<BreadcrumbItem[]> = computed((): BreadcrumbItem[] => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title as string
  }))
})

// ============================================
// Methods
// ============================================
const toggleSidebar = (): void => {
  isCollapsed.value = !isCollapsed.value
}

const handleMenuSelect = (index: string): void => {
  if (index && index.startsWith('/')) {
    router.push(index)
  }
}

const handleUserCommand = async (command: UserCommand): Promise<void> => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗?',
          '退出确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // User cancelled
      }
      break
  }
}

// Market-specific methods
const handlePeriodChange = (period: string): void => {
  ElMessage.info(`切换到 ${period} 周期`)
  // TODO: Emit event to parent or call API to reload data
}

const handleRefresh = async (): Promise<void> => {
  isRefreshing.value = true
  try {
    // TODO: Call API to refresh market data
    await new Promise<void>(resolve => setTimeout(resolve, 1000))
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    isRefreshing.value = false
  }
}

const handleExport = (format: string): void => {
  ElMessage.info(`导出为 ${format.toUpperCase()}`)
  // TODO: Implement export functionality
}

const handleRealtimeToggle = (value: boolean): void => {
  if (value) {
    startRealtimeUpdates()
    ElMessage.success('已开启实时更新')
  } else {
    stopRealtimeUpdates()
    ElMessage.info('已暂停实时更新')
  }
}

const getChangeClass = (change: number): ChangeClass => {
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
}

const startRealtimeUpdates = (): void => {
  if (refreshInterval.value) return

  refreshInterval.value = setInterval(() => {
    // TODO: Fetch real-time market data
    // Simulate data updates
    marketOverview.value.shIndex = (3000 + Math.random() * 500).toFixed(2)
    marketOverview.value.shIndexChange = parseFloat((Math.random() * 4 - 2).toFixed(2))
  }, 3000)
}

const stopRealtimeUpdates = (): void => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// ============================================
// Lifecycle
// ============================================
onMounted((): void => {
  if (isRealtime.value) {
    startRealtimeUpdates()
  }
})

onUnmounted((): void => {
  stopRealtimeUpdates()
})

// Watch for route changes
watch(() => route.path, (newPath: string): void => {
  console.log('Route changed:', newPath)
}, { immediate: true })
</script>

<style scoped lang="scss">
// ============================================
// Market Layout Container
// ============================================
.market-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-primary);
}

// ============================================
// Sidebar Styles (inherited from MainLayout)
// ============================================
.layout-sidebar {
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-base);
  transition: width var(--transition-base);
  overflow-x: hidden;
  overflow-y: auto;

  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-primary);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-base);
    border-radius: 3px;

    &:hover {
      background: var(--border-light);
    }
  }

  &.is-collapsed {
    .sidebar-logo {
      .logo-text {
        display: none;
      }

      .logo-text-short {
        display: block;
      }
    }
  }
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border-dark);
  background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-secondary) 100%);

  .logo-text {
    font-size: 24px;
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin: 0;
    letter-spacing: 1px;
    display: block;
  }

  .logo-text-short {
    font-size: 20px;
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin: 0;
    display: none;
  }

  .logo-fade-enter-active,
  .logo-fade-leave-active {
    transition: opacity var(--transition-base);
  }

  .logo-fade-enter-from,
  .logo-fade-leave-to {
    opacity: 0;
  }
}

.sidebar-menu {
  border-right: none;
  padding: var(--spacing-sm) 0;

  // Menu item hover effect
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    margin: 0 var(--spacing-sm);
    border-radius: var(--radius-md);
    color: var(--text-secondary);

    &:hover {
      background-color: var(--bg-hover);
      color: var(--text-primary);
    }
  }

  // Active menu item
  :deep(.el-menu-item.is-active) {
    background-color: var(--color-primary-bg);
    color: var(--color-primary);
    font-weight: var(--font-weight-medium);

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background-color: var(--color-primary);
      border-radius: 0 2px 2px 0;
    }
  }

  // Submenu
  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      margin: 0 var(--spacing-sm);
      border-radius: var(--radius-md);
    }

    .el-menu {
      background-color: var(--bg-card);

      .el-menu-item {
        padding-left: 48px !important;
        margin: 0 var(--spacing-sm);
      }
    }
  }
}

// ============================================
// Main Container
// ============================================
.layout-main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// ============================================
// Header Styles
// ============================================
.layout-header {
  height: 60px;
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
  box-shadow: var(--shadow-1);
  z-index: var(--z-index-sticky);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.collapse-toggle {
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-base);

  &:hover {
    color: var(--color-primary);
  }
}

.breadcrumb {
  :deep(.el-breadcrumb__item) {
    .el-breadcrumb__inner {
      color: var(--text-secondary);
      font-weight: var(--font-weight-normal);

      &:hover {
        color: var(--color-primary);
      }
    }

    &:last-child {
      .el-breadcrumb__inner {
        color: var(--text-primary);
        font-weight: var(--font-weight-medium);
      }
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-action {
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);

  &:hover {
    color: var(--color-primary);
    background-color: var(--bg-hover);
  }
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background-color var(--transition-base);

  &:hover {
    background-color: var(--bg-hover);
  }

  .user-avatar {
    background-color: var(--color-primary);
    color: var(--text-primary);
  }

  .username {
    color: var(--text-primary);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
  }

  .dropdown-arrow {
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

// ============================================
// Market Toolbar (MarketLayout Specific)
// ============================================
.market-toolbar {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  align-items: center;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);

  &.toolbar-right {
    margin-left: auto;
  }
}

.toolbar-label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.realtime-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-base);
  transition: all var(--transition-base);

  &.is-active {
    border-color: var(--color-up);
    background-color: var(--color-up-bg);

    .indicator-dot {
      background-color: var(--color-up);
      animation: pulse 1.5s ease-in-out infinite;
    }

    .indicator-text {
      color: var(--color-up);
    }
  }

  .indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--text-tertiary);
    transition: background-color var(--transition-base);
  }

  .indicator-text {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    font-weight: var(--font-weight-medium);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

// ============================================
// Market Overview Panel
// ============================================
.market-overview {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-base);
}

.overview-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-base);

  &:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-2);
  }

  .card-title {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-medium);
  }

  .card-value {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
  }

  .card-value-mini {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
  }

  .card-change {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .card-sub {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }
}

.text-up {
  color: var(--color-up);
}

.text-down {
  color: var(--color-down);
}

.text-flat {
  color: var(--color-flat);
}

.text-divider {
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

// ============================================
// Main Content Styles
// ============================================
.layout-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);

  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-primary);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-base);
    border-radius: var(--radius-md);

    &:hover {
      background: var(--border-light);
    }
  }
}

// ============================================
// Page Transition Animation
// ============================================
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all var(--transition-base);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

// ============================================
// Responsive Design
// ============================================
@media (max-width: 768px) {
  .market-toolbar {
    flex-direction: column;
    align-items: stretch;

    .toolbar-group {
      width: 100%;
      justify-content: center;

      &.toolbar-right {
        margin-left: 0;
      }
    }
  }

  .overview-card {
    margin-bottom: var(--spacing-md);
  }

  .layout-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: var(--z-index-fixed);
    transform: translateX(-100%);

    &.mobile-open {
      transform: translateX(0);
    }
  }

  .header-right {
    .username {
      display: none;
    }
  }

  .layout-main {
    padding: var(--spacing-md);
  }
}

@media (max-width: 576px) {
  .layout-header {
    padding: 0 var(--spacing-md);
  }

  .breadcrumb {
    display: none;
  }

  .market-toolbar {
    .el-radio-group {
      flex-wrap: wrap;
    }
  }

  .realtime-indicator {
    .indicator-text {
      display: none;
    }
  }
}
</style>
