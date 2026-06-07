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
          home-title="交易室"
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
import { ref, computed, watch, onMounted } from 'vue'
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
import { wsUrl } from '@/config/runtime-endpoints'

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
const sidebarCollapsed = ref(false) // Sidebar collapsed state (TODO owner=frontend-platform issue=techdebt-expired-markers ttl=2026-06-30: add persistence)
const unreadCount = ref(0)
const commandPaletteRef = ref<InstanceType<typeof CommandPalette>>()

// Toast Manager
const toast = useToastManager()

// Make menuItems reactive locally so their status can be updated
const menuItemsRef = ref<MenuItem[]>(props.menuItems)

// WebSocket Integration
const { connect, disconnect: _disconnect, message: wsMessage } = useWebSocket()

onMounted(() => {
  connect(wsUrl('/api/ws'))
})

// WebSocket message type
interface WsMessage {
  type: string;
  payload?: {
    path: string;
    status: string;
  };
}

// Watch for WebSocket messages and update menu item status
watch(wsMessage, (newMessage) => {
  const msg = newMessage as WsMessage | null
  if (msg && msg.type === 'menu_status_update' && msg.payload) {
    const { path, status } = msg.payload
    const itemIndex = menuItemsRef.value.findIndex(item => item.path === path)
    if (itemIndex > -1) {
      menuItemsRef.value[itemIndex].status = status as 'idle' | 'loading' | 'success' | 'error'
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
    const errMsg = error instanceof Error ? error.message : String(error)
    item.error = errMsg || 'API Error'  // Set error message (string, not boolean true)

    // 显示错误提示
    showErrorToast(
      `重新加载 ${item.label} 数据失败`,
      errMsg
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
@import "./styles/BaseLayout.scss";
</style>
