<template>
  <el-container class="strategy-layout">
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
          <!-- Strategy Notifications Badge -->
          <el-badge :value="runningStrategyCount" :hidden="runningStrategyCount === 0" class="header-action">
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

      <!-- Strategy-Specific Toolbar -->
      <div class="strategy-toolbar">
        <!-- Strategy Type Filter -->
        <div class="toolbar-group">
          <span class="toolbar-label">策略类型:</span>
          <el-select v-model="selectedStrategyType" size="small" placeholder="选择策略类型" @change="handleStrategyTypeChange">
            <el-option label="全部类型" value="all" />
            <el-option label="趋势跟踪" value="trend" />
            <el-option label="均值回归" value="mean_reversion" />
            <el-option label="套利策略" value="arbitrage" />
            <el-option label="做市策略" value="market_making" />
            <el-option label="动量策略" value="momentum" />
            <el-option label="自定义策略" value="custom" />
          </el-select>
        </div>

        <!-- Strategy Status Filter -->
        <div class="toolbar-group">
          <span class="toolbar-label">运行状态:</span>
          <el-select v-model="selectedStatus" size="small" placeholder="选择状态" @change="handleStatusChange">
            <el-option label="全部状态" value="all" />
            <el-option label="运行中" value="running">
              <span class="status-indicator status-running"></span>
              <span>运行中</span>
            </el-option>
            <el-option label="已暂停" value="paused">
              <span class="status-indicator status-paused"></span>
              <span>已暂停</span>
            </el-option>
            <el-option label="已停止" value="stopped">
              <span class="status-indicator status-stopped"></span>
              <span>已停止</span>
            </el-option>
            <el-option label="测试中" value="testing">
              <span class="status-indicator status-testing"></span>
              <span>测试中</span>
            </el-option>
          </el-select>
        </div>

        <!-- Time Range Selector -->
        <div class="toolbar-group">
          <span class="toolbar-label">回测时间:</span>
          <el-select v-model="selectedTimeRange" size="small" @change="handleTimeRangeChange">
            <el-option label="最近1月" value="1m" />
            <el-option label="最近3月" value="3m" />
            <el-option label="最近6月" value="6m" />
            <el-option label="最近1年" value="1y" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>

        <!-- Sort Options -->
        <div class="toolbar-group">
          <span class="toolbar-label">排序方式:</span>
          <el-select v-model="selectedSort" size="small" @change="handleSortChange">
            <el-option label="收益率" value="return" />
            <el-option label="夏普比率" value="sharpe" />
            <el-option label="最大回撤" value="drawdown" />
            <el-option label="胜率" value="winrate" />
            <el-option label="创建时间" value="created" />
          </el-select>
        </div>

        <!-- Actions -->
        <div class="toolbar-group toolbar-right">
          <el-button
            :icon="Plus"
            size="small"
            type="primary"
            @click="handleCreateStrategy"
          >
            新建策略
          </el-button>
          <el-button
            :icon="VideoPlay"
            size="small"
            :disabled="selectedStrategies.length === 0"
            @click="handleBatchStart"
          >
            批量启动 ({{ selectedStrategies.length }})
          </el-button>
          <el-button
            :icon="Refresh"
            size="small"
            :loading="isRefreshing"
            @click="handleRefresh"
          >
            刷新
          </el-button>
        </div>
      </div>

      <!-- Strategy Performance Overview Panel -->
      <div class="strategy-overview-panel">
        <el-row :gutter="16">
          <!-- Total Strategies -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="strategy-card">
              <div class="card-header">
                <el-icon class="card-icon"><Management /></el-icon>
                <span class="card-title">策略总数</span>
              </div>
              <div class="card-value">{{ strategyStats.total }}</div>
              <div class="card-sub">运行中: {{ strategyStats.running }}</div>
              <el-button
                link
                type="primary"
                size="small"
                @click="viewStrategiesByStatus('all')"
              >
                查看全部
              </el-button>
            </div>
          </el-col>

          <!-- Average Return -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="strategy-card">
              <div class="card-header">
                <el-icon class="card-icon"><TrendCharts /></el-icon>
                <span class="card-title">平均收益</span>
              </div>
              <div :class="['card-value', getReturnClass(strategyStats.avgReturn)]">
                {{ strategyStats.avgReturn }}%
              </div>
              <div class="card-sub">年化收益率</div>
              <el-button
                link
                size="small"
                @click="sortByMetric('return')"
              >
                查看排行
              </el-button>
            </div>
          </el-col>

          <!-- Average Sharpe Ratio -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="strategy-card">
              <div class="card-header">
                <el-icon class="card-icon"><DataLine /></el-icon>
                <span class="card-title">平均夏普</span>
              </div>
              <div class="card-value">{{ strategyStats.avgSharpe }}</div>
              <div class="card-sub">风险调整收益</div>
              <el-button
                link
                size="small"
                @click="sortByMetric('sharpe')"
              >
                查看排行
              </el-button>
            </div>
          </el-col>

          <!-- Win Rate -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="strategy-card">
              <div class="card-header">
                <el-icon class="card-icon"><Trophy /></el-icon>
                <span class="card-title">平均胜率</span>
              </div>
              <div class="card-value">{{ strategyStats.avgWinRate }}%</div>
              <div class="card-sub">交易成功率</div>
              <el-button
                link
                size="small"
                @click="sortByMetric('winrate')"
              >
                查看排行
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Strategy List/Detail Area -->
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
import {
  Plus,
  VideoPlay,
  Refresh,
  Odometer,
  TrendCharts,
  MagicStick
} from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

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
 * 策略统计数据
 */
