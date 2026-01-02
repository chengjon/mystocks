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
          <h1 v-if="!isCollapsed" class="logo-text">MYSTOCKS</h1>
          <h1 v-else class="logo-text-short">MS</h1>
        </transition>
        <!-- Web3 gradient line under logo -->
        <div v-if="!isCollapsed" class="logo-divider"></div>
      </div>

      <!-- Menu Items -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        background-color="transparent"
        text-color="var(--artdeco-fg-secondary)"
        active-text-color="var(--artdeco-accent-primary)"
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

      <!-- Web3 corner decoration (bottom of sidebar) -->
      <div class="sidebar-footer-decoration"></div>
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
//   COMPONENT: MainLayout (Web3 Redesign)
//   Bitcoin DeFi Web3 Style Main Layout
//
//   Design Philosophy:
//   - True void background (#030304)
//   - Grid pattern (blockchain network effect)
//   - Orange active states
//   - Glass morphism header
//   - Rounded corners (16px)
// ============================================

// ============================================
//   TYPE DEFINITIONS - 类型定义
// ============================================

interface BreadcrumbItem {
  path: string
  title: string
}

type UserCommand = 'profile' | 'settings' | 'logout'

// ============================================
//   COMPOSABLES - 组合式函数
// ============================================

const route = useRoute()
const router = useRouter()

// ============================================
//   STATE - 响应式状态
// ============================================

const isCollapsed: Ref<boolean> = ref(false)
const notificationCount: Ref<number> = ref(0)
const username: Ref<string> = ref('Admin')

// ============================================
//   COMPUTED PROPERTIES - 计算属性
// ============================================

const sidebarWidth: ComputedRef<string> = computed((): string => {
  return isCollapsed.value ? '64px' : '240px'
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
//   METHODS - 方法
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
//   LIFECYCLE - 生命周期
// ============================================

watch(() => route.path, (newPath: string): void => {
  console.log('Route changed:', newPath)
}, { immediate: true })
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   ARTDECO PATTERN BACKGROUND
//   Diagonal crosshatch pattern
// ============================================

@mixin artdeco-grid-bg {
  background-color: var(--artdeco-bg-primary);
  background-size: 40px 40px, 40px 40px;
  background-image:
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 2px,
      rgba(212, 175, 55, 0.03) 2px,
      rgba(212, 175, 55, 0.03) 4px
    ),
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 2px,
      rgba(212, 175, 55, 0.03) 2px,
      rgba(212, 175, 55, 0.03) 4px
    );
}

// ============================================
//   MAIN LAYOUT CONTAINER - 主布局容器
//   Web3 grid pattern background
// ============================================

.main-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;

  // MANDATORY: Grid pattern background
  @include artdeco-grid-bg;
}

// ============================================
//   SIDEBAR STYLES - 侧边栏样式
//   Dark matter background, grid pattern
// ============================================

.layout-sidebar {
  // MANDATORY: Dark matter background
  background-color: var(--artdeco-bg-surface);

  // MANDATORY: Ultra-thin border (white/10)
  border-right: 1px solid var(--artdeco-border-subtle);

  // Smooth width transition
  transition: width var(--artdeco-duration-base) var(--artdeco-ease-out);

  // Position relative for decorations
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;

  // Custom scrollbar (Web3 themed)
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--artdeco-bg-primary);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(247, 147, 26, 0.3);
    border-radius: var(--artdeco-radius-sm);

    &:hover {
      background: var(--artdeco-accent-primary);
    }
  }

  // Grid pattern overlay (subtle)
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: 50px 50px;
    background-image:
      linear-gradient(to right, rgba(30, 41, 59, 0.3) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(30, 41, 59, 0.3) 1px, transparent 1px);
    opacity: 0.5;
    pointer-events: none;
    z-index: 0;
  }
}

// ============================================
//   LOGO AREA - Logo区域
//   Space Grotesk font, gradient text
// ============================================

