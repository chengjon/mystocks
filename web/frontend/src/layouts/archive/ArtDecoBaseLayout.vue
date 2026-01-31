<template>
    <div class="artdeco-base-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <!-- Skip to Content Link (Accessibility) -->
        <ArtDecoSkipLink />

        <!-- ArtDeco Top Bar -->
        <header class="artdeco-layout-header">
            <div class="header-left">
                <!-- Sidebar Toggle -->
                <button class="artdeco-sidebar-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
                    <span class="toggle-icon">☰</span>
                </button>

                <!-- Breadcrumb Navigation -->
                <ArtDecoBreadcrumb />
            </div>

            <div class="header-center">
                <h1 class="artdeco-page-title">{{ pageTitle }}</h1>
            </div>

            <div class="header-right">
                <!-- Search Trigger -->
                <button class="artdeco-search-trigger" @click="openCommandPalette" aria-label="Search">
                    <span class="search-icon">🔍</span>
                    <span class="search-kbd">Ctrl+K</span>
                </button>

                <!-- Notifications -->
                <button class="artdeco-notification-btn" aria-label="Notifications">
                    <span class="notification-icon">🔔</span>
                    <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
                </button>

                <!-- User Menu -->
                <div class="artdeco-user-menu">
                    <button class="user-menu-btn">
                        <span class="user-avatar">👤</span>
                        <span class="user-name">Admin</span>
                    </button>
                </div>
            </div>
        </header>

        <!-- Main Content Area -->
        <div class="artdeco-layout-body">
            <!-- ArtDeco Sidebar -->
            <aside class="artdeco-layout-sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
                <!-- Sidebar Header with Logo -->
                <div class="sidebar-header">
                    <router-link to="/" class="sidebar-logo">
                        <div class="logo-frame">
                            <span class="logo-text">MYSTOCKS</span>
                            <span class="logo-subtitle">ArtDeco</span>
                        </div>
                    </router-link>

                    <!-- Decorative divider -->
                    <div class="sidebar-divider">
                        <div class="divider-ornament">◆</div>
                    </div>
                </div>

                <!-- Navigation Menu -->
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
                                <span v-if="item.badge" class="nav-badge artdeco-badge">{{ item.badge }}</span>
                            </router-link>
                        </li>
                    </ul>
                </nav>
            </aside>

            <!-- Main Content -->
            <main id="main-content" class="artdeco-layout-main" tabindex="-1">
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
    import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
    import { useRoute } from 'vue-router'
    import ArtDecoSkipLink from '@/components/artdeco/base/ArtDecoSkipLink.vue'
    import ArtDecoBreadcrumb from '@/components/artdeco/core/ArtDecoBreadcrumb.vue'
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
    const isMobile = ref(false)

    // Computed
    const commandItems = computed((): CommandItem[] => {
        // Memoize command items to avoid unnecessary re-computation
        return props.menuItems.map(item => ({
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

    // Mobile detection
    const checkMobile = () => {
        isMobile.value = window.innerWidth <= 1024
    }

    // Keyboard navigation
    const handleKeydown = (event: KeyboardEvent) => {
        // Ctrl/Cmd + B to toggle sidebar
        if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
            event.preventDefault()
            toggleSidebar()
        }
    }

    // Initialize keyboard navigation
    onMounted(() => {
        document.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
        document.removeEventListener('keydown', handleKeydown)
    })

    const isActive = (path: string) => {
        return route.path.startsWith(path)
    }

    const openCommandPalette = () => {
        commandPaletteRef.value?.open()
    }

    const onCommandPaletteOpen = () => {
        try {
            // Analytics tracking
            if (typeof window !== 'undefined' && (window as any).gtag) {
                ;(window as any).gtag('event', 'command_palette_open', {
                    event_category: 'navigation',
                    event_label: props.pageTitle
                })
            }
        } catch (error) {
            console.warn('Analytics error:', error)
        }
    }

    const onCommandPaletteClose = () => {
        try {
            // Analytics tracking
            if (typeof window !== 'undefined' && (window as any).gtag) {
                ;(window as any).gtag('event', 'command_palette_close', {
                    event_category: 'navigation',
                    event_label: props.pageTitle
                })
            }
        } catch (error) {
            console.warn('Analytics error:', error)
        }
    }

    const onCommandPaletteNavigate = (path: string) => {
        try {
            // Analytics tracking
            if (typeof window !== 'undefined' && (window as any).gtag) {
                ;(window as any).gtag('event', 'command_palette_navigate', {
                    event_category: 'navigation',
                    event_label: path
                })
            }
        } catch (error) {
            console.warn('Analytics error:', error)
        }
    }

    // Watch route changes to update document title
    watch(
        () => route.path,
        () => {
            document.title = `${props.pageTitle} - MyStocks`
        },
        { immediate: true }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   ART DECO BASE LAYOUT
    //   Luxury aesthetic with Art Deco design system
    // ============================================

    .artdeco-base-layout {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        background: var(--artdeco-bg-global);
        color: var(--artdeco-fg-primary);
    }

    // ============================================
    //   HEADER - ArtDeco Top Bar
    // ============================================

    .artdeco-layout-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 64px;
        padding: 0 var(--artdeco-spacing-6);
        background: var(--artdeco-bg-base);
        border-bottom: 2px solid var(--artdeco-border-default);
        position: relative;
        flex-shrink: 0;
        z-index: 100;

        // Decorative corner ornaments (ArtDeco signature)
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 20px;
            height: 20px;
            border-top: 2px solid var(--artdeco-gold-primary);
            border-left: 2px solid var(--artdeco-gold-primary);
            opacity: 0.4;
        }

        &::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 20px;
            height: 20px;
            border-top: 2px solid var(--artdeco-gold-primary);
            border-right: 2px solid var(--artdeco-gold-primary);
            opacity: 0.4;
        }
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
    }

    .header-center {
        flex: 1;
        text-align: center;
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-4);
    }

    // Sidebar Toggle Button
    .artdeco-sidebar-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: transparent;
        border: 1px solid var(--artdeco-border-default);
        cursor: pointer;
        transition: all var(--artdeco-transition-base) var(--artdeco-ease-out);
        color: var(--artdeco-gold-primary);

        &:hover {
            background: rgba(212, 175, 55, 0.15);
            border-color: var(--artdeco-gold-primary);
            box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
            transform: translateY(-1px);
        }

        .toggle-icon {
            font-size: var(--artdeco-text-xl);
        }
    }

    // Page Title - ArtDeco Typography
    .artdeco-page-title {
        font-family: var(--artdeco-font-heading, 'Marcellus', serif);
        font-size: var(--artdeco-text-lg, 18px);
        font-weight: 700;
        color: var(--artdeco-gold-primary, #d4af37);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider, 0.2em);
        margin: 0;
        text-shadow: 0 1px 2px rgba(212, 175, 55, 0.3);
    }

    // Search Trigger
    .artdeco-search-trigger {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-elevated);
        border: 1px solid var(--artdeco-border-default);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);
        color: var(--artdeco-fg-muted);

        &:hover {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
        }

        .search-icon {
            font-size: var(--artdeco-text-lg);
        }

        .search-kbd {
            padding: 2px 6px;
            background: var(--artdeco-bg-card);
            border: 1px solid var(--artdeco-border-default);
            border-radius: var(--artdeco-radius-sm);
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
        }
    }

    // Notification Button
    .artdeco-notification-btn {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: transparent;
        border: 1px solid var(--artdeco-border-default);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--artdeco-gold-primary);
        }

        .notification-icon {
            font-size: var(--artdeco-text-lg);
        }

        .notification-badge {
            position: absolute;
            top: -4px;
            right: -4px;
            min-width: 18px;
            height: 18px;
            padding: 0 6px;
            background: var(--artdeco-error);
            color: var(--artdeco-bg-global);
            border-radius: var(--artdeco-radius-sm);
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            line-height: 18px;
            text-align: center;
        }
    }

    // User Menu
    .artdeco-user-menu {
        .user-menu-btn {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-3);
            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
            background: var(--artdeco-bg-elevated);
            border: 1px solid var(--artdeco-border-default);
            cursor: pointer;
            transition: all var(--artdeco-transition-base);

            &:hover {
                background: rgba(212, 175, 55, 0.1);
                border-color: var(--artdeco-gold-primary);
            }

            .user-avatar {
                font-size: var(--artdeco-text-xl);
            }

            .user-name {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    // ============================================
    //   LAYOUT BODY
    // ============================================

    .artdeco-layout-body {
        display: flex;
        flex: 1;
        overflow: hidden;
    }

    // ============================================
    //   SIDEBAR - ArtDeco Navigation
    // ============================================

    .artdeco-layout-sidebar {
        width: 280px;
        background: var(--artdeco-bg-base);
        border-right: 2px solid var(--artdeco-border-default);
        overflow-y: auto;
        overflow-x: hidden;
        transition: width var(--artdeco-transition-base) var(--artdeco-ease-out);
        flex-shrink: 0;
        position: relative;

        // Decorative background pattern (ArtDeco crosshatch)
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                repeating-linear-gradient(
                    45deg,
                    rgba(212, 175, 55, 0.02) 0px,
                    rgba(212, 175, 55, 0.02) 1px,
                    transparent 1px,
                    transparent 4px
                ),
                repeating-linear-gradient(
                    -45deg,
                    rgba(212, 175, 55, 0.02) 0px,
                    rgba(212, 175, 55, 0.02) 1px,
                    transparent 1px,
                    transparent 4px
                );
            opacity: 0.5;
            pointer-events: none;
        }

        .sidebar-collapsed & {
            width: 80px;

            .nav-label,
            .nav-badge {
                display: none;
            }

            .nav-link {
                justify-content: center;
                padding: var(--artdeco-spacing-4);
            }

            .logo-subtitle {
                display: none;
            }
        }
    }

    // Sidebar Header
    .sidebar-header {
        padding: var(--artdeco-spacing-6);
        border-bottom: 2px solid var(--artdeco-border-default);
        position: relative;
        background: var(--artdeco-bg-card);

        // Decorative corners
        &::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 16px;
            height: 16px;
            border-bottom: 2px solid var(--artdeco-gold-primary);
            border-left: 2px solid var(--artdeco-gold-primary);
            opacity: 0.3;
        }

        &::after {
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 16px;
            height: 16px;
            border-bottom: 2px solid var(--artdeco-gold-primary);
            border-right: 2px solid var(--artdeco-gold-primary);
            opacity: 0.3;
        }
    }

    .sidebar-logo {
        display: block;
        text-decoration: none;
        margin-bottom: var(--artdeco-spacing-4);

        .logo-frame {
            text-align: center;
        }

        .logo-text {
            display: block;
            font-family: var(--artdeco-font-heading);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-widest);
        }

        .logo-subtitle {
            display: block;
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-xs);
            font-weight: 600;
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }
    }

    .sidebar-divider {
        position: relative;
        height: 2px;
        background: linear-gradient(
            to right,
            transparent,
            var(--artdeco-gold-dim) 20%,
            var(--artdeco-gold-dim) 80%,
            transparent
        );
        margin: var(--artdeco-spacing-4) 0;

        .divider-ornament {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: var(--artdeco-gold-primary);
            font-size: var(--artdeco-text-sm);
        }
    }

    // Navigation
    .sidebar-nav {
        padding: var(--artdeco-spacing-4) 0;
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
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
        color: var(--artdeco-fg-muted);
        text-decoration: none;
        transition: all var(--artdeco-transition-base);
        border-left: 2px solid transparent;
        position: relative;

        &:hover {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(212, 175, 55, 0.04));
            color: var(--artdeco-gold-primary);
            border-left-color: var(--artdeco-gold-primary);
            box-shadow: inset 0 0 8px rgba(212, 175, 55, 0.2);
            transform: translateX(2px);
        }

        &.active,
        &.router-link-active {
            background: rgba(212, 175, 55, 0.15);
            color: var(--artdeco-gold-primary);
            border-left-color: var(--artdeco-gold-primary);

            .nav-label {
                color: var(--artdeco-gold-primary);
            }
        }
    }

    .nav-icon {
        font-size: var(--artdeco-text-xl);
        width: 24px;
        text-align: center;
    }

    .nav-label {
        flex: 1;
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
    }

    .nav-badge {
        padding: 2px 8px;
        background: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-radius: var(--artdeco-radius-sm);
    }

    // ============================================
    //   MAIN CONTENT
    // ============================================

    .artdeco-layout-main {
        flex: 1;
        overflow-y: auto;
        background: var(--artdeco-bg-global);
        position: relative;

        // Subtle background pattern
        &::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                repeating-linear-gradient(
                    45deg,
                    rgba(212, 175, 55, 0.015) 0px,
                    rgba(212, 175, 55, 0.015) 1px,
                    transparent 1px,
                    transparent 4px
                ),
                repeating-linear-gradient(
                    -45deg,
                    rgba(212, 175, 55, 0.015) 0px,
                    rgba(212, 175, 55, 0.015) 1px,
                    transparent 1px,
                    transparent 4px
                );
            opacity: 0.3;
            pointer-events: none;
            z-index: 0;
        }
    }

    .content-wrapper {
        position: relative;
        padding: var(--artdeco-spacing-8);
        min-height: calc(100vh - 64px);
        z-index: 1;
        max-width: 1800px;
        margin: 0 auto;
    }

    // ============================================
    //   SCROLLBAR STYLING
    // ============================================

    .artdeco-layout-sidebar,
    .artdeco-layout-main {
        // Custom scrollbar for Webkit browsers
        &::-webkit-scrollbar {
            width: 8px;
        }

        &::-webkit-scrollbar-track {
            background: var(--artdeco-bg-base);
        }

        &::-webkit-scrollbar-thumb {
            background: var(--artdeco-gold-dim);
            border-radius: var(--artdeco-radius-sm);

            &:hover {
                background: var(--artdeco-gold-primary);
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN (DESKTOP ONLY)
    // ============================================

    // Large screens - enhanced ArtDeco experience
    @media (min-width: 1920px) {
        .artdeco-layout-sidebar {
            width: 320px;

            &.sidebar-collapsed {
                width: 80px;
            }
        }

        .content-wrapper {
            padding: var(--artdeco-spacing-10);
        }

        // Enhanced decorative elements for large screens
        .artdeco-layout-header::before,
        .artdeco-layout-header::after {
            width: 24px;
            height: 24px;
        }

        .sidebar-header::before,
        .sidebar-header::after {
            width: 18px;
            height: 18px;
        }
    }

    // Standard desktop optimization
    @media (min-width: 1440px) {
        .artdeco-layout-sidebar {
            width: 300px;

            &.sidebar-collapsed {
                width: 80px;
            }
        }
    }
</style>
