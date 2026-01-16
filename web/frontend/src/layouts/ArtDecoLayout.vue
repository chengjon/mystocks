<template>
    <div class="artdeco-layout">
        <!-- Dynamic Sidebar -->
        <ArtDecoDynamicSidebar ref="sidebarRef" class="artdeco-sidebar" />

        <!-- Main Content Area -->
        <div class="artdeco-main">
            <!-- Content Container with proper spacing -->
            <div class="artdeco-content">
                <!-- Page Content Slot -->
                <slot />
            </div>
        </div>
    </div>
</template>

<script setup>
    import ArtDecoDynamicSidebar from '@/components/artdeco/specialized/ArtDecoDynamicSidebar.vue'
    import { ref, onMounted } from 'vue'
    import { useRoute } from 'vue-router'

    // 响应式数据
    const sidebarRef = ref()

    // 路由信息
    const route = useRoute()

    // 在组件挂载后，根据当前路由设置侧边栏的活动模块
    onMounted(() => {
        if (sidebarRef.value) {
            // 根据路由路径自动设置活动模块
            const path = route.path

            if (path.startsWith('/dashboard') || path === '/') {
                sidebarRef.value.switchModule('dashboard')
            } else if (path.startsWith('/market')) {
                sidebarRef.value.switchModule('market')
            } else if (path.startsWith('/stocks') || path.startsWith('/portfolio') || path.startsWith('/trade')) {
                sidebarRef.value.switchModule('stocks')
            } else if (
                path.startsWith('/analysis') ||
                path.startsWith('/technical') ||
                path.startsWith('/indicators')
            ) {
                sidebarRef.value.switchModule('analysis')
            } else if (path.startsWith('/risk')) {
                sidebarRef.value.switchModule('risk')
            } else if (path.startsWith('/strategy') || path.startsWith('/backtest')) {
                sidebarRef.value.switchModule('strategy')
            } else if (path.startsWith('/system') || path.startsWith('/settings')) {
                sidebarRef.value.switchModule('system')
            }
        }
    })
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
