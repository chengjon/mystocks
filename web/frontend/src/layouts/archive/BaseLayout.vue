<template>
  <div class="base-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- ArtDeco Skip Link (WCAG AA 可访问性) -->
    <ArtDecoSkipLink />

    <!-- 顶部栏 -->
    <header class="layout-header">
      <div class="header-left">
        <button class="sidebar-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
          <span class="icon-menu">☰</span>
        </button>
        <!-- ArtDeco Breadcrumb (自动从路由meta生成) -->
        <ArtDecoBreadcrumb
          home-title="仪表盘"
          home-path="/dashboard"
          :show-icon="true"
        />
      </div>

      <div class="header-center">
        <h1 class="page-title">{{ pageTitle }}</h1>
      </div>

      <div class="header-right">
        <!-- 全局搜索 (占位，后续Command Palette) -->
        <button class="search-trigger" @click="openCommandPalette" aria-label="Search">
          <span class="icon-search">🔍</span>
          <kbd>Ctrl+K</kbd>
        </button>

        <!-- 通知图标 -->
        <button class="notification-btn" aria-label="Notifications">
          <span class="icon-bell">🔔</span>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
        </button>

        <!-- 用户菜单 -->
        <div class="user-menu">
          <button class="user-btn">
            <span class="user-avatar">👤</span>
            <span class="user-name">Admin</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="layout-body">
      <!-- 侧边栏 -->
      <aside class="layout-sidebar">
        <nav class="sidebar-nav">
                    <ul class="nav-list">
                      <li
                        v-for="(item, _idx) in menuItemsRef"
                        :key="item.path"
                        class="nav-item"
                        :class="{
                          active: isActive(item.path),
                          'nav-item--live': item.liveUpdate,
                          'nav-item--featured': item.featured,
                          [`priority-${item.priority}`]: item.priority
                        }"
                      >
                                      <router-link :to="item.path" class="nav-link" @error="handleNavigationError($event, item)">
                                        <ArtDecoIcon :name="item.icon" size="sm" :animated="item.liveUpdate" />
                                        <div class="nav-content">
                                          <span class="nav-label">{{ item.label }}</span>
                                          <span v-if="item.description" class="nav-description">{{ item.description }}</span>
                                        </div>
                                        <div class="nav-meta">
                                          <span v-if="item.lastUpdate" class="nav-timestamp">
                                            {{ formatTime(item.lastUpdate) }}
                                          </span>
                                          <span v-if="item.count" class="nav-count">
                                            {{ item.count }}
                                          </span>
                                        </div>
                                        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
                                        <!-- Error status indicator -->
                                        <ArtDecoBadge
                                          v-if="item.error"
                                          variant="danger"
                                          text="API Error"
                                          @click.stop="retryApiCall(item)"
                                        />
                                        <!-- Real-time status indicator -->
                                        <span v-if="item.liveUpdate"
                                              class="live-indicator"
                                              :class="`status-${item.status || 'idle'}`">
                                        </span>
                                      </router-link>                      </li>
                    </ul>        </nav>
      </aside>

      <!-- 内容区域 -->
      <main id="main-content" class="layout-main" tabindex="-1">
        <div class="content-wrapper">
          <slot></slot>
        </div>
      </main>
    </div>

    <!-- Command Palette -->
    <CommandPalette
      ref="commandPaletteRef"
      :items="commandItems"
      @open="onCommandPaletteOpen"
      @close="onCommandPaletteClose"
      @navigate="onCommandPaletteNavigate"
    />

    <!-- Toast Notifications -->
    <ArtDecoToast
      :toasts="toast.toasts"
      position="top-right"
      @close="toast.remove"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, _onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
import ArtDecoSkipLink from '@/components/artdeco/base/ArtDecoSkipLink.vue'
import CommandPalette, { type CommandItem } from '@/components/shared/command-palette/CommandPalette.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
import ArtDecoToast from '@/components/artdeco/core/ArtDecoToast.vue'
import { MenuItem } from '@/layouts/archive/MenuConfig.ts'
import { useWebSocket } from '@/composables/useWebSocket'
import { useToastManager } from '@/composables/useToastManager'
import { fetchMenuItemData, clearMenuDataCache } from '@/services/menuDataFetcher'

// Props
interface Props {
  pageTitle?: string
  menuItems: MenuItem[]
}

const props = withDefaults(defineProps<Props>(), {
  pageTitle: 'MyStocks'
})

