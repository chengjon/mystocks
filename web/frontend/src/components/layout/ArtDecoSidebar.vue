<template>
  <aside 
    class="artdeco-sidebar" 
    :class="{ collapsed: preferenceStore.sidebarCollapsed }"
    aria-label="Sidebar Menu"
  >
    <!-- Brand / Logo -->
    <div class="sidebar-header">
      <router-link to="/" class="brand-link">
        <ArtDecoIcon name="Logo" size="md" class="brand-logo" />
        <span class="brand-name" v-if="!preferenceStore.sidebarCollapsed">MyStocks</span>
      </router-link>
      
      <!-- Collapse Button (Desktop) -->
      <button 
        class="collapse-btn" 
        @click="preferenceStore.toggleSidebar()"
        aria-label="Toggle Sidebar"
      >
        <ArtDecoIcon :name="preferenceStore.sidebarCollapsed ? 'ChevronRight' : 'ChevronLeft'" size="sm" />
      </button>
    </div>

    <!-- Scrollable Menu Area -->
    <div class="sidebar-content">
      <TreeMenu />
    </div>

    <!-- Sidebar Footer (Optional) -->
    <div class="sidebar-footer" v-if="!preferenceStore.sidebarCollapsed">
      <div class="footer-links">
        <a href="#" class="link">Help</a>
        <span class="divider">•</span>
        <a href="#" class="link">Privacy</a>
        <span class="divider">•</span>
        <a href="#" class="link">Terms</a>
      </div>
      <div class="footer-version">v2.1.0</div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { usePreferenceStore } from '@/stores/preferenceStore'
import TreeMenu from '@/components/menu/TreeMenu.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'

const preferenceStore = usePreferenceStore()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-sidebar {
  display: flex;
  flex-direction: column;
  width: 280px; // Standard width
  height: 100vh;
  background: var(--artdeco-bg-surface);
  border-right: 1px solid var(--artdeco-border-default);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: sticky;
  top: 0;
  z-index: 50;

  &.collapsed {
    width: 64px; // Collapsed width

    .brand-name, 
    .sidebar-footer,
    .collapse-btn {
      // Hide elements when collapsed
      // Note: TreeMenu needs to handle collapsed state internally or be hidden
      // For now, we rely on CSS hiding
      opacity: 0;
      pointer-events: none;
      display: none; // Force hide
    }
    
    .sidebar-header {
      justify-content: center;
      padding: var(--artdeco-spacing-4) 0;
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  height: 64px; // Match header height
  border-bottom: 1px solid var(--artdeco-border-default);
  flex-shrink: 0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  text-decoration: none;
  color: var(--artdeco-gold-primary);
  font-weight: var(--artdeco-font-bold);
  font-size: var(--artdeco-text-lg);
  
  &:hover {
    color: var(--artdeco-gold-hover);
  }
}

.brand-logo {
  color: var(--artdeco-gold-primary);
}

.collapse-btn {
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  padding: var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-sm);
  transition: all var(--artdeco-transition-base);

  &:hover {
    background: var(--artdeco-bg-hover);
    color: var(--artdeco-fg-primary);
  }
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  
  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--artdeco-bg-secondary);
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
}

.sidebar-footer {
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  border-top: 1px solid var(--artdeco-border-default);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-align: center;
  flex-shrink: 0;
  
  .footer-links {
    margin-bottom: var(--artdeco-spacing-2);
    display: flex;
    justify-content: center;
    gap: var(--artdeco-spacing-2);
    
    .link {
      color: var(--artdeco-fg-muted);
      text-decoration: none;
      &:hover {
        text-decoration: underline;
        color: var(--artdeco-fg-primary);
      }
    }
  }
  
  .footer-version {
    opacity: 0.6;
    font-family: var(--artdeco-font-mono);
  }
}
</style>
