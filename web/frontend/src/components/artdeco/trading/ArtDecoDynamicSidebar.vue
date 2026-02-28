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
                v-for="(module, _idx) in modules"
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
                    v-for="(item, _idx) in currentMenuItems"
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
@import "./styles/ArtDecoDynamicSidebar";
</style>
