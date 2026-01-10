<template>
  <div class="base-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 顶部栏 -->
    <header class="layout-header">
      <div class="header-left">
        <button class="sidebar-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
          <span class="icon-menu">☰</span>
        </button>
        <BreadcrumbNav :items="breadcrumbItems" />
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
              v-for="item in menuItems"
              :key="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
            >
              <router-link :to="item.path" class="nav-link">
                <span class="nav-icon">{{ item.icon }}</span>
                <span class="nav-label">{{ item.label }}</span>
                <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- 内容区域 -->
      <main class="layout-main">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import BreadcrumbNav, { type BreadcrumbItem } from '@/components/layout/BreadcrumbNav.vue'
import CommandPalette, { type CommandItem } from '@/components/shared/command-palette/CommandPalette.vue'

interface MenuItem {
  path: string
  label: string
  icon: string
  badge?: string | number
}

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
const sidebarCollapsed = ref(false)
const unreadCount = ref(0)
const commandPaletteRef = ref<InstanceType<typeof CommandPalette>>()

// Computed
const commandItems = computed((): CommandItem[] => {
  return props.menuItems.map(item => ({
    path: item.path,
    label: item.label,
    icon: item.icon,
    category: props.pageTitle,
    keywords: [item.label, props.pageTitle]
  }))
})

const breadcrumbItems = computed((): BreadcrumbItem[] => {
  const items: BreadcrumbItem[] = [
    { label: 'Home', path: '/' }
  ]

  // 根据当前路由生成面包屑
  const pathSegments = route.path.split('/').filter(Boolean)
  let currentPath = ''

  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === pathSegments.length - 1
    items.push({
      label: segment.charAt(0).toUpperCase() + segment.slice(1),
      path: isLast ? undefined : currentPath
    })
  })

  return items
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

// Watch route changes to update document title
watch(() => route.path, () => {
  document.title = `${props.pageTitle} - MyStocks`
}, { immediate: true })
</script>

<style scoped lang="scss">
@import '@/styles/theme-tokens.scss';

.base-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

// ========== 顶部栏 ==========
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height, 56px);
  padding: 0 var(--spacing-md);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  z-index: var(--z-index-header, 100);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-center {
  flex: 1;
  text-align: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.sidebar-toggle {
  @include button-secondary;
  padding: var(--spacing-xs);
  background: transparent;
  border: none;
  cursor: pointer;

  &:hover {
    background: var(--bg-hover);
  }
}

.page-title {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-hover);
    border-color: var(--accent-color);
  }

  kbd {
    padding: 2px 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 12px;
    font-family: var(--font-family-mono);
  }
}

.notification-btn {
  position: relative;
  padding: var(--spacing-xs);
  background: transparent;
  border: none;
  cursor: pointer;

  .badge {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    background: var(--color-stock-up);
    border-radius: 8px;
    font-size: 10px;
    font-weight: 600;
    line-height: 16px;
    text-align: center;
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
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  transition: width 0.3s ease;
  flex-shrink: 0;

  .sidebar-collapsed & {
    width: var(--sidebar-collapsed-width, 64px);

    .nav-label,
    .nav-badge {
      display: none;
    }

    .nav-link {
      justify-content: center;
      padding: var(--spacing-md);
    }
  }
}

.sidebar-nav {
  padding: var(--spacing-sm) 0;
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
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--border-radius-sm);
  transition: all 0.2s;

  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  &.active,
  &.router-link-active {
    background: var(--accent-color);
    color: white;
  }
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  flex: 1;
  font-size: 14px;
}

.nav-badge {
  padding: 2px 8px;
  background: var(--color-stock-up);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

// ========== 主内容 ==========
.layout-main {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-primary);
}

.content-wrapper {
  padding: var(--spacing-lg);
  min-height: calc(100vh - var(--header-height) - var(--spacing-xl));
}

// ========== 滚动条样式 ==========
.layout-sidebar,
.layout-main {
  @include scrollbar;
}

// ========== 桌面端优化 (1280px+) ==========
@media (min-width: 1280px) {
  .layout-sidebar {
    width: 280px;

    &.sidebar-collapsed {
      width: var(--sidebar-collapsed-width, 64px);
    }
  }

  .content-wrapper {
    padding: var(--spacing-xl);
  }
}

// ========== 大屏幕优化 (1920px+) ==========
@media (min-width: 1920px) {
  .layout-sidebar {
    width: 320px;

    &.sidebar-collapsed {
      width: 80px;
    }
  }

  .page-title {
    font-size: 20px;
  }

  .content-wrapper {
    max-width: 1800px;
    margin: 0 auto;
  }
}
</style>
