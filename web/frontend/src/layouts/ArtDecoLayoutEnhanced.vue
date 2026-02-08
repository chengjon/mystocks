<template>
  <div class="artdeco-layout">
    <!-- Sidebar -->
    <ArtDecoSidebar />

    <!-- Main Content Area -->
    <main class="artdeco-main" :class="{ 'sidebar-collapsed': preferenceStore.sidebarCollapsed }">
      <!-- Top Bar -->
      <ArtDecoHeader 
        :unread-count="unreadCount"
        :user-name="userName"
        @open-command-palette="openCommandPalette"
        @open-notifications="toggleNotifications"
        @open-user-menu="toggleUserMenu"
      />

      <!-- Breadcrumb Navigation -->
      <div class="artdeco-breadcrumb-container">
        <ArtDecoBreadcrumb
          home-title="仪表盘"
          home-path="/dashboard"
          :show-icon="true"
        />
      </div>

      <!-- Content Container -->
      <div class="artdeco-content">
        
        <!-- Live Data Connection Status (Dev Only) -->
        <div v-if="devMode && !isLiveDataConnected" class="connection-status">
           <ArtDecoIcon name="WifiOff" size="xs" /> 
           <span>Offline Mode</span>
        </div>

        <!-- Router View with Transition -->
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Global Command Palette -->
    <CommandPalette ref="commandPaletteRef" />
    
    <!-- Performance Monitor -->
    <PerformanceMonitor />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMenuStore } from '@/stores/menuStore'
import { usePreferenceStore } from '@/stores/preferenceStore'
import { useLiveDataManager } from '@/composables/useLiveDataManager'
import ArtDecoSidebar from '@/components/layout/ArtDecoSidebar.vue'
import ArtDecoHeader from '@/components/layout/ArtDecoHeader.vue'
import CommandPalette from '@/components/menu/CommandPalette.vue'
import PerformanceMonitor from '@/components/common/PerformanceMonitor.vue'
import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import { ARTDECO_MENU_ENHANCED } from './MenuConfig.enhanced'

// Store & Route
const route = useRoute()
const menuStore = useMenuStore()
const preferenceStore = usePreferenceStore()

// Layout State
const unreadCount = ref(3) // Mock data
const userName = ref('Admin User')
const commandPaletteRef = ref<any>(null)
const devMode = import.meta.env.DEV

// Live Data Management - Simplified for layout, detailed logic in specific views
const { isConnected: isLiveDataConnected } = useLiveDataManager(ARTDECO_MENU_ENHANCED)

// Methods
const openCommandPalette = () => {
  commandPaletteRef.value?.open()
}

const toggleNotifications = () => {
  console.log('Toggle notifications')
  // Future: Open notification drawer
}

const toggleUserMenu = () => {
  console.log('Toggle user menu')
  // Future: Open user dropdown
}

</script>

<style scoped lang="scss">
@import '@/styles/artdeco-main.css';

// ============================================
//   ART DECO LAYOUT (Refactored)
// ============================================

.artdeco-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--artdeco-bg-global);
  overflow: hidden;
}

// Main Content Area
.artdeco-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--artdeco-bg-global);
  
  // Transition handled by sidebar component width change usually, 
  // but if we need margin transition:
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

// Breadcrumb Container
.artdeco-breadcrumb-container {
  padding: var(--artdeco-space-2) var(--artdeco-space-6);
  border-bottom: 1px solid var(--artdeco-border-subtle);
  background: var(--artdeco-bg-header);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  height: 48px; // Fixed height for consistency
}

// Content Container
.artdeco-content {
  flex: 1;
  overflow-y: auto; // Main scrollable area
  overflow-x: hidden;
  padding: var(--artdeco-space-6);
  position: relative;
  scroll-behavior: smooth;
  
  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--artdeco-bg-elevated);
    border-radius: 3px;
    &:hover {
      background: var(--artdeco-gold-muted);
    }
  }
}

// Connection Status
.connection-status {
  position: absolute;
  top: var(--artdeco-space-2);
  right: var(--artdeco-space-6);
  background: rgba(244, 67, 54, 0.1); // Error color with opacity
  border: 1px solid var(--artdeco-error);
  color: var(--artdeco-error);
  padding: 4px 12px;
  font-size: 11px;
  border-radius: 12px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(4px);
}

// Transitions
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
