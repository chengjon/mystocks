<template>
    <div class="main-layout">
        <!-- Sidebar Navigation -->
        <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed }">
            <!-- Logo Area -->
            <div class="sidebar-header">
                <transition name="fade">
                    <div v-if="!isCollapsed" class="logo-container">
                        <div class="logo-icon">
                            <svg viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="2" />
                                <path
                                    d="M50 30 L50 70 M30 50 L70 50"
                                    stroke="currentColor"
                                    stroke-width="3"
                                    stroke-linecap="round"
                                />
                            </svg>
                        </div>
                        <div class="logo-text">
                            <h1 class="logo-title">MyStocks</h1>
                            <p class="logo-subtitle">专业股票分析</p>
                        </div>
                    </div>
                </transition>

                <button v-if="isCollapsed" class="logo-icon-collapsed" @click="toggleSidebar">
                    <svg viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="2" />
                        <path
                            d="M50 30 L50 70 M30 50 L70 50"
                            stroke="currentColor"
                            stroke-width="3"
                            stroke-linecap="round"
                        />
                    </svg>
                </button>
            </div>

            <!-- Navigation Menu -->
            <nav class="sidebar-nav">
                <div v-for="(section, index) in menuSections" :key="index" class="nav-section">
                    <div v-if="!isCollapsed" class="nav-section-title">
                        {{ section.title }}
                    </div>

                    <div class="nav-items">
                        <router-link
                            v-for="item in section.items"
                            :key="item.path"
                            :to="item.path"
                            class="nav-item"
                            :class="{ 'nav-item-active': isActive(item.path) }"
                        >
                            <component :is="item.icon" class="nav-icon" />
                            <transition name="fade">
                                <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
                            </transition>
                            <div v-if="isActive(item.path)" class="nav-indicator"></div>
                        </router-link>
                    </div>
                </div>
            </nav>

            <!-- Sidebar Footer -->
            <div class="sidebar-footer">
                <button class="collapse-btn" @click="toggleSidebar">
                    <el-icon>
                        <Fold v-if="!isCollapsed" />
                        <Expand v-else />
                    </el-icon>
                </button>
            </div>
        </aside>

        <!-- Main Content Area -->
        <div class="main-content">
            <!-- Top Header -->
            <header class="top-header">
                <div class="header-left">
                    <el-breadcrumb separator="/">
                        <el-breadcrumb-item v-for="crumb in breadcrumbs" :key="crumb.path" :to="crumb.path">
                            {{ crumb.title }}
                        </el-breadcrumb-item>
                    </el-breadcrumb>
                </div>

                <div class="header-right">
                    <!-- Search -->
                    <div class="header-search">
                        <el-input
                            v-model="searchQuery"
                            placeholder="搜索股票、代码..."
                            :prefix-icon="Search"
                            clearable
                        />
                    </div>

                    <!-- Notifications -->
                    <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="header-action">
                        <el-button :icon="Bell" circle />
                    </el-badge>

                    <!-- User Menu -->
                    <el-dropdown>
                        <el-button :icon="UserFilled" circle />
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item>个人设置</el-dropdown-item>
                                <el-dropdown-item divided>退出登录</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </header>

            <!-- Page Content -->
            <main class="page-content">
                <router-view v-slot="{ Component }">
                    <transition name="fade" mode="out-in">
                        <component :is="Component" :key="$route.path" />
                    </transition>
                </router-view>
            </main>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, watch } from 'vue'
    import { useRoute, useRouter } from 'vue-router'
    import {
        Search,
        Bell,
        UserFilled,
        Fold,
        Expand,
        DataAnalysis,
        TrendCharts,
        Monitor,
        Warning,
        Setting
    } from '@element-plus/icons-vue'

    const route = useRoute()
    const router = useRouter()

    // State
    const isCollapsed = ref(false)
    const searchQuery = ref('')
    const notificationCount = ref(3)

    // Menu Configuration - Art Deco 风格导航
    const menuSections = [
        {
            title: '仪表盘',
            items: [
                { path: '/dashboard', label: '概览', icon: DataAnalysis },
                { path: '/dashboard/watchlist', label: '自选股', icon: TrendCharts },
                { path: '/dashboard/portfolio', label: '投资组合', icon: Monitor },
                { path: '/dashboard/activity', label: '交易活动', icon: TrendCharts }
            ]
        },
        {
            title: '市场数据',
            items: [
                { path: '/market/list', label: '股票列表', icon: DataAnalysis },
                { path: '/market/realtime', label: '实时行情', icon: TrendCharts },
                { path: '/market/kline', label: 'K线图', icon: Monitor }
            ]
        },
        {
            title: '分析工具',
            items: [
                { path: '/analysis/screener', label: '选股器', icon: DataAnalysis },
                { path: '/analysis/technical', label: '技术分析', icon: TrendCharts },
                { path: '/risk/overview', label: '风险监控', icon: Warning }
            ]
        },
        {
            title: '系统',
            items: [{ path: '/settings', label: '设置', icon: Setting }]
        }
    ]

    // Computed
    const breadcrumbs = computed(() => {
        const crumbs = [{ title: '首页', path: '/dashboard' }]

        if (route.meta.title) {
            crumbs.push({ title: route.meta.title, path: route.path })
        }

        return crumbs
    })

    // Methods
    const toggleSidebar = () => {
        isCollapsed.value = !isCollapsed.value
    }

    const isActive = path => {
        return route.path === path || route.path.startsWith(path + '/')
    }

    // Watch route changes
    watch(
        () => route.path,
        () => {
            // Auto-collapse sidebar on mobile
            if (window.innerWidth < 1024) {
                isCollapsed.value = true
            }
        }
    )
