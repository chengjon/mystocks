<template>
  <!-- Mobile Overlay (only visible on mobile when sidebar is open) -->
  <transition name="fade">
    <div
      v-if="isMobile && isOpen"
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>
  </transition>

  <!-- Sidebar Container -->
  <aside
    class="responsive-sidebar"
    :class="sidebarClasses"
    :style="sidebarStyle"
    role="navigation"
    aria-label="Main navigation"
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
      <template v-for="menu in menus" :key="menu.index">
        <!-- Submenu -->
        <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.index">
          <template #title>
            <el-icon v-if="menu.icon">
              <component :is="menu.icon" />
            </el-icon>
            <span>{{ menu.title }}</span>
          </template>
          <el-menu-item
            v-for="child in menu.children"
            :key="child.index"
            :index="child.index"
          >
            <el-icon v-if="child.icon">
              <component :is="child.icon" />
            </el-icon>
            <template #title>{{ child.title }}</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- Single Menu Item -->
        <el-menu-item v-else :index="menu.index">
          <el-icon v-if="menu.icon">
            <component :is="menu.icon" />
          </el-icon>
          <template #title>{{ menu.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>

    <!-- Collapse Toggle (Desktop) -->
    <div v-if="!isMobile" class="collapse-toggle-container">
      <el-icon class="collapse-toggle" @click="toggleCollapse">
        <Fold v-if="!isCollapsed" />
        <Expand v-else />
      </el-icon>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Odometer,
  TrendCharts,
  DataLine,
  DataAnalysis,
  Grid,
  Warning,
  Document,
  Monitor,
  Tickets,
  Management,
  Histogram,
  List,
  Setting,
  Money,
  ShoppingCart,
  Flag,
  Search,
  Fold,
  Expand
} from '@element-plus/icons-vue'

// ============================================
// Props & Emits
// ============================================
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  menus: {
    type: Array,
    default: () => [
      {
        index: '/dashboard',
        title: '仪表盘',
        icon: Odometer
      },
      {
        index: 'market',
        title: '市场行情',
        icon: TrendCharts,
        children: [
          { index: '/market', title: '实时行情' },
          { index: '/tdx-market', title: 'TDX行情' }
        ]
      },
      {
        index: 'market-data',
        title: '市场数据',
        icon: DataLine,
        children: [
          { index: '/market-data/fund-flow', title: '资金流向', icon: Money },
          { index: '/market-data/etf', title: 'ETF行情', icon: TrendCharts },
          { index: '/market-data/chip-race', title: '竞价抢筹', icon: ShoppingCart },
          { index: '/market-data/lhb', title: '龙虎榜', icon: Flag },
          { index: '/market-data/wencai', title: '问财筛选', icon: Search }
        ]
      },
      { index: '/stocks', title: '股票管理', icon: Grid },
      { index: '/analysis', title: '数据分析', icon: DataAnalysis },
      { index: '/technical', title: '技术分析', icon: DataLine },
      { index: '/indicators', title: '指标库', icon: Grid },
      { index: '/risk', title: '风险监控', icon: Warning },
      { index: '/announcement', title: '公告监控', icon: Document },
      { index: '/realtime', title: '实时监控', icon: Monitor },
      { index: '/trade', title: '交易管理', icon: Tickets },
      { index: '/strategy', title: '策略管理', icon: Management },
      { index: '/backtest', title: '回测分析', icon: Histogram },
      { index: '/tasks', title: '任务管理', icon: List },
      { index: '/settings', title: '系统设置', icon: Setting }
    ]
  }
})

const emit = defineEmits(['update:modelValue', 'update:collapsed', 'menu-select'])

// ============================================
// Composables
// ============================================
const route = useRoute()
const router = useRouter()

// ============================================
// State
// ============================================
const isOpen = ref(props.modelValue)
const isCollapsed = ref(props.collapsed)
const isMobile = ref(false)
const touchStartX = ref(0)
const touchEndX = ref(0)

