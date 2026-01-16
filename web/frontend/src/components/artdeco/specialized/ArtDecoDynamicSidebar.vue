<template>
    <nav class="artdeco-dynamic-sidebar">
        <!-- Decorative background pattern -->
        <div class="artdeco-sidebar-pattern"></div>

        <!-- Header Section -->
        <div class="artdeco-sidebar-header">
            <!-- Decorative corner ornaments -->
            <div class="artdeco-corner-tl"></div>
            <div class="artdeco-corner-tr"></div>

            <!-- Logo with ArtDeco style -->
            <router-link to="/dashboard" class="artdeco-logo">
                <div class="artdeco-logo-frame">
                    <span class="artdeco-logo-text">MYSTOCKS</span>
                    <span class="artdeco-logo-subtitle">ArtDeco Edition</span>
                </div>
            </router-link>

            <!-- Decorative divider line with ornament -->
            <div class="artdeco-header-divider">
                <div class="artdeco-divider-ornament"></div>
            </div>
        </div>

        <!-- Module Selection Tabs -->
        <div class="artdeco-module-tabs">
            <button
                v-for="module in modules"
                :key="module.key"
                class="module-tab"
                :class="{ active: activeModule === module.key }"
                @click="switchModule(module.key)"
            >
                <span class="module-icon">{{ module.icon }}</span>
                <span class="module-label">{{ module.label }}</span>
            </button>
        </div>

        <!-- Navigation Menu (Dynamic based on active module) -->
        <div class="artdeco-nav">
            <!-- Current Module Navigation -->
            <div class="artdeco-nav-section animate-in">
                <div class="artdeco-nav-section-header">
                    <div class="artdeco-nav-section-icon">{{ currentModuleIcon }}</div>
                    <div class="artdeco-nav-section-title">{{ currentModuleTitle }}</div>
                    <div class="artdeco-nav-section-line"></div>
                </div>

                <router-link
                    v-for="item in currentMenuItems"
                    :key="item.path"
                    :to="item.path"
                    class="artdeco-nav-item"
                    active-class="active"
                >
                    <div class="artdeco-nav-number">{{ item.number }}</div>
                    <div class="artdeco-nav-content">
                        <div class="artdeco-nav-label">{{ item.label }}</div>
                        <div class="artdeco-nav-subtitle">{{ item.subtitle }}</div>
                    </div>
                </router-link>
            </div>
        </div>

        <!-- Footer with decorative element -->
        <div class="artdeco-sidebar-footer">
            <div class="artdeco-footer-ornament">❧</div>
            <div class="artdeco-footer-text">EST. 2025</div>
        </div>
    </nav>
</template>

