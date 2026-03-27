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
            v-for="(child, _idx) in menu.children"
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
        title: '交易室',
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
@use "./styles/ResponsiveSidebar.scss" as *;
</style>