.sidebar-logo {
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--artdeco-border-subtle);
  background: linear-gradient(
    180deg,
    var(--artdeco-bg-surface) 0%,
    rgba(15, 17, 21, 0.5) 100%
  );
  position: relative;
  padding: var(--artdeco-spacing-4);
  z-index: 1;
}

.logo-text {
  // MANDATORY: Space Grotesk font (heading)
  font-family: var(--artdeco-font-heading);

  // MANDATORY: Uppercase
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);

  // MANDATORY: Gradient text (orange to gold)
  background: var(--artdeco-gradient-gold);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;

  // Size and weight
  font-size: var(--artdeco-text-2xl);
  font-weight: var(--artdeco-weight-bold);

  margin: 0;
  display: block;
  line-height: var(--artdeco-leading-tight);
}

.logo-text-short {
  font-family: var(--artdeco-font-heading);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);

  // Gradient text
  background: var(--artdeco-gradient-gold);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;

  font-size: var(--artdeco-text-xl);
  font-weight: var(--artdeco-weight-bold);
  margin: 0;
  display: none;
  line-height: var(--artdeco-leading-tight);
}

// MANDATORY: Gradient line under logo
.logo-divider {
  width: 60%;
  height: 2px;
  background: var(--artdeco-gradient-orange);
  margin-top: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-full);
}

// Logo transition
.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity var(--artdeco-duration-base);
}

.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

// ============================================
//   SIDEBAR MENU - 侧边栏菜单
//   Web3 hover effects (orange glow)
// ============================================

.sidebar-menu {
  border-right: none;
  padding: var(--artdeco-spacing-4) 0;
  position: relative;
  z-index: 1;

  // Menu item hover effect
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    margin: 0 var(--artdeco-spacing-3);

    // MANDATORY: Rounded corners (8px)
    border-radius: var(--artdeco-radius-sm);

    // Web3 typography
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    font-size: var(--artdeco-text-sm);

    color: var(--artdeco-fg-secondary);

    transition: all var(--artdeco-duration-base) var(--artdeco-ease-out);

    &:hover {
      background-color: rgba(247, 147, 26, 0.1);
      color: var(--artdeco-accent-primary);
    }
  }

  // Active menu item (MANDATORY: Orange with glow)
  :deep(.el-menu-item.is-active) {
    background: linear-gradient(90deg, rgba(247, 147, 26, 0.15), transparent);
    color: var(--artdeco-accent-primary);
    font-weight: var(--artdeco-weight-semibold);

    // MANDATORY: Orange glow on active item
    box-shadow: 0 0 20px -5px rgba(247, 147, 26, 0.3);

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 60%;
      background: var(--artdeco-accent-primary);
      border-radius: 0 var(--artdeco-radius-full) var(--artdeco-radius-full) 0;
    }
  }

  // Submenu
  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      margin: 0 var(--artdeco-spacing-3);
      border-radius: var(--artdeco-radius-sm);
    }

    .el-menu {
      background-color: rgba(3, 3, 4, 0.5);

      .el-menu-item {
        padding-left: 48px !important;
        margin: 0 var(--artdeco-spacing-3);

        // Nested item styling
        font-size: var(--artdeco-text-xs);
        letter-spacing: var(--artdeco-tracking-normal);
      }
    }
  }
}

// ============================================
//   SIDEBAR FOOTER DECORATION - 底部装饰
//   Bitcoin orange corner embellishment
// ============================================

.sidebar-footer-decoration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 16px;
  height: 16px;
  border-bottom: 2px solid var(--artdeco-accent-primary);
  border-right: 2px solid var(--artdeco-accent-primary);
  border-bottom-right-radius: 4px;
  pointer-events: none;
  opacity: 0.6;
  z-index: 1;
}

// ============================================
//   MAIN CONTAINER - 主容器
// ============================================

.layout-main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// ============================================
//   HEADER STYLES - 顶部导航栏样式
//   Glass morphism, orange accents
// ============================================

