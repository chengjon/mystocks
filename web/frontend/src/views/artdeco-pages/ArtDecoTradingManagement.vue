<template>
    <div class="artdeco-trading-management">
        <section class="hero-shell artdeco-card-shell">
            <div class="hero-rail">
                <div class="hero-copy">
                    <span class="hero-eyebrow">execution command stage</span>
                    <div class="hero-meta">
                        <span>REQ_ID: {{ requestTraceId }}</span>
                        <span>SYNC: {{ syncLabel }}</span>
                        <span>FOCUS: {{ activeTabMeta.label }}</span>
                    </div>
                </div>
            </div>

            <ArtDecoHeader
                title="量化交易管理中心"
                subtitle="智能交易执行、风险控制与订单管理"
                :show-status="true"
                :status-text="connectionStatus"
                :status-type="connectionStatusType"
            >
                <template #actions>
                    <ArtDecoButton variant="outline" size="sm" @click="refreshData" :loading="refreshing">
                        <template #icon>
                            <ArtDecoIcon name="refresh" />
                        </template>
                        刷新数据
                    </ArtDecoButton>

                    <ArtDecoButton variant="default" size="sm" @click="openSettings">
                        <template #icon>
                            <ArtDecoIcon name="settings" />
                        </template>
                        系统设置
                    </ArtDecoButton>
                </template>
            </ArtDecoHeader>
        </section>

        <section class="stats-strip artdeco-card-shell">
            <ArtDecoStatCard
                label="市场状态"
                :value="marketStatus"
                :trend="marketTrend"
                :variant="marketStatusColor"
            />
            <ArtDecoStatCard
                label="活跃信号"
                :value="activeSignalsCount"
                :variant="'gold'"
            />
            <ArtDecoStatCard
                label="今日盈亏"
                :value="todayPnL"
                :trend="todayPnLTrend"
                :variant="todayPnLColor"
            />
            <ArtDecoStatCard
                label="当前焦点"
                :value="activeTabMeta.label"
                :variant="'gold'"
            />
        </section>

        <section class="tabs-shell artdeco-card-shell">
            <div class="tabs-shell-header">
                <div class="tabs-shell-copy">
                    <span class="tabs-shell-eyebrow">trading route</span>
                    <h2 class="tabs-shell-title">交易执行工作流</h2>
                    <p class="tabs-shell-subtitle">{{ activeTabMeta.description }}</p>
                </div>
                <div class="tabs-shell-trace">
                    <span>TABS: {{ mainTabs.length }}</span>
                    <span>STATUS: {{ connectionStatus }}</span>
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
                    <span>MODE: {{ syncLabel }}</span>
                    <span>SIGNALS: {{ activeSignalsCount }}</span>
                </div>
            </div>

            <div class="trading-management-content">
            <!-- 核心功能区域 -->
            <div class="tab-content">
                <!-- 交易概览 -->
                <div v-if="activeTab === 'overview'" class="tab-panel overview-panel">
                    <div class="artdeco-content-grid">
                        <ArtDecoCard class="overview-card">
                            <template #header>
                                <div class="card-header">
                                    <ArtDecoIcon name="bar-chart" />
                                    <h3>交易概览</h3>
                                </div>
                            </template>
                            <ArtDecoTradingStats :stats="tradingStats" />
                        </ArtDecoCard>

                        <ArtDecoCard class="attribution-card" variant="elevated" gradient>
                            <template #header>
                                <div class="card-header">
                                    <ArtDecoIcon name="pie-chart" />
                                    <h3>收益归因分析</h3>
                                </div>
                            </template>
                            <div class="attribution-content">
                                <ArtDecoAttributionAnalysis
                                    :strategy-breakdown="strategyBreakdown"
                                    :stock-breakdown="stockBreakdown"
                                    :loading="attributionLoading"
                                />
                            </div>
                        </ArtDecoCard>
                    </div>
                </div>

                <!-- 交易信号 -->
                <div v-if="activeTab === 'signals'" class="tab-panel">
                    <ArtDecoCard class="controls-card" variant="bordered">
                        <template #header>
                            <div class="card-header">
                                <ArtDecoIcon name="sliders" />
                                <h3>信号过滤</h3>
                            </div>
                        </template>
                        <ArtDecoTradingSignalsControls
                            :signal-filters="signalFilters"
                            :active-signal-filter="activeSignalFilter"
                            @export-csv="handleExportCsv"
                            @batch-execute="handleBatchExecute"
                        />
                    </ArtDecoCard>

                    <ArtDecoCard class="realtime-panel" gradient>
                        <template #header>
                            <div class="card-header dramatic">
                                <div class="header-icon">
                                    <ArtDecoIcon name="zap" />
                                </div>
                                <div class="header-content">
                                    <h3>实时信号</h3>
                                    <p>基于策略生成的最新交易机会</p>
                                </div>
                            </div>
                        </template>
                        <ArtDecoTradingSignals
                            :data="tradingSignals"
                            @execute-signal="handleExecuteSignal"
                            @cancel-signal="handleCancelSignal"
                        />
                    </ArtDecoCard>
                </div>

                <!-- 持仓监控 -->
                <div v-if="activeTab === 'positions'" class="tab-panel">
                    <ArtDecoCard class="realtime-panel" gradient>
                        <template #header>
                            <div class="card-header dramatic">
                                <div class="header-icon">
                                    <ArtDecoIcon name="briefcase" />
                                </div>
                                <div class="header-content">
                                    <h3>活跃持仓</h3>
                                    <p>实时持仓盈亏与仓位分配</p>
                                </div>
                            </div>
                        </template>
                        <ArtDecoTradingPositions
                            :positions="activePositions"
                            @close-position="handleClosePosition"
                            @adjust-position="handleAdjustPosition"
                        />
                    </ArtDecoCard>
                </div>

                <!-- 交易历史 -->
                <div v-if="activeTab === 'history'" class="tab-panel">
                    <ArtDecoCard class="history-panel" variant="bordered">
                        <template #header>
                            <div class="card-header elegant">
                                <div class="header-icon">
                                    <ArtDecoIcon name="clock" />
                                </div>
                                <div class="header-content">
                                    <h3>历史分析</h3>
                                    <p>交易历史查询与分析</p>
                                </div>
                            </div>
                        </template>

                        <div class="history-controls">
                            <ArtDecoTradingHistoryControls
                                :symbol-options="symbolOptions"
                                :trade-type-options="tradeTypeOptions"
                                :start-date="startDate"
                                :end-date="endDate"
                                :selected-symbol="selectedSymbol"
                                :selected-type="selectedType"
                                @update:start-date="startDate = $event"
                                @update:end-date="endDate = $event"
                                @update:symbol="selectedSymbol = String($event)"
                                @update:type="selectedType = String($event)"
                                @search="handleHistoryFilter"
                            />
                        </div>

                        <div class="history-data">
                            <ArtDecoTradingHistory
                                :history="tradingHistory"
                                :loading="historyLoading"
                                @load-more="handleLoadMoreHistory"
                            />
                        </div>
                    </ArtDecoCard>
                </div>

                <!-- 绩效分析 -->
                <div v-if="activeTab === 'attribution'" class="tab-panel">
                    <ArtDecoCard class="attribution-card" variant="elevated" gradient>
                        <template #header>
                            <div class="card-header">
                                <ArtDecoIcon name="pie-chart" />
                                <h3>绩效归因</h3>
                            </div>
                        </template>

                        <div class="attribution-content">
                            <ArtDecoAttributionControls
                                :date-range="attributionDateRange"
                                :portfolio="selectedPortfolio"
                                @update:date-range="attributionDateRange = $event"
                                @update:portfolio="selectedPortfolio = $event"
                                @analyze="handleAttributionAnalysis"
                            />

                            <div class="attribution-results">
                                <ArtDecoAttributionAnalysis
                                    :strategy-breakdown="strategyBreakdown"
                                    :stock-breakdown="stockBreakdown"
                                    :loading="attributionLoading"
                                />
                            </div>
                        </div>
                    </ArtDecoCard>
                </div>
            </div>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import { useArtDecoTradingManagement } from './composables/useArtDecoTradingManagement'

