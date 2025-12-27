<template>
  <el-container class="main-layout">
    <!-- Sidebar Navigation -->
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
          <!-- Theme Toggle (Future) -->
          <!-- <el-icon class="header-action"><Sunny /></el-icon> -->

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
import { ref, computed, watch, type Ref, type ComputedRef } from 'vue'
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

// ============================================
// Lifecycle
// ============================================
// Watch for route changes to update active menu
watch(() => route.path, (newPath: string): void => {
  console.log('Route changed:', newPath)
}, { immediate: true })
</script>

<style scoped lang="scss">
// ============================================
// Main Layout Container
// ============================================
.main-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-primary);
}

// ============================================
// Sidebar Styles
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
}
</style>