// Route
const route = useRoute()

// State
const sidebarCollapsed = ref(false) // Sidebar collapsed state (TODO: add persistence)
const unreadCount = ref(0)
const commandPaletteRef = ref<InstanceType<typeof CommandPalette>>()

// Toast Manager
const toast = useToastManager()

// Make menuItems reactive locally so their status can be updated
const menuItemsRef = ref<MenuItem[]>(props.menuItems)

// WebSocket Integration
const { connect, _disconnect, message: wsMessage } = useWebSocket()

onMounted(() => {
  // Connect to WebSocket server, replace with your actual WebSocket URL
  connect('ws://localhost:8000/api/ws')
})

// Watch for WebSocket messages and update menu item status
watch(wsMessage, (newMessage) => {
  if (newMessage && newMessage.type === 'menu_status_update' && newMessage.payload) {
    const { path, status } = newMessage.payload
    const itemIndex = menuItemsRef.value.findIndex(item => item.path === path)
    if (itemIndex > -1) {
      menuItemsRef.value[itemIndex].status = status // Assuming MenuItem has a status property
      // Trigger reactivity
      menuItemsRef.value = [...menuItemsRef.value]
    }
  }
})

// Computed
const commandItems = computed((): CommandItem[] => {
  return menuItemsRef.value.map(item => ({
    path: item.path,
    label: item.label,
    icon: item.icon,
    category: props.pageTitle,
    keywords: [item.label, props.pageTitle]
  }))
})

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const openCommandPalette = () => {
  commandPaletteRef.value?.open()
}

const onCommandPaletteOpen = () => {
  console.log('Command Palette opened')
}

const onCommandPaletteClose = () => {
  console.log('Command Palette closed')
}

const onCommandPaletteNavigate = (path: string) => {
  console.log('Navigated to:', path)
}

// ============================================
// Toast Notification Functions
// ============================================

/**
 * 显示错误Toast通知
 */
const showErrorToast = (message: string, title?: string) => {
  toast.showError(message, title)
}

/**
 * 显示成功Toast通知
 */
const showSuccessToast = (message: string, title?: string) => {
  toast.showSuccess(message, title)
}

// ============================================
// Menu Data Fetching Functions
// ============================================

/**
 * 获取菜单项数据
 * 使用MenuConfig中配置的API端点
 */
const fetchItemData = async (item: MenuItem) => {
  // 验证MenuItem是否配置了API端点
  if (!item.apiEndpoint) {
    console.warn(`[BaseLayout] MenuItem "${item.label}" has no API endpoint configured`)
    return null
  }

  console.log(`[BaseLayout] Fetching data for: ${item.label} from ${item.apiEndpoint}`)

  try {
    // 使用fetchMenuItemData服务获取数据
    const result = await fetchMenuItemData(item, {
      timeout: 10000,
      retries: 2,
      cache: true
    })

    if (result.success) {
      console.log(`[BaseLayout] Successfully fetched data for: ${item.label}`)

      // 更新MenuItem的lastUpdate时间戳
      if (result.cached === false) {
        item.lastUpdate = Math.floor(Date.now() / 1000)
      }

      // 返回数据
      return result.data
    } else {
      throw new Error(result.error || '获取数据失败')
    }
  } catch (error: unknown) {
    console.error(`[BaseLayout] Failed to fetch data for ${item.label}:`, error)
    throw error
  }
}

const handleNavigationError = (event: Event, item: MenuItem) => {
  console.error('Navigation failed for item:', item.label, event)
  item.error = 'Navigation failed'; // Mark item as error (string, not boolean)
  showErrorToast(`无法加载 ${item.label} 页面. 请尝试重试或检查网络连接.`)
}

const retryApiCall = async (item: MenuItem) => {
  console.log('Retrying API call for:', item.label);

  try {
    // 清除该菜单项的缓存
    clearMenuDataCache(item.apiEndpoint)

    // 重新获取数据
    await fetchItemData(item)

    // 清除错误状态
    item.error = null  // Clear error (null, not boolean false)

    // 显示成功提示
    showSuccessToast(`${item.label} 数据已成功重新加载`)
  } catch (error: unknown) {
    // 保持错误状态
    item.error = error.message || 'API Error'  // Set error message (string, not boolean true)

    // 显示错误提示
    showErrorToast(
      `重新加载 ${item.label} 数据失败`,
      error.message || String(error)
    )
  }
}

