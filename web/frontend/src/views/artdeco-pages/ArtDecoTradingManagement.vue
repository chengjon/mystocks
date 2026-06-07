<template>
    <div class="artdeco-trading-management">
        <section class="hero-shell artdeco-card-shell">
            <div class="hero-rail">
                <div class="hero-copy">
                    <span class="hero-eyebrow">execution command stage</span>
                    <div class="hero-meta">
                        <span>FOCUS: {{ activeTabMeta.label }}</span>
                        <span>SOURCE: {{ activeTruthSourceLabel }}</span>
                    </div>
                </div>
            </div>

            <ArtDecoHeader
                title="量化交易管理中心"
                subtitle="仅做交易域编排与 canonical 路由入口，不维护独立实况快照。"
            >
                <template #actions>
                    <ArtDecoButton variant="outline" priority="ghost" motion="data" size="sm" @click="openSettings">
                        <template #icon>
                            <ArtDecoIcon name="settings" />
                        </template>
                        系统设置
                    </ArtDecoButton>
                </template>
            </ArtDecoHeader>
        </section>

        <section class="tabs-shell artdeco-card-shell">
            <div class="tabs-shell-header">
                <div class="tabs-shell-copy">
                    <span class="tabs-shell-eyebrow">trading route</span>
                    <h2 class="tabs-shell-title">交易执行工作流</h2>
                    <p class="tabs-shell-subtitle">
                        所有可复用实况均来自对应 canonical /trade/* 页面；当前壳层仅保留导航和静态说明，不声明独立实况。
                    </p>
                </div>
                <div class="tabs-shell-trace">
                    <span>TABS: {{ mainTabs.length }}</span>
                    <span>SHELL: CANONICAL ONLY</span>
                </div>
            </div>

            <nav class="main-tabs">
                <button
                    v-for="(tab, _idx) in mainTabs"
                    :key="'key' in tab ? tab.key : tab.id"
                    class="main-tab"
                    :class="{ active: activeTab === ('key' in tab ? tab.key : tab.id) }"
                    @click="switchTab('key' in tab ? tab.key : tab.id)"
                >
                    <ArtDecoIcon v-if="'icon' in tab && tab.icon" :name="tab.icon" size="sm" class="tab-icon" />
                    <span class="tab-label">{{ 'label' in tab ? tab.label : '' }}</span>
                </button>
            </nav>
        </section>

        <section class="content-shell artdeco-card-shell">
            <div class="content-shell-header">
                <div class="content-shell-copy">
                    <span class="content-shell-kicker">{{ activeTabMeta.eyebrow }}</span>
                    <h3 class="content-shell-title">{{ activeTabMeta.label }}</h3>
                </div>
                <div class="content-shell-meta">
                    <span>TRUTH: {{ activeTruthLabel }}</span>
                    <span>MODE: {{ activeTabModeLabel }}</span>
                </div>
            </div>

            <div class="trading-management-content">
                <TradePortfolioPage
                    v-if="activeTab === 'overview'"
                    function-key="trade-portfolio-shell"
                />

                <TradeSignalsPage
                    v-else-if="activeTab === 'signals'"
                    function-key="trade-signals-shell"
                />

                <TradeCenterPage
                    v-else-if="activeTab === 'positions'"
                    :positions="[]"
                />

                <TradeHistoryPage
                    v-else-if="activeTab === 'history'"
                    :history="[]"
                />

                <ArtDecoCard v-else class="static-shell-card" variant="bordered">
                    <template #header>
                        <div class="card-header elegant">
                            <div class="header-icon">
                                <ArtDecoIcon name="pie-chart" />
                            </div>
                            <div class="header-content">
                                <h3>绩效归因</h3>
                                <p>当前壳层不维护独立绩效归因实况。</p>
                            </div>
                        </div>
                    </template>

                    <div class="static-shell-message">
                        <p>请前往 canonical /trade/portfolio 查看已验证组合资产与归因能力。</p>
                        <ArtDecoButton variant="solid" priority="primary" motion="data" size="sm" @click="switchTab('overview')">
                            前往组合资产工作台
                        </ArtDecoButton>
                    </div>
                </ArtDecoCard>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import { useArtDecoTradingManagement } from './composables/useArtDecoTradingManagement'
    import TradePortfolioPage from '@/views/trade/Portfolio.vue'
    import TradeSignalsPage from '@/views/trade/Signals.vue'
    import TradeCenterPage from '@/views/trade/Center.vue'
    import TradeHistoryPage from '@/views/trade/History.vue'

    const { activeTab, mainTabs, switchTab, openSettings } = useArtDecoTradingManagement()

    const activeTabMeta = computed(() => {
        const tabs = mainTabs.value as Array<Record<string, string>>
        return tabs.find((tab) => tab.key === activeTab.value) || tabs[0] || {
            key: 'overview',
            label: '交易概览',
            eyebrow: 'command summary',
            description: '汇总组合资产与归因能力的 canonical 入口。',
        }
    })

    const activeTruthLabel = computed(() => {
        if (activeTab.value === 'overview') return '/trade/portfolio'
        if (activeTab.value === 'signals') return '/trade/signals'
        if (activeTab.value === 'positions') return '/trade/positions'
        if (activeTab.value === 'history') return '/trade/history'
        return 'static shell'
    })

    const activeTruthSourceLabel = computed(() => {
        if (activeTab.value === 'attribution') return 'STATIC SHELL'
        return 'CANONICAL /trade/*'
    })

    const activeTabModeLabel = computed(() => {
        if (activeTab.value === 'attribution') return 'STATIC'
        return 'EMBEDDED'
    })
</script>

<style scoped lang="scss">
@import "./styles/ArtDecoTradingManagement";

.static-shell-card {
    min-height: 12rem;
}

.static-shell-message {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-muted);
}
</style>
