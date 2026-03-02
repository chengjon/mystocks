<template>
    <div class="artdeco-trading-management">
        <!-- ArtDeco 页面头部 -->
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

        <!-- Main Tabs -->
        <nav class="main-tabs">
            <button
                v-for="(tab, _idx) in mainTabs"
                :key="'key' in tab ? tab.key : tab.id"
                class="main-tab"
                :class="{ active: activeTab === ('key' in tab ? tab.key : tab.id) }"
                @click="switchTab('key' in tab ? tab.key : tab.id)"
            >
                <span class="tab-icon">{{ 'icon' in tab ? tab.icon : '' }}</span>
                <span class="tab-label">{{ 'label' in tab ? tab.label : '' }}</span>
            </button>
        </nav>

        <!-- 主内容区域 -->
        <div class="trading-management-content">
            <!-- 实时状态栏 - 仅在概览显示 -->
            <div v-if="activeTab === 'overview'" class="status-bar">
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
            </div>

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
    </div>
</template>

<script setup lang="ts">
    import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import { useArtDecoTradingManagement } from './composables/useArtDecoTradingManagement'

const { route, _router, currentRouteName, currentPageConfig, isMonolithic, activeTab, mainTabs, currentTabConfig, apiEndpoint, switchTab, tradingStats, signalFilters, activeSignalFilter, symbolOptions, tradeTypeOptions, startDate, endDate, selectedSymbol, selectedType, connectionStatus, connectionStatusType, marketStatus, marketTrend, marketStatusColor, activeSignalsCount, todayPnL, todayPnLTrend, todayPnLColor, refreshing, attributionDateRange, selectedPortfolio, attributionLoading, strategyBreakdown, stockBreakdown, activePositions, tradingSignals, tradingHistory, historyLoading, handleExportCsv, handleBatchExecute, refreshData, openSettings, handleClosePosition, handleAdjustPosition, handleExecuteSignal, handleCancelSignal, handleHistoryFilter, handleLoadMoreHistory, handleAttributionAnalysis } = useArtDecoTradingManagement()
</script>

<style scoped lang="scss">
@import "./styles/ArtDecoTradingManagement";
</style>