// Helper for time formatting
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000) // Convert to milliseconds
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// Watch route changes to update document title
watch(() => route.path, () => {
  document.title = `${props.pageTitle} - MyStocks`
}, { immediate: true })
</script>

<style scoped lang="scss">
@import '@/styles/theme-tokens';
@import '@/styles/artdeco-menu';

.base-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--artdeco-bg-global); /* Use ArtDeco global background */
  color: var(--artdeco-fg-primary); /* Use ArtDeco primary foreground color */
}

// ========== 顶部栏 ==========
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height, 56px);
  padding: 0 var(--artdeco-spacing-md); /* Use ArtDeco spacing */
  background: var(--artdeco-bg-elevated); /* Use ArtDeco elevated background */
  border-bottom: 1px solid var(--artdeco-border-default); /* Use ArtDeco border */
  flex-shrink: 0;
  z-index: var(--artdeco-z-header, 100); /* Use ArtDeco z-index */

  @include artdeco-geometric-corners(var(--artdeco-gold-dim), 12px, 1px); /* Add geometric corners */
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-md); /* Use ArtDeco spacing */
}

.header-center {
  flex: 1;
  text-align: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-md); /* Use ArtDeco spacing */
}

.sidebar-toggle {
  @include button-secondary;

  padding: var(--artdeco-spacing-xs); /* Use ArtDeco spacing */
  background: transparent;
  border: none;
  cursor: pointer;

  &:hover {
    background: var(--artdeco-bg-hover); /* Use ArtDeco hover background */
  }
}

.page-title {
  font-size: var(--artdeco-text-xl); /* Use ArtDeco text size */
  font-weight: var(--artdeco-font-semibold); /* Use ArtDeco font weight */
  color: var(--artdeco-fg-primary); /* Use ArtDeco primary foreground */
  margin: 0;

  @include artdeco-gradient-text; /* Apply gradient text for page title */
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-xs); /* Use ArtDeco spacing */
  padding: var(--artdeco-spacing-xs) var(--artdeco-spacing-sm); /* Use ArtDeco spacing */
  background: var(--artdeco-bg-base); /* Use ArtDeco base background */
  border: 1px solid var(--artdeco-border-default); /* Use ArtDeco border */
  border-radius: var(--artdeco-radius-sm); /* Use ArtDeco border-radius */
  color: var(--artdeco-fg-muted); /* Use ArtDeco muted foreground */
  cursor: pointer;
  transition: all var(--artdeco-transition-base); /* Use ArtDeco transition */

  &:hover {
    background: var(--artdeco-bg-elevated); /* Use ArtDeco elevated background */
    border-color: var(--artdeco-gold-primary); /* Use ArtDeco gold */
  }

  kbd {
    padding: 2px 6px;
    background: var(--artdeco-bg-secondary); /* Use ArtDeco secondary background */
    border: 1px solid var(--artdeco-border-default); /* Use ArtDeco border */
    border-radius: var(--artdeco-radius-sm); /* Use ArtDeco border-radius */
    font-size: var(--artdeco-text-xs); /* Use ArtDeco text size */
    font-family: var(--artdeco-font-mono); /* Use ArtDeco mono font */
    color: var(--artdeco-fg-primary);
  }
}

.notification-btn {
  position: relative;
  padding: var(--artdeco-spacing-xs); /* Use ArtDeco spacing */
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
    background: var(--artdeco-up); /* Use ArtDeco up color */
    border-radius: var(--artdeco-radius-full); /* Use ArtDeco full radius */
    font-size: var(--artdeco-text-xs); /* Use ArtDeco text size */
    font-weight: var(--artdeco-font-semibold); /* Use ArtDeco font weight */
    line-height: 16px;
    text-align: center;
    color: var(--artdeco-fg-primary);
  }
}

.user-menu .user-btn {
  color: var(--artdeco-fg-primary);
  &:hover {
    color: var(--artdeco-gold-hover);
  }
}

// ========== 主体 ==========
.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

// ========== 侧边栏 ==========
.layout-sidebar {
  width: var(--sidebar-width, 240px);
  background: var(--artdeco-bg-base); /* Use ArtDeco base background */
  border-right: 2px solid var(--artdeco-gold-primary); /* Use ArtDeco gold border */
  overflow-y: auto;
  transition: width var(--artdeco-transition-base) ease; /* Use ArtDeco transition */
  flex-shrink: 0;

  @include artdeco-corner-brackets; /* Add corner brackets */

  .sidebar-collapsed & {
    width: var(--sidebar-collapsed-width, 64px);

    .nav-label,
    .nav-badge {
      display: none;
    }

    .nav-link {
      justify-content: center;
      padding: var(--artdeco-spacing-md); /* Use ArtDeco spacing */
    }
  }
}

