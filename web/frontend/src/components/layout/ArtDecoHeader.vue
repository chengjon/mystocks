<template>
  <header class="artdeco-header">
    <div class="header-left">
      <button 
        class="menu-toggle-btn"
        @click="preferenceStore.toggleSidebar()"
        aria-label="Toggle Sidebar"
      >
        <ArtDecoIcon :name="preferenceStore.sidebarCollapsed ? 'Menu' : 'ChevronLeft'" size="sm" />
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>

    <div class="header-right">
      <!-- Global Search -->
      <button 
        class="search-trigger" 
        @click="emit('openCommandPalette')" 
        aria-label="Search"
      >
        <ArtDecoIcon name="Search" size="xs" />
        <kbd>Ctrl+K</kbd>
      </button>

      <!-- Notifications -->
      <button 
        class="notification-btn" 
        aria-label="Notifications"
        @click="emit('openNotifications')"
      >
        <ArtDecoIcon name="Bell" size="sm" />
        <span v-if="unreadCount && unreadCount > 0" class="badge">{{ unreadCount }}</span>
      </button>

      <!-- User Menu -->
      <div class="user-menu">
        <button 
          class="user-btn"
          aria-label="User Profile"
          @click="emit('openUserMenu')"
        >
          <ArtDecoIcon name="User" size="sm" />
          <span class="user-name">{{ userName }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePreferenceStore } from '@/stores/preferenceStore'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'

// Props & Emitters
const props = defineProps<{
  unreadCount?: number
  userName?: string
}>()

const emit = defineEmits([
  'openCommandPalette', 
  'openNotifications', 
  'openUserMenu'
])

// State
const route = useRoute()
const preferenceStore = usePreferenceStore()

const pageTitle = computed(() => {
  return (route.meta.title as string) || 'MyStocks'
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  background: var(--artdeco-bg-elevated);
  border-bottom: 1px solid var(--artdeco-border-default);
  flex-shrink: 0;
  height: 64px;
  
  // Sticky header support
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
}

.menu-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-2);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--artdeco-radius-md);
  color: var(--artdeco-fg-primary);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    background: var(--artdeco-bg-hover);
    border-color: var(--artdeco-border-default);
  }
}

.page-title {
  font-size: var(--artdeco-text-lg);
  font-weight: var(--artdeco-font-semibold);
  color: var(--artdeco-fg-primary);
  margin: 0;
  line-height: 1.2;
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
  min-width: 140px;

  &:hover {
    background: var(--artdeco-bg-elevated);
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-fg-primary);
  }

  kbd {
    margin-left: auto;
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
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--artdeco-spacing-2);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  color: var(--artdeco-fg-muted);
  transition: all var(--artdeco-transition-base);
  width: 36px;
  height: 36px;

  &:hover {
    color: var(--artdeco-gold-hover);
    background: var(--artdeco-bg-hover);
  }

  .badge {
    position: absolute;
    top: 4px;
    right: 4px;
    min-width: 8px;
    height: 8px;
    padding: 0;
    background: var(--artdeco-up);
    border-radius: var(--artdeco-radius-full);
    border: 2px solid var(--artdeco-bg-elevated); // Border creates spacing from icon
  }
}

.user-menu .user-btn {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-full); // Pill shape
  color: var(--artdeco-fg-primary);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);
  height: 36px;

  &:hover {
    background: var(--artdeco-bg-hover);
    border-color: var(--artdeco-gold-primary);
  }
  
  .user-name {
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-medium);
  }
}

// Mobile Responsiveness
@media (max-width: 768px) {
  .page-title {
    display: none; // Hide title on mobile if needed or shrink
  }
  
  .search-trigger {
    min-width: auto;
    padding: var(--artdeco-spacing-2);
    
    kbd, span {
      display: none;
    }
  }
  
  .user-name {
    display: none;
  }
}
</style>
