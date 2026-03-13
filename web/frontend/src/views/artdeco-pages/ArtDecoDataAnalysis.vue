<template>
    <div class="artdeco-data-analysis">
        <!-- Page Header -->
        <div class="page-header artdeco-card-shell">
            <div class="header-content">
                <div class="eyebrow">analysis workstation</div>
                <h1 class="page-title">数据分析中心</h1>
                <p class="page-subtitle">技术指标分析 · 智能选股 · 自定义指标</p>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" @click="refreshData">刷新数据</ArtDecoButton>
                <ArtDecoButton variant="solid" @click="runScreening">执行筛选</ArtDecoButton>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview artdeco-card-shell">
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
        <nav class="main-tabs artdeco-card-shell">
            <button
                v-for="(tab, _idx) in mainTabs"
                :key="tab.key"
                class="main-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <div class="analysis-blocker artdeco-card-shell">
            <strong>指标接口真值待确认</strong>
            <span>本页当前优先保证路由壳层、编辑器占位和筛选流程可见；真实指标接口待 API 分支复核后再接入。</span>
        </div>

        <!-- Tab Content -->
        <div class="tab-content artdeco-card-shell">
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
                <ArtDecoCard v-if="activeTab === 'editor'" title="指标编辑器" class="editor-card">
                    <div class="editor-placeholder">
                        <div class="placeholder-title">公式编辑器升级中</div>
                        <p class="placeholder-desc">正在整合可视化表达式构建、回测联动与指标发布流程。</p>
                        <ul class="placeholder-list">
                            <li>支持拖拽组合基础指标与自定义变量</li>
                            <li>提供公式语法提示与实时计算预览</li>
                            <li>一键发布至智能选股与策略回测模块</li>
                        </ul>
                    </div>
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

function getCategoryCount(_key) {
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
@import '@/styles/artdeco-tokens';

.artdeco-data-analysis {
    padding: var(--artdeco-spacing-6);
    background: var(--artdeco-bg-global);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-5);
}

.artdeco-card-shell {
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), color-mix(in srgb, var(--artdeco-bg-global) 92%, transparent));
    box-shadow: inset 0 1px 0 color-mix(in srgb, var(--artdeco-fg-primary) 3%, transparent), 0 8px 24px color-mix(in srgb, var(--artdeco-bg-global) 82%, transparent);
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--artdeco-spacing-4);
    padding: var(--artdeco-spacing-5);
}

.header-content {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-2);
}

.eyebrow {
    font-size: var(--artdeco-text-xs);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
}

.page-title {
    margin: 0;
    font-size: var(--artdeco-text-3xl);
    color: var(--artdeco-gold-primary);
    letter-spacing: var(--artdeco-tracking-wide);
}

.page-subtitle {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-3);
}

.stats-overview {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: var(--artdeco-spacing-3);
    padding: var(--artdeco-spacing-4);
}

.main-tabs {
    display: flex;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-2);
}

.analysis-blocker {
    display: grid;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);

    strong {
        font-family: var(--font-display);
        letter-spacing: var(--artdeco-tracking-wide);
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
    }

    span {
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-sm);
    }
}

.main-tab {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    background: transparent;
    border: 1px solid transparent;
    color: var(--artdeco-fg-primary);
    cursor: pointer;
    transition: border-color var(--artdeco-transition-base), background-color var(--artdeco-transition-base), color var(--artdeco-transition-base), box-shadow var(--artdeco-transition-base);

    .tab-icon {
        opacity: 80%;
    }

    &:hover {
        color: var(--artdeco-gold-light);
        border-color: var(--artdeco-gold-opacity-20);
        background: var(--artdeco-gold-opacity-05);
    }

    &:focus-visible {
        outline: none;
        border-color: var(--artdeco-border-hover);
        box-shadow: 0 0 0 1px var(--artdeco-border-hover);
    }

    &.active {
        color: var(--artdeco-gold-primary);
        border-color: var(--artdeco-border-accent);
        background: var(--artdeco-gold-opacity-08);
        box-shadow: inset 0 calc(var(--artdeco-spacing-px) * -2) 0 var(--artdeco-gold-primary);

        .tab-icon {
            opacity: 100%;
        }
    }
}

.tab-content {
    min-height: calc(var(--artdeco-spacing-px) * 520);
    padding: var(--artdeco-spacing-5);
    position: relative;
}

.loading-overlay {
    min-height: calc(var(--artdeco-spacing-px) * 380);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--artdeco-spacing-3);
    color: var(--artdeco-fg-muted);

    .spinner {
        width: var(--artdeco-text-3xl);
        height: var(--artdeco-text-3xl);
        border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-opacity-20);
        border-top-color: var(--artdeco-gold-primary);
        border-radius: 50%;
        animation: spin var(--artdeco-transition-dramatic) linear infinite;
    }
}

.editor-card {
    background: transparent;
}

.editor-placeholder {
    padding: var(--artdeco-spacing-6);
    border: 1px dashed var(--artdeco-border-accent);
    background: var(--artdeco-gold-opacity-05);

    .placeholder-title {
        font-size: var(--artdeco-text-xl);
        color: var(--artdeco-gold-primary);
        margin-bottom: var(--artdeco-spacing-2);
    }

    .placeholder-desc {
        margin: 0 0 var(--artdeco-spacing-4);
        color: var(--artdeco-fg-muted);
    }

    .placeholder-list {
        margin: 0;
        padding-left: var(--artdeco-spacing-5);
        color: var(--artdeco-fg-primary);
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);
    }
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

</style>
