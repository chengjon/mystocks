<template>
    <div class="artdeco-data-analysis">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">数据分析中心</h1>
                <p class="page-subtitle">技术指标分析 · 智能选股 · 自定义指标</p>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
                <ArtDecoButton variant="solid" @click="runScreening">执行筛选</ArtDecoButton>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview">
            <ArtDecoStatCard
                label="可用指标"
                :value="stats.availableIndicators"
                variant="gold"
            />
            <ArtDecoStatCard
                label="自定义指标"
                :value="stats.customIndicators"
                variant="gold"
            />
            <ArtDecoStatCard
                label="筛选股票数"
                :value="stats.screenedStocks"
                variant="rise"
            />
            <ArtDecoStatCard
                label="今日筛选次数"
                :value="stats.screeningTimes"
                variant="gold"
            />
            <ArtDecoStatCard
                label="符合条件"
                :value="stats.qualifiedStocks"
                :variant="stats.qualifiedChange >= 0 ? 'rise' : 'fall'"
            />
        </div>

        <!-- Main Tabs -->
        <nav class="main-tabs">
            <button
                v-for="tab in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
            <div v-if="loading" class="loading-overlay">
                <div class="spinner"></div>
                <p>处理中...</p>
            </div>

            <template v-else>
                <!-- 指标库 -->
                <AnalysisIndicators
                    v-if="activeTab === 'indicators'"
                    :categories="indicatorCategories"
                    :indicators="filteredIndicators"
                    v-model:activeCategory="activeCategory"
                    :getCount="getCategoryCount"
                    @select="selectIndicator"
                />

                <!-- 选股器 -->
                <AnalysisScreener
                    v-if="activeTab === 'screener'"
                    :filters="screeningFilters"
                    :availableIndicators="availableIndicatorsForFilter"
                    :operators="operatorOptions"
                    @add-indicator="addIndicatorFilter"
                    @remove-indicator="removeIndicatorFilter"
                    @reset="resetFilters"
                    @run="runScreening"
                />

                <!-- 结果 -->
                <AnalysisResults
                    v-if="activeTab === 'results'"
                    :columns="resultColumns"
                    :data="screeningResults"
                    @row-click="handleRowClick"
                />

                <!-- 编辑器 (Placeholder) -->
                <ArtDecoCard v-if="activeTab === 'editor'" title="指标编辑器">
                    <div class="editor-placeholder">编辑器模块正在优化中...</div>
                </ArtDecoCard>
            </template>
        </div>
    </div>
</template>

<script setup>
import { 
    ArtDecoStatCard, ArtDecoButton, ArtDecoCard 
} from '@/components/artdeco'
import { useDataAnalysis } from '@/composables/market/useDataAnalysis'

// Components
import AnalysisIndicators from './components/AnalysisIndicators.vue'
import AnalysisScreener from './components/AnalysisScreener.vue'
import AnalysisResults from './components/AnalysisResults.vue'

const {
    activeTab, activeCategory, loading, stats,
    indicatorCategories, filteredIndicators,
    screeningFilters, screeningResults,
    switchTab, refreshData, runScreening, resetFilters
} = useDataAnalysis()

const mainTabs = [
    { key: 'indicators', label: '指标库', icon: '📊' },
    { key: 'editor', label: '指标编辑器', icon: '✏️' },
    { key: 'screener', label: '智能选股', icon: '🔍' },
    { key: 'results', label: '筛选结果', icon: '📈' }
]

const operatorOptions = [
    { label: '大于', value: '>' },
    { label: '小于', value: '<' },
    { label: '等于', value: '=' },
    { label: '金叉', value: 'golden_cross' },
    { label: '死叉', value: 'death_cross' }
]

const availableIndicatorsForFilter = [
    { label: 'MA5', value: 'ma5' },
    { label: 'RSI', value: 'rsi' },
    { label: 'MACD', value: 'macd' }
]

const resultColumns = [
    { key: 'symbol', label: '代码' },
    { key: 'name', label: '名称' },
    { key: 'price', label: '最新价' },
    { key: 'change', label: '涨跌幅' }
]

function getCategoryCount(key) {
    return 5 // Simplified
}

function selectIndicator(ind) {
    console.log('Selected:', ind.name)
}

function addIndicatorFilter() {
    screeningFilters.value.indicators.push({ indicator: '', operator: '>', value: 0 })
}

function removeIndicatorFilter(index) {
    screeningFilters.value.indicators.splice(index, 1)
}

function handleRowClick(row) {
    console.log('Clicked:', row.symbol)
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-data-analysis {
    padding: 20px;
    background: var(--artdeco-bg-global);
    min-height: 100vh;
}

.page-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
}

.stats-overview {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.main-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
}

.main-tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: transparent;
    border: none;
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    &.active {
        color: var(--artdeco-gold-primary);
        border-bottom: 2px solid var(--artdeco-gold-primary);
    }
}

.loading-overlay {
    text-align: center;
    padding: 100px;
}

.editor-placeholder {
    padding: 50px;
    text-align: center;
    color: var(--artdeco-fg-muted);
}
</style>