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
                            v-for="(item, _idx) in menuItems"
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
    const _checkMobile = () => {
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
            if (typeof window !== 'undefined' && (window as unknown as { gtag: (...args: unknown[]) => void }).gtag) {
                ;(window as unknown as { gtag: (...args: unknown[]) => void }).gtag('event', 'command_palette_open', {
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
            if (typeof window !== 'undefined' && (window as unknown as { gtag: (...args: unknown[]) => void }).gtag) {
                ;(window as unknown as { gtag: (...args: unknown[]) => void }).gtag('event', 'command_palette_close', {
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
            if (typeof window !== 'undefined' && (window as unknown as { gtag: (...args: unknown[]) => void }).gtag) {
                ;(window as unknown as { gtag: (...args: unknown[]) => void }).gtag('event', 'command_palette_navigate', {
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

<style scoped lang="scss" src="./styles/ArtDecoBaseLayout.scss"></style>