interface StrategyStats {
  total: number
  running: number
  avgReturn: string
  avgSharpe: string
  avgWinRate: string
}

/**
 * 策略运行状态
 */
type StrategyStatus = 'running' | 'paused' | 'stopped' | 'testing'

/**
 * 策略收益变化类型
 */
type StrategyReturnClass = 'strategy-up' | 'strategy-down' | 'strategy-flat'

/**
 * 排序指标类型
 */
type SortMetric = 'return' | 'sharpe' | 'drawdown' | 'winrate' | 'created'

// ============================================
// Composables
// ============================================
const route = useRoute()
const router = useRouter()

// ============================================
// State
// ============================================
const isCollapsed: Ref<boolean> = ref(false)
const runningStrategyCount: Ref<number> = ref(5)
const username: Ref<string> = ref('Admin')

// Strategy-specific state
const selectedStrategyType: Ref<string> = ref('all')
const selectedStatus: Ref<string> = ref('all')
const selectedTimeRange: Ref<string> = ref('1y')
const selectedSort: Ref<string> = ref('return')
const selectedStrategies: Ref<any[]> = ref([])
const isRefreshing: Ref<boolean> = ref(false)
const refreshInterval: Ref<ReturnType<typeof setInterval> | null> = ref(null)

// Strategy statistics
const strategyStats: Ref<StrategyStats> = ref({
  total: 24,
  running: 5,
  avgReturn: '18.5',
  avgSharpe: '1.65',
  avgWinRate: '62.3'
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

// Strategy-specific methods
const handleStrategyTypeChange = (type: string): void => {
  ElMessage.info(`策略类型: ${type}`)
  // TODO: Emit event or call API to filter strategies
}

const handleStatusChange = (status: string): void => {
  ElMessage.info(`运行状态: ${status}`)
  // TODO: Emit event or call API to filter strategies
}

const handleTimeRangeChange = (range: string): void => {
  ElMessage.info(`回测时间: ${range}`)
  // TODO: Emit event or call API to update backtest period
}

const handleSortChange = (sort: string): void => {
  ElMessage.info(`排序方式: ${sort}`)
  // TODO: Emit event or call API to sort strategies
}

const handleCreateStrategy = (): void => {
  ElMessage.info('打开策略创建向导...')
  // TODO: Open strategy creation dialog or navigate to create page
}

const handleBatchStart = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要启动选中的 ${selectedStrategies.value.length} 个策略吗?`,
      '批量启动',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('批量启动成功')
    selectedStrategies.value = []
    // TODO: Call API to start strategies
  } catch {
    // User cancelled
  }
}

const handleRefresh = async (): Promise<void> => {
  isRefreshing.value = true
  try {
    // TODO: Call API to refresh strategy data
    await new Promise<void>(resolve => setTimeout(resolve, 1000))
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    isRefreshing.value = false
  }
}

const viewStrategiesByStatus = (status: string): void => {
  ElMessage.info(`查看${status}策略`)
  selectedStatus.value = status
  // TODO: Navigate to strategy list or filter
}

const sortByMetric = (metric: SortMetric): void => {
  ElMessage.info(`按${metric}排序`)
  selectedSort.value = metric
  // TODO: Sort strategies by metric
}

const getReturnClass = (returnValue: string): StrategyReturnClass => {
  const value = parseFloat(returnValue)
  if (value > 0) return 'strategy-up'
  if (value < 0) return 'strategy-down'
  return 'strategy-flat'
}

const startRealtimeUpdates = (): void => {
  if (refreshInterval.value) return

  refreshInterval.value = setInterval(() => {
    // TODO: Fetch real-time strategy data
    // Simulate data updates
    strategyStats.value.running = Math.floor(Math.random() * 10)
    strategyStats.value.avgReturn = (10 + Math.random() * 20).toFixed(1)

    // Update running strategy count
    runningStrategyCount.value = strategyStats.value.running
  }, 5000)
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
  startRealtimeUpdates()
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
// Strategy Layout Container
// ============================================
.strategy-layout {
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
// Strategy Toolbar (StrategyLayout Specific)
// ============================================
.strategy-toolbar {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
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
  white-space: nowrap;
}

// Status indicator in select options
.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;

  &.status-running {
    background-color: var(--color-success);
  }

  &.status-paused {
    background-color: var(--color-warning);
  }

  &.status-stopped {
    background-color: var(--color-danger);
  }

  &.status-testing {
    background-color: var(--color-info);
  }
}

// ============================================
// Strategy Overview Panel
// ============================================
.strategy-overview-panel {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-base);
}

.strategy-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
  margin-bottom: var(--spacing-md);

  &:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-2);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
  }

  .card-icon {
    font-size: 20px;
    color: var(--color-primary);
  }

  .card-title {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
  }

  .card-value {
    font-size: 32px;
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);

    &.strategy-up {
      color: var(--color-up);
    }

    &.strategy-down {
      color: var(--color-down);
    }

    &.strategy-flat {
      color: var(--color-flat);
    }
  }

  .card-sub {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin-bottom: var(--spacing-sm);
  }
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
  .strategy-toolbar {
    flex-direction: column;
    align-items: stretch;

    .toolbar-group {
      width: 100%;
      justify-content: flex-start;

      &.toolbar-right {
        margin-left: 0;
        flex-direction: column;

        .el-button {
          width: 100%;
        }
      }
    }

    .el-select {
      width: 100% !important;
    }
  }

  .strategy-card {
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

  .strategy-toolbar {
    .toolbar-label {
      display: none;
    }
  }

  .strategy-card {
    .card-value {
      font-size: 24px;
    }
  }
}
</style>
