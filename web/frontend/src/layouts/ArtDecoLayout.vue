<template>
  <BaseLayout
    page-title="MyStocks 量化交易管理中心"
    :menu-items="ARTDECO_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { ARTDECO_MENU_ITEMS } from './MenuConfig'
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
    .artdeco-sidebar {
        flex-shrink: 0;
    }

    // Main Content Area
    .artdeco-main {
        flex: 1;
        margin-left: 320px; // Match sidebar width
        min-height: 100vh;
        background: var(--artdeco-bg-global);
    }

    // Content Container
    .artdeco-content {
        padding: var(--artdeco-spacing-6);
        max-width: none; // Allow full width for content
    }

    // ============================================
    //   RESPONSIVE DESIGN
    // ============================================
    @media (max-width: 1400px) {
        .artdeco-main {
            margin-left: 280px; // Match responsive sidebar width
        }
    }

    @media (max-width: 1024px) {
        .artdeco-main {
            margin-left: 260px; // Match responsive sidebar width
        }
    }

    @media (max-width: 768px) {
        // For mobile/tablet, we might need to hide sidebar or make it overlay
        // But since we only support desktop, this is kept for reference
        .artdeco-main {
            margin-left: 0;
        }

        .artdeco-sidebar {
            display: none; // Hide sidebar on mobile for now
        }
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