const { _router, activeTab, mainTabs, switchTab, tradingStats, signalFilters, activeSignalFilter, symbolOptions, tradeTypeOptions, startDate, endDate, selectedSymbol, selectedType, connectionStatus, connectionStatusType, marketStatus, marketTrend, marketStatusColor, activeSignalsCount, todayPnL, todayPnLTrend, todayPnLColor, refreshing, attributionDateRange, selectedPortfolio, attributionLoading, strategyBreakdown, stockBreakdown, activePositions, tradingSignals, tradingHistory, historyLoading, handleExportCsv, handleBatchExecute, refreshData, openSettings, handleClosePosition, handleAdjustPosition, handleExecuteSignal, handleCancelSignal, handleHistoryFilter, handleLoadMoreHistory, handleAttributionAnalysis } = useArtDecoTradingManagement()

const activeTabMeta = computed(() => {
    const tabs = mainTabs.value as Array<Record<string, string>>
    return tabs.find((tab) => tab.key === activeTab.value) || tabs[0] || {
        key: 'overview',
        label: '交易概览',
        eyebrow: 'command summary',
        description: '汇总市场状态、信号活跃度与收益归因的总览面板。'
    }
})
const requestTraceId = computed(() => 'N/A')
const syncLabel = computed(() => refreshing.value ? '同步中' : '实时工作流')
</script>

<style scoped lang="scss">
@import "./styles/ArtDecoTradingManagement";
</style>