</script>

<style scoped>
    /**
 * Main Layout - Art Deco Financial Terminal Style
 * 精致、优雅、专业的金融终端界面
 */

    .main-layout {
        display: flex;
        height: 100vh;
        overflow: hidden;
    }

    /* ========================================
   SIDEBAR - 侧边栏导航
   ======================================== */

    .sidebar {
        width: 260px;
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-right: 1px solid rgba(212, 175, 55, 0.1);
        display: flex;
        flex-direction: column;
        transition: width var(--transition-base);
        position: relative;
        z-index: var(--z-sticky);
    }

    .sidebar-collapsed {
        width: 80px;
    }

    /* Sidebar Header */
    .sidebar-header {
        padding: var(--space-6);
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    }

    .logo-container {
        display: flex;
        align-items: center;
        gap: var(--space-4);
    }

    .logo-icon,
    .logo-icon-collapsed {
        width: 48px;
        height: 48px;
        color: var(--accent-primary);
        flex-shrink: 0;
    }

    .logo-icon-collapsed {
        margin: 0 auto;
        cursor: pointer;
        transition: transform var(--transition-fast);

        &:hover {
            transform: scale(1.1);
        }
    }

    .logo-text {
        flex: 1;
    }

    .logo-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--accent-primary);
        letter-spacing: 0.1em;
        margin: 0;
    }

    .logo-subtitle {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin: 0;
        letter-spacing: 0.05em;
    }

    /* Navigation */
    .sidebar-nav {
        flex: 1;
        overflow-y: auto;
        padding: var(--space-4) 0;
    }

    .nav-section {
        margin-bottom: var(--space-6);
    }

    .nav-section-title {
        padding: 0 var(--space-6);
        margin-bottom: var(--space-2);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-tertiary);
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .nav-items {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
    }

    .nav-item {
        position: relative;
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-6);
        color: var(--text-secondary);
        text-decoration: none;
        transition: all var(--transition-fast);
        border-left: 3px solid transparent;
    }

    .nav-item:hover {
        color: var(--text-primary);
        background: rgba(212, 175, 55, 0.05);
    }

    .nav-item-active {
        color: var(--accent-primary);
        background: rgba(212, 175, 55, 0.1);
        border-left-color: var(--accent-primary);
    }

    .nav-icon {
        font-size: 20px;
        flex-shrink: 0;
    }

    .nav-label {
        flex: 1;
        font-size: 0.875rem;
        font-weight: 500;
        white-space: nowrap;
    }

    .nav-indicator {
        position: absolute;
        right: var(--space-2);
        width: 6px;
        height: 6px;
        background: var(--accent-primary);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--accent-primary);
    }

    /* Sidebar Footer */
    .sidebar-footer {
        padding: var(--space-4);
        border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .collapse-btn {
        width: 100%;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-secondary);
        background: transparent;
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all var(--transition-fast);

        &:hover {
            color: var(--accent-primary);
            border-color: var(--accent-primary);
            background: rgba(212, 175, 55, 0.1);
        }
    }

    /* ========================================
   MAIN CONTENT
   ======================================== */

    .main-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        background: var(--bg-primary);
    }

    /* Top Header */
    .top-header {
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 var(--space-6);
        background: var(--bg-secondary);
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    }

    .header-left {
        flex: 1;
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: var(--space-4);
    }

    .header-search {
        width: 300px;
    }

    .header-action {
        cursor: pointer;
    }

    /* Page Content */
    .page-content {
        flex: 1;
        overflow-y: auto;
        padding: var(--space-6);
    }

    /* ========================================
   TRANSITIONS
   ======================================== */

    .fade-enter-active,
    .fade-leave-active {
        transition: opacity 0.2s ease;
    }

    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }

    /* ========================================
   RESPONSIVE
   ======================================== */

    @media (max-width: 1024px) {
        .sidebar {
            position: absolute;
            height: 100%;
            z-index: var(--z-modal);
            box-shadow: var(--shadow-xl);
        }

        .sidebar-collapsed {
            width: 0;
            overflow: hidden;
        }

        .header-search {
            width: 200px;
        }
    }

    @media (max-width: 768px) {
        .top-header {
            padding: 0 var(--space-4);
        }

        .header-search {
            width: 150px;
        }

        .page-content {
            padding: var(--space-4);
        }
    }
</style>