// ============================================
// Computed Properties
// ============================================
const sidebarClasses = computed(() => {
  return {
    'is-collapsed': isCollapsed.value,
    'is-mobile': isMobile.value,
    'is-open': isOpen.value
  }
})

const sidebarStyle = computed(() => {
  if (isMobile.value) {
    return {
      width: isOpen.value ? '220px' : '0px',
      transform: isOpen.value ? 'translateX(0)' : 'translateX(-100%)'
    }
  } else {
    return {
      width: isCollapsed.value ? '64px' : '220px'
    }
  }
})

const activeMenu = computed(() => {
  return route.path
})

// ============================================
// Methods
// ============================================
const closeSidebar = () => {
  isOpen.value = false
  emit('update:modelValue', false)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('update:collapsed', isCollapsed.value)
}

const handleMenuSelect = (index) => {
  if (index && index.startsWith('/')) {
    router.push(index)
  }
  emit('menu-select', index)

  // Close sidebar on mobile after selection
  if (isMobile.value) {
    closeSidebar()
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  // Auto-collapse on mobile
  if (isMobile.value && isOpen.value) {
    closeSidebar()
  }
}

// Touch gesture handlers
const handleTouchStart = (e) => {
  touchStartX.value = e.changedTouches[0].screenX
}

const handleTouchMove = (e) => {
  if (!isMobile.value) return

  touchEndX.value = e.changedTouches[0].screenX
  const swipeDistance = touchEndX.value - touchStartX.value

  // Swipe right to open
  if (swipeDistance > 50 && !isOpen.value) {
    isOpen.value = true
    emit('update:modelValue', true)
  }
  // Swipe left to close
  else if (swipeDistance < -50 && isOpen.value) {
    closeSidebar()
  }
}

const handleTouchEnd = () => {
  touchStartX.value = 0
  touchEndX.value = 0
}

// Keyboard navigation
const handleKeydown = (e) => {
  // ESC key to close sidebar on mobile
  if (e.key === 'Escape' && isMobile.value && isOpen.value) {
    closeSidebar()
  }
}

// ============================================
// Lifecycle
// ============================================
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: true })
  window.addEventListener('touchend', handleTouchEnd)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
  window.removeEventListener('keydown', handleKeydown)
})

// Watch for prop changes
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue
})

watch(() => props.collapsed, (newValue) => {
  isCollapsed.value = newValue
})

// Watch route changes
watch(() => route.path, () => {
  // Update active menu automatically
}, { immediate: true })
</script>

<style scoped lang="scss">
// ============================================
// Sidebar Container
// ============================================
.responsive-sidebar {
  position: relative;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-base);
  transition: all var(--transition-base);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100vh;

  // Desktop behavior
  @media (min-width: 768px) {
    position: sticky;
    top: 0;
    z-index: var(--z-index-sticky);
  }

  // Mobile behavior
  &.is-mobile {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: var(--z-index-modal);
    box-shadow: var(--shadow-3);

    &.is-open {
      border-right: 1px solid var(--border-base);
    }
  }

  // Collapsed state (desktop)
  &.is-collapsed:not(.is-mobile) {
    .sidebar-logo {
      .logo-text {
        display: none;
      }

      .logo-text-short {
        display: block;
      }
    }

    .collapse-toggle-container {
      .collapse-toggle {
        transform: rotate(180deg);
      }
    }
  }

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
}

