<template>
  <div class="artdeco-layout">
    <!-- Sidebar with Tree Menu -->
    <aside class="artdeco-sidebar">
      <TreeMenu />
    </aside>

    <!-- Main Content Area -->
    <main class="artdeco-main">
      <!-- Top Bar -->
      <header class="artdeco-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <!-- Global Search -->
          <button class="search-trigger" @click="openCommandPalette" aria-label="Search">
            <ArtDecoIcon name="Search" size="xs" />
            <kbd>Ctrl+K</kbd>
          </button>

          <!-- Notifications -->
          <button class="notification-btn" aria-label="Notifications">
            <ArtDecoIcon name="Bell" size="sm" />
            <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
          </button>

          <!-- User Menu -->
          <div class="user-menu">
            <button class="user-btn">
              <ArtDecoIcon name="User" size="sm" />
              <span class="user-name">Admin</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Breadcrumb Navigation -->
      <ArtDecoBreadcrumb
        class="artdeco-breadcrumb"
        home-title="仪表盘"
        home-path="/dashboard"
        :show-icon="true"
      />

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

    <!-- Command Palette -->
    <CommandPalette ref="commandPaletteRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TreeMenu from '@/components/menu/TreeMenu.vue'
import CommandPalette from '@/components/menu/CommandPalette.vue'
import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED } from './MenuConfig.enhanced'
import { getMenuApiEndpoints, getAllWebSocketChannels, findMenuItem } from './MenuConfig.enhanced'
import { useMenuService } from '@/services/menuService'
import type { MenuItem } from './MenuConfig.enhanced'

// Route
const route = useRoute()
const router = useRouter()

// State
const unreadCount = ref(0)
const commandPaletteRef = ref<any>(null)

// Menu Service
const { loading, error, getMenuData, subscribeToLiveUpdates, getLiveUpdateMenus } = useMenuService()

// Use ARTDECO_MENU_ENHANCED directly (6 main menus, 40+ submenus)
const enhancedMenus = computed((): MenuItem[] => ARTDECO_MENU_ENHANCED)

// Loading and error states
const isLoading = loading
const errorMessage = error

// Page title from route meta
const pageTitle = computed(() => {
  return route.meta.title as string || 'MyStocks'
})

// Methods
const handleMenuToggle = () => {
  // Handle menu toggle (for mobile/tablet)
  console.log('[ArtDecoLayout] Menu toggle requested')
}

const clearError = () => {
  errorMessage.value = null
}

// Open command palette
const openCommandPalette = () => {
  console.log('[ArtDecoLayout] Command palette requested')
  if (commandPaletteRef.value) {
    commandPaletteRef.value.open()
  }
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

// Sidebar
.artdeco-sidebar {
  width: 320px;
  flex-shrink: 0;
  background: var(--artdeco-bg-surface);
  border-right: 2px solid var(--artdeco-border-primary);
  overflow-y: auto;
}

// Main Content Area
.artdeco-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--artdeco-bg-global);
}

// Header
.artdeco-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  background: var(--artdeco-bg-elevated);
  border-bottom: 1px solid var(--artdeco-border-default);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
}

.page-title {
  font-size: var(--artdeco-text-xl);
  font-weight: var(--artdeco-font-semibold);
  color: var(--artdeco-fg-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  background: var(--artdeco-bg-base);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    background: var(--artdeco-bg-elevated);
    border-color: var(--artdeco-gold-primary);
  }

  kbd {
    padding: 2px 6px;
    background: var(--artdeco-bg-secondary);
    border: 1px solid var(--artdeco-border-default);
    border-radius: var(--artdeco-radius-sm);
    font-size: var(--artdeco-text-xs);
    font-family: var(--artdeco-font-mono);
    color: var(--artdeco-fg-primary);
  }
}

.notification-btn {
  position: relative;
  padding: var(--artdeco-spacing-2);
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--artdeco-fg-muted);

  &:hover {
    color: var(--artdeco-gold-hover);
  }

  .badge {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    background: var(--artdeco-up);
    border-radius: var(--artdeco-radius-full);
    font-size: var(--artdeco-text-xs);
    font-weight: var(--artdeco-font-semibold);
    line-height: 16px;
    text-align: center;
    color: var(--artdeco-fg-primary);
  }
}

.user-menu .user-btn {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  color: var(--artdeco-fg-primary);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    background: var(--artdeco-bg-hover);
    border-color: var(--artdeco-gold-primary);
  }
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
