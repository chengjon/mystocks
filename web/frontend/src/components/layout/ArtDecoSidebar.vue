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
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-sidebar {
  display: flex;
  flex-direction: column;
  width: calc(var(--artdeco-sidebar-width) + var(--artdeco-spacing-5));
  height: 100vh;
  background: var(--artdeco-bg-card);
  border-right: 1px solid var(--artdeco-border-default);
  transition: width var(--artdeco-transition-base) var(--artdeco-ease-out);
  overflow: hidden;
  position: sticky;
  top: 0;
  z-index: 50;

  &.collapsed {
    width: var(--artdeco-sidebar-collapsed-width);

    .brand-name, 
    .sidebar-footer,
    .collapse-btn {
      // Hide elements when collapsed
      // Note: TreeMenu needs to handle collapsed state internally or be hidden
      // For now, we rely on CSS hiding
      opacity: 0%;
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
  height: var(--artdeco-spacing-16);
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
    color: var(--artdeco-gold-light);
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
  overflow: hidden auto;
  
  // Custom scrollbar
  &::-webkit-scrollbar {
    width: var(--artdeco-spacing-1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--artdeco-bg-base);
    border-radius: var(--artdeco-radius-sm);
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