<script setup>
    import { ref, computed } from 'vue'

    // 响应式数据
    const activeModule = ref('dashboard')

    // 模块配置
    const modules = [
        { key: 'dashboard', label: '仪表盘', icon: '📊' },
        { key: 'market', label: '市场行情', icon: '📈' },
        { key: 'stocks', label: '股票管理', icon: '📋' },
        { key: 'analysis', label: '投资分析', icon: '🔍' },
        { key: 'risk', label: '风险管理', icon: '⚠️' },
        { key: 'strategy', label: '策略交易', icon: '🎯' },
        { key: 'system', label: '系统监控', icon: '🔧' }
    ]

    // 各模块的菜单项配置
    const menuConfigs = {
        dashboard: {
            title: 'DASHBOARD',
            icon: '◈',
            items: [
                { path: '/dashboard', label: '主控仪表盘', subtitle: 'Dashboard', number: 'Ⅰ' },
                { path: '/artdeco-test', label: 'ArtDeco测试', subtitle: 'ArtDeco Test', number: 'Ⅱ' }
            ]
        },
        market: {
            title: 'MARKET DATA',
            icon: '◈',
            items: [
                { path: '/market', label: '实时行情监控', subtitle: 'Realtime Quotes', number: 'Ⅰ' },
                { path: '/market-quotes', label: '市场行情中心', subtitle: 'Market Quotes', number: 'Ⅱ' },
                { path: '/market-data', label: '市场数据分析', subtitle: 'Market Data', number: 'Ⅲ' }
            ]
        },
        stocks: {
            title: 'STOCK MANAGEMENT',
            icon: '◇',
            items: [
                { path: '/stocks', label: '自选股管理', subtitle: 'Watchlist', number: 'Ⅰ' },
                { path: '/portfolio', label: '投资组合', subtitle: 'Portfolio', number: 'Ⅱ' },
                { path: '/trade', label: '交易管理', subtitle: 'Trading', number: 'Ⅲ' },
                { path: '/trading-management', label: '交易管理中心', subtitle: 'Trade Center', number: 'Ⅳ' }
            ]
        },
        analysis: {
            title: 'INVESTMENT ANALYSIS',
            icon: '◆',
            items: [
                { path: '/data-analysis', label: '数据分析中心', subtitle: 'Data Analysis Center', number: 'Ⅰ' },
                { path: '/technical', label: '技术分析', subtitle: 'Technical', number: 'Ⅱ' },
                { path: '/indicators', label: '指标库', subtitle: 'Indicators', number: 'Ⅲ' }
            ]
        },
        risk: {
            title: 'RISK MANAGEMENT',
            icon: '◊',
            items: [
                { path: '/risk', label: '风险监控', subtitle: 'Risk Monitor', number: 'Ⅰ' },
                { path: '/risk-management', label: '风险管理中心', subtitle: 'Risk Center', number: 'Ⅱ' }
            ]
        },
        strategy: {
            title: 'STRATEGY & TRADING',
            icon: '❖',
            items: [
                { path: '/strategy', label: '策略管理', subtitle: 'Strategy', number: 'Ⅰ' },
                { path: '/backtest', label: '回测分析', subtitle: 'Backtest', number: 'Ⅱ' },
                { path: '/strategy-lab', label: '策略实验室', subtitle: 'Strategy Lab', number: 'Ⅲ' },
                { path: '/backtest-arena', label: '回测竞技场', subtitle: 'Backtest Arena', number: 'Ⅳ' }
            ]
        },
        system: {
            title: 'SYSTEM MONITORING',
            icon: '◈',
            items: [
                { path: '/system/architecture', label: '系统架构', subtitle: 'Architecture', number: 'Ⅰ' },
                { path: '/system/database-monitor', label: '数据库监控', subtitle: 'Database', number: 'Ⅱ' },
                { path: '/settings', label: '系统设置', subtitle: 'Settings', number: 'Ⅲ' }
            ]
        }
    }

    // 计算属性
    const currentModuleConfig = computed(() => {
        return menuConfigs[activeModule.value] || menuConfigs.dashboard
    })

    const currentModuleTitle = computed(() => {
        return currentModuleConfig.value.title
    })

    const currentModuleIcon = computed(() => {
        return currentModuleConfig.value.icon
    })

    const currentMenuItems = computed(() => {
        return currentModuleConfig.value.items
    })

    // 方法
    const switchModule = moduleKey => {
        activeModule.value = moduleKey
    }

    // 暴露组件方法
    defineExpose({
        switchModule,
        activeModule
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    //   DYNAMIC SIDEBAR CONTAINER
    // ============================================
    .artdeco-dynamic-sidebar {
        width: 320px;
        background: var(--artdeco-bg-header);
        border-right: 2px solid var(--artdeco-gold-dim);
        position: fixed;
        height: 100vh;
        overflow-y: auto;
        overflow-x: hidden;
        z-index: var(--artdeco-z-fixed);
        transition: transform var(--artdeco-transition-slow);
    }

    // Decorative background pattern
    .artdeco-sidebar-pattern {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(212, 175, 55, 0.02) 10px,
            rgba(212, 175, 55, 0.02) 20px
        );
        pointer-events: none;
        z-index: 0;
    }

    // ============================================
    //   HEADER SECTION
    // ============================================
    .artdeco-sidebar-header {
        padding: var(--artdeco-spacing-5) var(--artdeco-spacing-4);
        border-bottom: 2px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        position: relative;
        background: var(--artdeco-bg-header);
        z-index: 1;
    }

    // Decorative corner ornaments
    .artdeco-corner-tl,
    .artdeco-corner-tr {
        position: absolute;
        width: 30px;
        height: 30px;
        border: 2px solid rgba(212, 175, 55, 0.2);
        pointer-events: none;
    }

    .artdeco-corner-tl {
        top: 10px;
        left: 10px;
        border-right: none;
        border-bottom: none;
    }

    .artdeco-corner-tr {
        top: 10px;
        right: 10px;
        border-left: none;
        border-bottom: none;
    }

    // Logo with frame
    .artdeco-logo {
        display: inline-block;
        text-decoration: none;
        position: relative;
        z-index: 1;
        margin-top: var(--artdeco-spacing-2);
    }

    .artdeco-logo-frame {
        border: 2px solid var(--artdeco-accent-gold);
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
        transition: all var(--artdeco-transition-slow);
    }

    .artdeco-logo:hover .artdeco-logo-frame {
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
        transform: scale(1.02);
    }

    .artdeco-logo-text {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-base);
        font-weight: 700;
        color: var(--artdeco-accent-gold);
        letter-spacing: 0.25em;
        text-transform: uppercase;
        display: block;
        margin-bottom: 4px;
        transition: color var(--artdeco-transition-slow);
        line-height: 1.2;
    }

    .artdeco-logo:hover .artdeco-logo-text {
        color: var(--artdeco-accent-gold);
    }

    .artdeco-logo-subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        font-weight: 500;
        color: var(--artdeco-fg-muted);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        display: block;
    }

    // Decorative divider with ornament
    .artdeco-header-divider {
        height: 1px;
        background: linear-gradient(
            to right,
            transparent,
            var(--artdeco-accent-gold) 40%,
            var(--artdeco-accent-gold) 60%,
            transparent
        );
        margin: var(--artdeco-spacing-3) auto 0;
        position: relative;
        opacity: 0.6;
    }

    .artdeco-divider-ornament {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 8px;
        height: 8px;
        background: var(--artdeco-accent-gold);
        transform: translate(-50%, -50%) rotate(45deg);
        box-shadow: 0 0 8px var(--artdeco-accent-gold);
    }

    // ============================================
    //   MODULE TABS
    // ============================================
    .artdeco-module-tabs {
        padding: 0 var(--artdeco-spacing-4) var(--artdeco-spacing-2);
        position: relative;
        z-index: 1;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    }

    .module-tab {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--artdeco-spacing-2);
        width: 100%;
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-1);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--artdeco-radius-none);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        cursor: pointer;
        transition: all var(--artdeco-transition-base);

        &:hover {
            border-color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-subtle);
        }

        &.active {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.1), rgba(212, 175, 55, 0.05));
            border-color: var(--artdeco-gold-primary);
            color: var(--artdeco-gold-primary);
            box-shadow: var(--artdeco-glow-medium);
        }

        .module-icon {
            font-size: var(--artdeco-text-base);
        }

        .module-label {
            font-size: var(--artdeco-text-sm);
        }
    }

    // ============================================
    //   NAVIGATION MENU
    // ============================================
    .artdeco-nav {
        padding: var(--artdeco-spacing-4);
        position: relative;
        z-index: 1;
    }

    // Navigation Section
    .artdeco-nav-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    // Section Header with Icon
    .artdeco-nav-section-header {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        margin-bottom: var(--artdeco-spacing-3);
        padding-bottom: var(--artdeco-spacing-2);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .artdeco-nav-section-icon {
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-accent-gold);
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
    }

    .artdeco-nav-section-title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-accent-gold);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        flex: 1;
        opacity: 0.8;
    }

    .artdeco-nav-section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, rgba(212, 175, 55, 0.2), transparent);
    }

    // Navigation Item
    .artdeco-nav-item {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        padding: 16px var(--artdeco-spacing-3);
        color: var(--artdeco-fg-primary);
        text-decoration: none;
        border-left: 3px solid transparent;
        background: transparent;
        transition: all var(--artdeco-transition-slow);
        margin-bottom: var(--artdeco-spacing-2);
        position: relative;
        overflow: hidden;
        min-height: 60px;
    }

    .artdeco-nav-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.05));
        transition: width var(--artdeco-transition-slow);
    }

    .artdeco-nav-number {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-md);
        font-weight: 700;
        color: rgba(212, 175, 55, 0.2);
        min-width: 32px;
        text-align: center;
        transition: all var(--artdeco-transition-slow);
    }

    .artdeco-nav-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .artdeco-nav-label {
        font-family: var(--artdeco-font-body);
        font-weight: 600;
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-fg-primary);
        letter-spacing: 0.05em;
        transition: all var(--artdeco-transition-slow);
        line-height: 1.3;
    }

    .artdeco-nav-subtitle {
        font-family: var(--artdeco-font-body);
        font-weight: 400;
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all var(--artdeco-transition-slow);
        line-height: 1.2;
    }

    // Hover State
    .artdeco-nav-item:hover {
        background: rgba(212, 175, 55, 0.08);
        border-left-color: var(--artdeco-accent-gold);
        padding-left: calc(var(--artdeco-spacing-3) + 4px);
    }

    .artdeco-nav-item:hover::before {
        width: 100%;
    }

    .artdeco-nav-item:hover .artdeco-nav-number {
        color: var(--artdeco-accent-gold);
        transform: scale(1.1);
        text-shadow: 0 0 12px rgba(212, 175, 55, 0.5);
    }

    .artdeco-nav-item:hover .artdeco-nav-label {
        color: var(--artdeco-accent-gold);
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.2);
    }

    .artdeco-nav-item:hover .artdeco-nav-subtitle {
        color: var(--artdeco-fg-primary);
    }

    // Active State
    .artdeco-nav-item.active {
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.08));
        border-left-color: var(--artdeco-accent-gold);
        border-left-width: 4px;
        box-shadow: inset 0 0 30px rgba(212, 175, 55, 0.15);
    }

    .artdeco-nav-item.active .artdeco-nav-number {
        color: var(--artdeco-accent-gold);
        text-shadow: var(--artdeco-glow-subtle);
        transform: scale(1.15);
    }

    .artdeco-nav-item.active .artdeco-nav-label {
        color: var(--artdeco-accent-gold);
        font-weight: 700;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }

    .artdeco-nav-item.active .artdeco-nav-subtitle {
        color: var(--artdeco-fg-secondary);
    }

    // ============================================
    //   FOOTER SECTION
    // ============================================
    .artdeco-sidebar-footer {
        padding: var(--artdeco-spacing-4);
        text-align: center;
        border-top: 1px solid rgba(212, 175, 55, 0.2);
        background: var(--artdeco-bg-header);
        position: relative;
        z-index: 1;
    }

    .artdeco-footer-ornament {
        font-size: var(--artdeco-text-lg);
        color: rgba(212, 175, 55, 0.2);
        margin-bottom: var(--artdeco-spacing-1);
        text-shadow: 0 0 8px rgba(212, 175, 55, 0.2);
    }

    .artdeco-footer-text {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    // ============================================
    //   ANIMATIONS
    // ============================================
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }

    // ============================================
    //   RESPONSIVE DESIGN
    // ============================================
    @media (max-width: 1400px) {
        .artdeco-dynamic-sidebar {
            width: 280px;
        }

        .artdeco-nav-label {
            font-size: var(--artdeco-text-sm);
        }

        .artdeco-nav-subtitle {
            font-size: var(--artdeco-text-xs);
        }
    }

    @media (max-width: 1024px) {
        .artdeco-dynamic-sidebar {
            width: 260px;
        }

        .module-label {
            display: none;
        }

        .module-tab {
            justify-content: center;
            padding: var(--artdeco-spacing-2);
        }
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
