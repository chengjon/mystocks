<template>
  <el-container class="risk-layout">
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
          <!-- Alert Notifications Badge -->
          <el-badge :value="criticalAlertCount" :hidden="criticalAlertCount === 0" class="header-action" type="danger">
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

      <!-- Risk-Specific Toolbar -->
      <div class="risk-toolbar">
        <!-- Risk Type Filter -->
        <div class="toolbar-group">
          <span class="toolbar-label">风险类型:</span>
          <el-select v-model="selectedRiskType" size="small" placeholder="选择风险类型" @change="handleRiskTypeChange">
            <el-option label="全部类型" value="all" />
            <el-option label="市场风险" value="market" />
            <el-option label="流动性风险" value="liquidity" />
            <el-option label="系统性风险" value="systemic" />
            <el-option label="信用风险" value="credit" />
            <el-option label="操作风险" value="operational" />
          </el-select>
        </div>

        <!-- Severity Level Filter -->
        <div class="toolbar-group">
          <span class="toolbar-label">严重级别:</span>
          <el-select v-model="selectedSeverity" size="small" placeholder="选择严重级别" @change="handleSeverityChange">
            <el-option label="全部级别" value="all" />
            <el-option label="严重" value="critical">
              <span class="severity-indicator severity-critical"></span>
              <span>严重</span>
            </el-option>
            <el-option label="高" value="high">
              <span class="severity-indicator severity-high"></span>
              <span>高</span>
            </el-option>
            <el-option label="中" value="medium">
              <span class="severity-indicator severity-medium"></span>
              <span>中</span>
            </el-option>
            <el-option label="低" value="low">
              <span class="severity-indicator severity-low"></span>
              <span>低</span>
            </el-option>
          </el-select>
        </div>

        <!-- Time Range Selector -->
        <div class="toolbar-group">
          <span class="toolbar-label">时间范围:</span>
          <el-select v-model="selectedTimeRange" size="small" @change="handleTimeRangeChange">
            <el-option label="最近1小时" value="1h" />
            <el-option label="今天" value="today" />
            <el-option label="最近7天" value="7d" />
            <el-option label="最近30天" value="30d" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>

        <!-- Alert Status Filter -->
        <div class="toolbar-group">
          <el-checkbox-group v-model="selectedStatuses" size="small" @change="handleStatusChange">
            <el-checkbox-button label="active">活跃</el-checkbox-button>
            <el-checkbox-button label="acknowledged">已确认</el-checkbox-button>
            <el-checkbox-button label="resolved">已解决</el-checkbox-button>
          </el-checkbox-group>
        </div>

        <!-- Actions -->
        <div class="toolbar-group toolbar-right">
          <el-button
            :icon="Notification"
            size="small"
            @click="handleTestAlert"
          >
            测试告警
          </el-button>
          <el-button
            :icon="Delete"
            size="small"
            :disabled="selectedAlerts.length === 0"
            @click="handleBatchAcknowledge"
          >
            批量确认 ({{ selectedAlerts.length }})
          </el-button>
          <el-button
            :loading="isRefreshing"
            :icon="Refresh"
            size="small"
            type="primary"
            @click="handleRefresh"
          >
            刷新
          </el-button>
        </div>
      </div>

      <!-- Risk Alert Panel -->
      <div class="risk-alert-panel">
        <el-row :gutter="16">
          <!-- Critical Alerts -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="alert-card alert-critical">
              <div class="card-header">
                <el-icon class="card-icon"><WarningFilled /></el-icon>
                <span class="card-title">严重告警</span>
              </div>
              <div class="card-value">{{ riskStats.critical }}</div>
              <div class="card-sub">需要立即处理</div>
              <el-button
                link
                type="danger"
                size="small"
                @click="viewAlertsBySeverity('critical')"
              >
                查看详情
              </el-button>
            </div>
          </el-col>

          <!-- High Severity Alerts -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="alert-card alert-high">
              <div class="card-header">
                <el-icon class="card-icon"><Warning /></el-icon>
                <span class="card-title">高级告警</span>
              </div>
              <div class="card-value">{{ riskStats.high }}</div>
              <div class="card-sub">需要尽快处理</div>
              <el-button
                link
                type="warning"
                size="small"
                @click="viewAlertsBySeverity('high')"
              >
                查看详情
              </el-button>
            </div>
          </el-col>

          <!-- Medium Severity Alerts -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="alert-card alert-medium">
              <div class="card-header">
                <el-icon class="card-icon"><InfoFilled /></el-icon>
                <span class="card-title">中级告警</span>
              </div>
              <div class="card-value">{{ riskStats.medium }}</div>
              <div class="card-sub">需要关注</div>
              <el-button
                link
                size="small"
                @click="viewAlertsBySeverity('medium')"
              >
                查看详情
              </el-button>
            </div>
          </el-col>

          <!-- Low Severity Alerts -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="alert-card alert-low">
              <div class="card-header">
                <el-icon class="card-icon"><InfoFilled /></el-icon>
                <span class="card-title">低级告警</span>
              </div>
              <div class="card-value">{{ riskStats.low }}</div>
              <div class="card-sub">提醒信息</div>
              <el-button
                link
                size="small"
                @click="viewAlertsBySeverity('low')"
              >
                查看详情
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Risk Metrics Dashboard -->
      <div class="risk-metrics-panel">
        <el-row :gutter="16">
          <!-- Value at Risk (VaR) -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="metric-card">
              <div class="metric-title">VaR (95%)</div>
              <div class="metric-value">{{ riskMetrics.var }}</div>
              <div class="metric-sub">万元</div>
            </div>
          </el-col>

          <!-- Maximum Drawdown -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="metric-card">
              <div class="metric-title">最大回撤</div>
              <div class="metric-value metric-down">{{ riskMetrics.maxDrawdown }}</div>
              <div class="metric-sub">%</div>
            </div>
          </el-col>

          <!-- Sharpe Ratio -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="metric-card">
              <div class="metric-title">夏普比率</div>
              <div :class="['metric-value', getSharpeClass(riskMetrics.sharpe)]">
                {{ riskMetrics.sharpe }}
              </div>
              <div class="metric-sub">风险调整收益</div>
            </div>
          </el-col>

          <!-- Volatility -->
          <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
            <div class="metric-card">
              <div class="metric-title">波动率</div>
              <div class="metric-value">{{ riskMetrics.volatility }}</div>
              <div class="metric-sub">年化</div>
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
import { ref, computed, watch, onMounted, onUnmounted, type Ref, type ComputedRef } from 'vue'
import {
  Notification,
  Delete,
  Refresh,
  Odometer,
  TrendCharts,
  Bell,
  Warning,
  CircleCheck
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
 * 风险告警统计
 */
interface RiskStats {
  critical: number
  high: number
  medium: number
  low: number
}

/**
 * 风险指标数据
 */
interface RiskMetrics {
  var: string
  maxDrawdown: string
  sharpe: string
  volatility: string
}

/**
 * 告警严重级别
 */
type SeverityLevel = 'critical' | 'high' | 'medium' | 'low'

/**
 * 指标变化类型
 */
type MetricClass = 'metric-up' | 'metric-flat' | 'metric-down'

// ============================================
// Composables
// ============================================
const route = useRoute()
const router = useRouter()

// ============================================
// State
// ============================================
const isCollapsed: Ref<boolean> = ref(false)
const criticalAlertCount: Ref<number> = ref(3)
const username: Ref<string> = ref('Admin')

// Risk-specific state
const selectedRiskType: Ref<string> = ref('all')
const selectedSeverity: Ref<string> = ref('all')
const selectedTimeRange: Ref<string> = ref('today')
const selectedStatuses: Ref<string[]> = ref(['active', 'acknowledged'])
const selectedAlerts: Ref<any[]> = ref([])
const isRefreshing: Ref<boolean> = ref(false)
const refreshInterval: Ref<ReturnType<typeof setInterval> | null> = ref(null)

// Risk statistics
const riskStats: Ref<RiskStats> = ref({
  critical: 3,
  high: 12,
  medium: 28,
  low: 45
})

// Risk metrics
const riskMetrics: Ref<RiskMetrics> = ref({
  var: '125.67',
  maxDrawdown: '-8.45',
  sharpe: '1.85',
  volatility: '18.23'
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

// Risk-specific methods
const handleRiskTypeChange = (type: string): void => {
  ElMessage.info(`风险类型: ${type}`)
  // TODO: Emit event or call API to filter alerts
}

const handleSeverityChange = (severity: string): void => {
  ElMessage.info(`严重级别: ${severity}`)
  // TODO: Emit event or call API to filter alerts
}

const handleTimeRangeChange = (range: string): void => {
  ElMessage.info(`时间范围: ${range}`)
  // TODO: Emit event or call API to filter alerts
}

const handleStatusChange = (statuses: string[]): void => {
  console.log('Alert statuses:', statuses)
  // TODO: Emit event or call API to filter alerts
}

const handleTestAlert = (): void => {
  ElNotification({
    title: '严重风险告警',
    message: '检测到市场异常波动，请立即关注！',
    type: 'error',
    duration: 0,
    position: 'top-right'
  })
}

const handleBatchAcknowledge = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要确认选中的 ${selectedAlerts.value.length} 条告警吗?`,
      '批量确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('批量确认成功')
    selectedAlerts.value = []
    // TODO: Call API to acknowledge alerts
  } catch {
    // User cancelled
  }
}

const handleRefresh = async (): Promise<void> => {
  isRefreshing.value = true
  try {
    // TODO: Call API to refresh risk data
    await new Promise<void>(resolve => setTimeout(resolve, 1000))
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    isRefreshing.value = false
  }
}

const viewAlertsBySeverity = (severity: SeverityLevel): void => {
  ElMessage.info(`查看${severity}级别告警`)
  selectedSeverity.value = severity
  // TODO: Navigate to alert list or open dialog
}

const getSharpeClass = (sharpe: string): MetricClass => {
  const value = parseFloat(sharpe)
  if (value >= 2) return 'metric-up'
  if (value >= 1) return 'metric-flat'
  return 'metric-down'
}

const startRealtimeUpdates = (): void => {
  if (refreshInterval.value) return

  refreshInterval.value = setInterval(() => {
    // TODO: Fetch real-time risk data
    // Simulate data updates
    riskStats.value.critical = Math.floor(Math.random() * 5)
    riskStats.value.high = Math.floor(Math.random() * 15) + 5
    riskMetrics.value.var = (100 + Math.random() * 50).toFixed(2)

    // Update critical alert count
    criticalAlertCount.value = riskStats.value.critical
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
// Risk Layout Container
// ============================================
.risk-layout {
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
// Risk Toolbar (RiskLayout Specific)
// ============================================
.risk-toolbar {
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

// Severity indicator in select options
.severity-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;

  &.severity-critical {
    background-color: var(--color-danger);
  }

  &.severity-high {
    background-color: var(--color-warning);
  }

  &.severity-medium {
    background-color: var(--color-info);
  }

  &.severity-low {
    background-color: var(--color-success);
  }
}

// ============================================
// Risk Alert Panel
// ============================================
.risk-alert-panel {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-base);
}

.alert-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
  margin-bottom: var(--spacing-md);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
  }

  &.alert-critical {
    border-color: var(--color-danger);

    &::before {
      background-color: var(--color-danger);
    }

    &:hover {
      box-shadow: 0 0 0 2px rgba(255, 23, 68, 0.2);
    }
  }

  &.alert-high {
    border-color: var(--color-warning);

    &::before {
      background-color: var(--color-warning);
    }

    &:hover {
      box-shadow: 0 0 0 2px rgba(255, 171, 0, 0.2);
    }
  }

  &.alert-medium {
    border-color: var(--color-info);

    &::before {
      background-color: var(--color-info);
    }

    &:hover {
      box-shadow: 0 0 0 2px rgba(0, 176, 255, 0.2);
    }
  }

  &.alert-low {
    border-color: var(--color-success);

    &::before {
      background-color: var(--color-success);
    }

    &:hover {
      box-shadow: 0 0 0 2px rgba(0, 200, 83, 0.2);
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
  }

  .card-icon {
    font-size: 20px;

    .alert-critical & {
      color: var(--color-danger);
    }

    .alert-high & {
      color: var(--color-warning);
    }

    .alert-medium &,
    .alert-low & {
      color: var(--color-info);
    }
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
  }

  .card-sub {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin-bottom: var(--spacing-sm);
  }
}

// ============================================
// Risk Metrics Dashboard
// ============================================
.risk-metrics-panel {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-base);
}

.metric-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  text-align: center;
  transition: all var(--transition-base);
  margin-bottom: var(--spacing-md);

  &:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-2);
  }

  .metric-title {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-medium);
  }

  .metric-value {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);

    &.metric-up {
      color: var(--color-up);
    }

    &.metric-down {
      color: var(--color-down);
    }
  }

  .metric-sub {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
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
  .risk-toolbar {
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

    .el-select,
    .el-checkbox-group {
      width: 100% !important;
    }
  }

  .alert-card,
  .metric-card {
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

  .risk-toolbar {
    .toolbar-label {
      display: none;
    }
  }

  .alert-card {
    .card-value {
      font-size: 24px;
    }
  }

  .metric-card {
    .metric-value {
      font-size: var(--font-size-base);
    }
  }
}
</style>