// ============================================
// Mobile Overlay (Mask)
// ============================================
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-overlay);
  z-index: calc(var(--z-index-modal) - 1);
  backdrop-filter: blur(2px);

  @media (min-width: 768px) {
    display: none;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// ============================================
// Logo Area
// ============================================
.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border-dark);
  background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
  flex-shrink: 0;

  .logo-text {
    font-size: 24px;
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin: 0;
    letter-spacing: 1px;
    display: block;
    white-space: nowrap;
  }

  .logo-text-short {
    font-size: 20px;
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin: 0;
    display: none;
    white-space: nowrap;
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

// ============================================
// Menu Styles
// ============================================
.sidebar-menu {
  border-right: none;
  padding: var(--spacing-sm) 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;

  // Remove default Element Plus menu styles
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    margin: 0 var(--spacing-sm);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    height: 48px;
    line-height: 48px;

    &:hover {
      background-color: var(--bg-hover);
      color: var(--text-primary);
    }

    &:focus {
      background-color: var(--bg-hover);
      outline: none;
    }
  }

  // Active menu item
  :deep(.el-menu-item.is-active) {
    background-color: var(--color-up-bg);
    color: var(--color-up);
    font-weight: var(--font-weight-medium);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 60%;
      background-color: var(--color-up);
      border-radius: 0 2px 2px 0;
    }
  }

  // Submenu
  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      margin: 0 var(--spacing-sm);
      border-radius: var(--radius-md);
      height: 48px;
      line-height: 48px;
    }

    .el-menu {
      background-color: var(--bg-card);

      .el-menu-item {
        padding-left: 48px !important;
        margin: 0 var(--spacing-sm);
        height: 44px;
        line-height: 44px;

        &:hover {
          background-color: var(--bg-hover);
        }

        &.is-active {
          background-color: var(--color-up-bg);
          color: var(--color-up);
        }
      }
    }
  }

  // Icon styling
  :deep(.el-icon) {
    font-size: 18px;
    width: 18px;
    height: 18px;
    margin-right: 8px;
  }

  // Collapsed mode icon adjustment
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

// ============================================
// Collapse Toggle (Desktop)
// ============================================
.collapse-toggle-container {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-dark);
  display: flex;
  justify-content: center;
  flex-shrink: 0;

  .collapse-toggle {
    font-size: 18px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-base);
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);

    &:hover {
      color: var(--color-primary);
      background-color: var(--bg-hover);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }

    &:active {
      transform: rotate(180deg) scale(0.95);
    }
  }
}

// ============================================
// Touch Optimizations (Mobile)
// ============================================
@media (hover: none) and (pointer: coarse) {
  .responsive-sidebar.is-mobile {
    .sidebar-menu {
      // Larger touch targets for mobile
      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        height: 52px;
        line-height: 52px;
        min-height: 52px;
      }
    }
  }
}

// ============================================
// Responsive Breakpoints
// ============================================
@media (max-width: 768px) {
  .responsive-sidebar {
    // Full height on mobile
    height: 100vh;
    height: 100dvh; // Dynamic viewport height for mobile browsers

    // Hide collapse toggle on mobile
    .collapse-toggle-container {
      display: none;
    }
  }

  .sidebar-logo {
    height: 56px;

    .logo-text {
      font-size: 20px;
    }

    .logo-text-short {
      font-size: 18px;
    }
  }
}

@media (max-width: 576px) {
  .sidebar-overlay {
    // More transparent overlay on small screens
    background-color: rgba(11, 15, 25, 0.7);
  }

  .responsive-sidebar.is-mobile {
    // Full width menu on very small screens
    &.is-open {
      width: 240px !important;
    }
  }
}

// ============================================
// Accessibility Improvements
// ============================================
// High contrast mode support
@media (prefers-contrast: high) {
  .responsive-sidebar {
    border-right: 2px solid var(--border-base);
  }

  .sidebar-menu {
    :deep(.el-menu-item.is-active) {
      &::before {
        width: 4px;
      }
    }
  }
}

// Reduced motion support
@media (prefers-reduced-motion: reduce) {
  .responsive-sidebar,
  .sidebar-overlay,
  .logo-fade-enter-active,
  .logo-fade-leave-active {
    transition: none;
  }
}

// Focus visible for keyboard navigation
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

// ============================================
// Print Styles
// ============================================
@media print {
  .responsive-sidebar,
  .sidebar-overlay {
    display: none;
  }
}
</style>
