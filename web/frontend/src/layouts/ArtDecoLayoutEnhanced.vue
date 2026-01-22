<template>
  <div class="artdeco-layout">
    <!-- Collapsible Sidebar -->
    <ArtDecoCollapsibleSidebar :menus="enhancedMenus" />

    <!-- Main Content Area -->
    <main class="artdeco-main">
      <!-- Top Bar -->
      <ArtDecoTopBar
        :menu-items="enhancedMenus"
        @menu-toggle="handleMenuToggle"
      />

      <!-- Breadcrumb Navigation -->
      <ArtDecoBreadcrumb :breadcrumbs="breadcrumbItems" class="artdeco-breadcrumb" />

      <!-- Content Container -->
      <div class="artdeco-content">
        <!-- Loading Overlay -->
        <div v-if="isLoading" class="loading-state">
          <p>Loading ArtDeco Layout...</p>
        </div>

        <!-- Error Display -->
        <div v-else-if="errorMessage" class="error-state">
          <p>Error: {{ errorMessage }}</p>
        </div>

        <!-- Router View -->
        <router-view v-else />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ArtDecoCollapsibleSidebar from '@/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue'
import ArtDecoTopBar from '@/components/artdeco/trading/ArtDecoTopBar.vue'
import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
import ArtDecoLoadingOverlay from '@/components/artdeco/core/ArtDecoLoadingOverlay.vue'
import ArtDecoAlert from '@/components/artdeco/base/ArtDecoAlert.vue'
import { ARTDECO_MENU_ENHANCED } from './MenuConfig.enhanced'
import { getMenuApiEndpoints, getAllWebSocketChannels, getLiveUpdateMenus } from './MenuConfig.enhanced'
import { useMenuService } from '@/services/menuService'
import type { MenuItem } from './MenuConfig.enhanced'

// Route
const route = useRoute()
const router = useRouter()

// Menu Service
const { loading, error, getMenuData, subscribeToLiveUpdates, getLiveUpdateMenus } =
  useMenuService()

// Import the correct menu for current routes
import { ARTDECO_MENU_ITEMS } from './MenuConfig'

// Computed
const enhancedMenus = computed((): MenuItem[] => {
  // Convert flat ARTDECO_MENU_ITEMS to hierarchical structure
  const groupedMenus: MenuItem[] = [
    {
      path: '/dashboard-group',
      label: '仪表盘',
      icon: '📊',
      description: '数据概览和监控',
      children: [
        {
          path: '/dashboard',
          label: '数据概览',
          icon: '📊',
          description: '市场汇总信息'
        },
        {
          path: '/stocks',
          label: '股票管理',
          icon: '📋',
          description: '自选股、关注列表、策略选股'
        }
      ]
    },
    {
      path: '/analysis-group',
      label: '投资分析',
      icon: '🔍',
      description: '技术分析、基本面分析',
      children: [
        {
          path: '/analysis',
          label: '数据分析',
          icon: '📊',
          description: '技术分析、基本面分析、指标分析'
        },
        {
          path: '/analysis/industry-concept',
          label: '行业概念分析',
          icon: '🏢',
          description: '行业板块分析'
        }
      ]
    }
  ]
  return groupedMenus
})
const isLoading = loading  // Already a Ref<boolean>
const errorMessage = error  // Already a Ref<string | null>

// Breadcrumb items
const breadcrumbItems = computed(() => {
  const items: Array<{ title: string; path?: string; icon?: string }> = [
    { title: 'Home', path: '/dashboard' },
  ]

  // Find current menu item
  const currentPath = route.path
  for (const menu of enhancedMenus.value) {
    if (menu.path === currentPath) {
      items.push({ title: menu.label })
      break
    }

    if (menu.children) {
      const child = menu.children.find(c => c.path === currentPath)
      if (child) {
        items.push(
          { title: menu.label, path: menu.path },
          { title: child.label }
        )
        break
      }
    }
  }

  return items
})

// Methods
const handleMenuToggle = () => {
  // Handle menu toggle (for mobile/tablet)
  console.log('[ArtDecoLayout] Menu toggle requested')
}

const clearError = () => {
  error.value = null
}

// Load menu data for current route
const loadCurrentRouteData = async () => {
  const currentPath = route.path

  // Find matching menu item
  for (const menu of enhancedMenus.value) {
    if (menu.path === currentPath && menu.apiEndpoint) {
      try {
        await getMenuData(menu)
      } catch (err) {
        console.error(`[ArtDecoLayout] Failed to load menu data:`, err)
      }
      break
    }

    if (menu.children) {
      const child = menu.children.find(c => c.path === currentPath)
      if (child && child.apiEndpoint) {
        try {
          await getMenuData(child)
        } catch (err) {
          console.error(`[ArtDecoLayout] Failed to load menu data:`, err)
        }
        break
      }
    }
  }
}

// Setup live updates
const setupLiveUpdates = () => {
  const liveMenus = getLiveUpdateMenus()

  liveMenus.forEach(menu => {
    const unsubscribe = subscribeToLiveUpdates(menu, (data) => {
      console.log(`[ArtDecoLayout] Live update for ${menu.path}:`, data)
      // Handle live data update
      // You can emit an event or update a store here
    })

    // Store unsubscribe function for cleanup
    ;(window as any).__liveUpdateUnsubscribes =
      (window as any).__liveUpdateUnsubscribes || []
    ;(window as any).__liveUpdateUnsubscribes.push(unsubscribe)
  })
}

// Cleanup live updates
const cleanupLiveUpdates = () => {
  const unsubscribes = (window as any).__liveUpdateUnsubscribes || []
  unsubscribes.forEach((fn: () => void) => fn())
  ;(window as any).__liveUpdateUnsubscribes = []
}

// Lifecycle
onMounted(() => {
  // Load initial data
  loadCurrentRouteData()

  // Setup live updates
  setupLiveUpdates()
})

onUnmounted(() => {
  // Cleanup live updates
  cleanupLiveUpdates()
})

// Watch route changes
watch(
  () => route.path,
  () => {
    loadCurrentRouteData()
  }
)
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   ART DECO LAYOUT
// ============================================
.artdeco-layout {
  display: flex;
  min-height: 100vh;
  background: var(--artdeco-bg-global);
}

// Sidebar (fixed positioning handled by component)
.artdeco-collapsible-sidebar {
  flex-shrink: 0;
}

// Main Content Area
.artdeco-main {
  flex: 1;
  margin-left: 320px; // Match sidebar width
  min-height: 100vh;
  background: var(--artdeco-bg-global);
  display: flex;
  flex-direction: column;
}

// Breadcrumb
.artdeco-breadcrumb {
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
  background: var(--artdeco-bg-header);
}

// Content Container
.artdeco-content {
  flex: 1;
  padding: var(--artdeco-spacing-6);
  max-width: none; // Allow full width for content
  position: relative;
}

// ============================================
//   DESIGN NOTE - 设计说明
//   本项目仅支持桌面端，不包含移动端响应式代码
// ============================================
</style>