.layout-header {
  height: 64px;
  padding: 0 var(--artdeco-spacing-6);
  display: flex;
  align-items: center;
  justify-content: space-between;

  // MANDATORY: Glass morphism
  background: var(--artdeco-bg-glass-light);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);

  // MANDATORY: Ultra-thin border (bottom)
  border-bottom: 1px solid var(--artdeco-border-subtle);

  z-index: var(--artdeco-z-sticky);

  // Position relative for effects
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-6);
}

// Collapse toggle
.collapse-toggle {
  font-size: 20px;
  color: var(--artdeco-fg-secondary);
  cursor: pointer;
  padding: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-sm);
  transition: all var(--artdeco-duration-base);

  &:hover {
    color: var(--artdeco-accent-primary);
    background: var(--artdeco-bg-glass-light);
    box-shadow: var(--artdeco-glow-orange-sm);
  }
}

// Breadcrumb (monospace font)
.breadcrumb {
  :deep(.el-breadcrumb__item) {
    .el-breadcrumb__inner {
      color: var(--artdeco-fg-secondary);
      font-weight: var(--artdeco-weight-normal);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      font-size: var(--artdeco-text-xs);
      font-family: var(--artdeco-font-mono);

      &:hover {
        color: var(--artdeco-accent-primary);
      }
    }

    &:last-child {
      .el-breadcrumb__inner {
        color: var(--artdeco-accent-primary);
        font-weight: var(--artdeco-weight-semibold);
      }
    }

    .el-breadcrumb__separator {
      color: var(--artdeco-fg-muted);
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
}

.header-action {
  font-size: 20px;
  color: var(--artdeco-fg-secondary);
  cursor: pointer;
  padding: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-sm);
  transition: all var(--artdeco-duration-base);

  &:hover {
    color: var(--artdeco-accent-primary);
    background: var(--artdeco-bg-glass-light);
  }
}

// User dropdown (glass morphism)
.user-dropdown {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);

  // MANDATORY: Rounded corners (pill)
  border-radius: var(--artdeco-radius-full);

  cursor: pointer;
  transition: all var(--artdeco-duration-base);
  border: 1px solid transparent;

  &:hover {
    background: var(--artdeco-bg-glass-light);
    border-color: var(--artdeco-border-hover);
  }

  .user-avatar {
    background: var(--artdeco-accent-primary);
    color: var(--artdeco-bg-primary);
  }

  .username {
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-weight-semibold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    font-family: var(--artdeco-font-heading);
  }

  .dropdown-arrow {
    font-size: 12px;
    color: var(--artdeco-fg-secondary);
  }
}

// ============================================
//   MAIN CONTENT - 主内容区域
//   Grid pattern background
// ============================================

.layout-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--artdeco-spacing-6);

  // MANDATORY: Grid pattern background
  @include artdeco-grid-bg;

  // Custom scrollbar (Web3 themed)
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--artdeco-bg-primary);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(247, 147, 26, 0.3);
    border: 1px solid var(--artdeco-accent-primary);
    border-radius: var(--artdeco-radius-sm);

    &:hover {
      background: var(--artdeco-accent-primary);
    }
  }
}

// ============================================
//   PAGE TRANSITION - 页面切换动画
//   Fast, smooth transitions
// ============================================

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all var(--artdeco-duration-base) var(--artdeco-ease-out);
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
//   RESPONSIVE DESIGN - 响应式设计
//   Mobile optimization
// ============================================

@media (max-width: 768px) {
  .layout-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: var(--artdeco-z-fixed);
    transform: translateX(-100%);
    transition: transform var(--artdeco-duration-base) var(--artdeco-ease-out);

    &.mobile-open {
      transform: translateX(0);
    }
  }

  .layout-header {
    height: 56px;
    padding: 0 var(--artdeco-spacing-4);
  }

  .header-right {
    .username {
      display: none;
    }
  }

  .layout-main {
    padding: var(--artdeco-spacing-4);
  }

  .breadcrumb {
    display: none;
  }
}

@media (max-width: 576px) {
  .layout-header {
    padding: 0 var(--artdeco-spacing-3);
  }

  .logo-text {
    font-size: var(--artdeco-text-xl);
  }
}
</style>