.sidebar-nav {
  padding: var(--artdeco-spacing-sm) 0; /* Use ArtDeco spacing */
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-md); /* Use ArtDeco spacing */
  padding: var(--artdeco-spacing-sm) var(--artdeco-spacing-md); /* Use ArtDeco spacing */
  color: var(--artdeco-fg-muted); /* Use ArtDeco muted foreground */
  text-decoration: none;
  border-radius: var(--artdeco-radius-none); /* ArtDeco minimal radius */
  transition: all var(--artdeco-transition-fast); /* Use ArtDeco fast transition */

  @include artdeco-hover-lift-glow; /* Apply hover lift glow mixin */

  &:hover {
    background: var(--artdeco-bg-elevated); /* Use ArtDeco elevated background */
    color: var(--artdeco-gold-hover); /* Use ArtDeco gold hover */
  }

  &.active,
  &.router-link-active {
    background: linear-gradient(90deg, var(--artdeco-gold-dim) 0%, transparent 100%); /* ArtDeco gradient */
    color: var(--artdeco-gold-primary); /* Use ArtDeco gold primary */
    box-shadow: var(--artdeco-glow-subtle); /* Apply subtle glow */
    border-left: 4px solid var(--artdeco-gold-primary);
  }
}

.nav-icon {
  font-size: 20px;
  color: var(--artdeco-gold-primary); /* ArtDeco icon color */
}

.nav-label {
  flex: 1;
  font-size: var(--artdeco-text-sm); /* Use ArtDeco text size */
  font-family: var(--artdeco-font-body); /* Use ArtDeco body font */
}

.nav-badge {
  padding: 2px 8px;
  background: var(--artdeco-up); /* Use ArtDeco up color */
  border-radius: var(--artdeco-radius-full); /* Use ArtDeco full radius */
  font-size: var(--artdeco-text-xs); /* Use ArtDeco text size */
  font-weight: var(--artdeco-font-semibold); /* Use ArtDeco font weight */
  color: var(--artdeco-fg-primary);
}

// ========== 主内容 ==========
.layout-main {
  flex: 1;
  overflow-y: auto;
  background: var(--artdeco-bg-global); /* Use ArtDeco global background */
}

.content-wrapper {
  padding: var(--artdeco-spacing-lg); /* Use ArtDeco spacing */
  min-height: calc(100vh - var(--header-height) - var(--artdeco-spacing-xl)); /* Use ArtDeco spacing */

  @include artdeco-geometric-corners(var(--artdeco-gold-muted), 16px, 1px); /* Add subtle geometric corners */

  background: var(--artdeco-bg-card);
  border-radius: var(--artdeco-radius-sm);
  box-shadow: var(--artdeco-shadow-md);
}

// ========== 滚动条样式 ==========
.layout-sidebar,
.layout-main {
  /* @include scrollbar; */ // Keeping original for now, will review later
}

// ========== 桌面端优化 (1280px+) ==========
@media (width >= 1280px) {
  .layout-sidebar {
    width: 280px;

    &.sidebar-collapsed {
      width: var(--sidebar-collapsed-width, 64px);
    }
  }

  .content-wrapper {
    padding: var(--artdeco-spacing-xl); /* Use ArtDeco spacing */
  }
}

// ========== 大屏幕优化 (1920px+) ==========
@media (width >= 1920px) {
  .layout-sidebar {
    width: 320px;

    &.sidebar-collapsed {
      width: 80px;
    }
  }

  .page-title {
    font-size: var(--artdeco-text-2xl); /* Use ArtDeco text size */
  }

  .content-wrapper {
    max-width: 1800px;
    margin: 0 auto;
  }
}

// ArtDeco Mixins from artdeco-tokens.scss (if not globally available)
// Assuming mixins are available via @import '../styles/artdeco-tokens.scss';
// If not, they would need to be re-declared or imported differently.
// For now, I'm assuming @import '../styles/artdeco-tokens.scss'; makes them available.
@import '@/styles/artdeco-tokens';
</style>
