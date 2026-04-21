<template>
  <div class="artdeco-layout">
    <!-- Sidebar: Correctly imported collapsible sidebar -->
    <ArtDecoSidebar />

    <!-- Main Content Area -->
    <main class="artdeco-main" :class="{ 'sidebar-collapsed': preferenceStore.sidebarCollapsed }">
      <!-- Top Bar: Core ArtDeco header -->
      <ArtDecoHeader
        :unread-count="unreadCount"
        :user-name="userName"
        @open-command-palette="openCommandPalette"
        @open-notifications="toggleNotifications"
        @open-user-menu="toggleUserMenu"
      >
        <template #actions>
          <div v-if="headerSummary.marketStatus.value" class="header-metrics">
            <ArtDecoBadge variant="gold" pulse>
              <ArtDecoIcon name="activity" />
              {{ headerSummary.activeStrategiesCount.value ?? 0 }} 策略运行中
            </ArtDecoBadge>
            <ArtDecoBadge variant="success" pulse>
              <ArtDecoIcon name="trending-up" />
              {{ headerSummary.todayPnLValue.value }}
            </ArtDecoBadge>
          </div>
          <div v-if="headerSummary.marketStatus.value" class="time-refresh">
            <div class="time-display">
              <ArtDecoIcon name="clock" />
              <span class="time-value">{{ headerSummary.currentTime.value }}</span>
            </div>
            <ArtDecoButton variant="outline" size="sm"
              @click="headerSummary.refresh()" :loading="headerSummary.refreshing.value">
              <template #icon><ArtDecoIcon name="refresh" /></template>
              刷新数据
            </ArtDecoButton>
          </div>
        </template>
      </ArtDecoHeader>

      <!-- Breadcrumb Navigation -->
      <div v-show="showBreadcrumb" class="artdeco-breadcrumb-container">
        <ArtDecoBreadcrumb
          ref="breadcrumbRef"
          home-title="交易室"
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
            <!-- Guard against transient null component during async route resolution. -->
            <component v-if="Component" :is="Component" :key="route.fullPath" />
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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMenuStore } from '@/stores/menuStore'
import { usePreferenceStore } from '@/stores/preferenceStore'
import { useLiveDataManager } from '@/composables/useLiveDataManager'
import { useHeaderSummary } from '@/composables/useHeaderSummary'

// ✅ 修正组件引用路径
import ArtDecoSidebar from '@/components/artdeco/trading/ArtDecoCollapsibleSidebar.vue'
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
import CommandPalette from '@/components/menu/CommandPalette.vue'
import PerformanceMonitor from '@/components/common/PerformanceMonitor.vue'
import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'

// ✅ 修正菜单配置引用
import { ARTDECO_MENU_ITEMS } from './MenuConfig'

// Store & Route
const route = useRoute()
const _menuStore = useMenuStore()
const preferenceStore = usePreferenceStore()

// Layout State
const unreadCount = ref(3) // Mock data
const userName = ref('Admin User')
const commandPaletteRef = ref<{ open: () => void } | null>(null)
const breadcrumbRef = ref<InstanceType<typeof ArtDecoBreadcrumb> | null>(null)
const devMode = import.meta.env.DEV

const showBreadcrumb = computed(() => (breadcrumbRef.value?.breadcrumbs?.length ?? 0) > 0)

// Live Data Management
const { isConnected: isLiveDataConnected } = useLiveDataManager(ARTDECO_MENU_ITEMS)

// Header Summary
const headerSummary = useHeaderSummary()

// Methods
const openCommandPalette = () => {
  commandPaletteRef.value?.open()
}

const toggleNotifications = () => {
  console.log('Toggle notifications')
}

const toggleUserMenu = () => {
  console.log('Toggle user menu')
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
  margin-left: var(--artdeco-sidebar-width); /* Default */
  
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &.sidebar-collapsed {
    margin-left: var(--artdeco-sidebar-collapsed-width);
  }
}

// Breadcrumb Container
.artdeco-breadcrumb-container {
  padding: var(--artdeco-space-2) var(--artdeco-space-6);
  border-bottom: 1px solid var(--artdeco-border-subtle);
  background: var(--artdeco-bg-header);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  height: 48px;
}

// Content Container
.artdeco-content {
  flex: 1;
  overflow: hidden auto;
  padding: var(--artdeco-space-6);
  position: relative;
  scroll-behavior: smooth;
  
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
  background: rgba(244, 67, 54, 0.1);
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
.header-metrics {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-6);

  :deep(.artdeco-badge) {
    border: none;
    background: transparent;
  }
}

.time-refresh {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);

  :deep(.artdeco-button) {
    border: none;
    background: transparent;

    .artdeco-button__icon {
      margin-right: 0 !important;
      padding-right: 0 !important;
    }
  }

  .time-display {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-1);
  }

  .time-value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-gold-primary);
    font-weight: 600;
  }
}
</style>
