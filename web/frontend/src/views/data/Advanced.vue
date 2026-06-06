<template>
    <div class="artdeco-data-analysis">
        <div class="page-header artdeco-card-shell">
            <div class="header-content">
                <div class="eyebrow">analysis workstation</div>
                <h1 class="page-title">数据分析中心</h1>
                <p class="page-subtitle">技术指标分析 · 智能选股 · 指标详情</p>
                <div class="header-meta">
                    <span>STATUS: {{ pageStatusText }}</span>
                    <span>UPDATED: {{ displayLastUpdateTime }}</span>
                </div>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" @click="handleRefresh">刷新数据</ArtDecoButton>
                <ArtDecoButton variant="solid" :disabled="loading" @click="handleRunScreening">执行筛选</ArtDecoButton>
            </div>
        </div>

        <div class="stats-overview artdeco-card-shell">
            <ArtDecoStatCard
                label="可用指标"
                :value="displayAvailableIndicators"
                :show-change="false"
                variant="gold"
            />
            <ArtDecoStatCard
                label="当前分类指标"
                :value="displayVisibleIndicatorCount"
                :show-change="false"
                variant="gold"
            />
            <ArtDecoStatCard
                label="筛选股票数"
                :value="displayScreenedStocks"
                :show-change="false"
                variant="rise"
            />
            <ArtDecoStatCard
                label="今日筛选次数"
                :value="displayScreeningTimes"
                :show-change="false"
                variant="gold"
            />
            <ArtDecoStatCard
                label="符合条件"
                :value="displayQualifiedStocks"
                :show-change="false"
                :variant="showSummaryPlaceholders ? 'gold' : stats.qualifiedChange >= 0 ? 'rise' : 'fall'"
            />
        </div>

        <nav class="main-tabs artdeco-card-shell" role="tablist" aria-label="数据分析主标签">
            <button
                v-for="(tab, _idx) in mainTabs"
                :key="tab.key"
                type="button"
                class="main-tab"
                role="tab"
                :class="{ active: activeTab === tab.key }"
                :aria-selected="activeTab === tab.key ? 'true' : 'false'"
                :aria-controls="`data-analysis-panel-${tab.key}`"
                :tabindex="activeTab === tab.key ? 0 : -1"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <div class="tab-content artdeco-card-shell" :data-status="pageStatusType">
            <div v-if="loading" class="loading-overlay" role="status" aria-live="polite">
                <div class="spinner"></div>
                <p>{{ loadingMessage }}</p>
                <span class="loading-hint">{{ loadingHint }}</span>
            </div>

            <div v-else-if="showErrorState" class="state-panel artdeco-card" role="alert">
                <p>数据分析数据加载失败</p>
                <span>{{ error }}</span>
                <ArtDecoButton variant="outline" size="sm" @click="handleRefresh">重新加载</ArtDecoButton>
            </div>

            <template v-else>
                <div v-if="showRefreshWarning" class="state-panel warning-panel artdeco-card" role="status" aria-live="polite">
                    <p>部分刷新失败</p>
                    <span>{{ staleError }}</span>
                </div>

                <AnalysisIndicators
                    v-if="activeTab === 'indicators' && !showIndicatorsEmpty"
                    id="data-analysis-panel-indicators"
                    v-model:activeCategory="activeCategory"
                    :categories="indicatorCategories"
                    :getCount="getCategoryCount"
                    :indicators="filteredIndicators"
                    @select="selectIndicator"
                />

                <div v-if="showIndicatorsEmpty" class="state-panel artdeco-card" role="status" aria-live="polite">
                    <p>暂无指标数据</p>
                    <span>当前分类下暂无可展示指标，请刷新后重试。</span>
                </div>

                <AnalysisScreener
                    v-if="activeTab === 'screener'"
                    id="data-analysis-panel-screener"
                    :availableIndicators="availableIndicatorsForFilter"
                    :filters="screeningFilters"
                    :indicatorConditionsSupported="technicalIndicatorScreeningSupported"
                    :indicatorSupportMessage="technicalIndicatorSupportMessage"
                    :operators="operatorOptions"
                    @add-indicator="addIndicatorFilter"
                    @remove-indicator="removeIndicatorFilter"
                    @reset="resetFilters"
                    @run="runScreening"
                />

                <div v-if="activeTab === 'results' && selectedStock" class="context-panel artdeco-card">
                    <div class="context-eyebrow">selected stock</div>
                    <div class="context-grid">
                        <div>
                            <span class="context-label">名称</span>
                            <strong>{{ selectedStock.name }}</strong>
                        </div>
                        <div>
                            <span class="context-label">代码</span>
                            <strong>{{ selectedStock.symbol }}</strong>
                        </div>
                        <div>
                            <span class="context-label">最新价</span>
                            <strong>{{ selectedStock.price }}</strong>
                        </div>
                        <div>
                            <span class="context-label">涨跌幅</span>
                            <strong>{{ selectedStock.change }}</strong>
                        </div>
                    </div>
                </div>

                <div v-if="showResultsIdle" class="state-panel artdeco-card" role="status" aria-live="polite">
                    <p>尚未执行筛选</p>
                    <span>请先配置条件并执行筛选，结果面板会展示最新命中股票。</span>
                </div>

                <AnalysisResults
                    v-else-if="activeTab === 'results' && !showResultsEmpty"
                    id="data-analysis-panel-results"
                    :columns="resultColumns"
                    :data="screeningResults"
                    @row-click="handleRowClick"
                />

                <div v-if="showResultsEmpty" class="state-panel artdeco-card" role="status" aria-live="polite">
                    <p>暂无筛选结果</p>
                    <span>当前条件下没有命中股票，可调整条件后重新执行筛选。</span>
                </div>

                <ArtDecoCard v-if="activeTab === 'editor'" id="data-analysis-panel-editor" title="指标详情" class="editor-card">
                    <div v-if="selectedIndicator" class="detail-workspace">
                        <div class="context-panel inline-context">
                            <div class="context-eyebrow">selected indicator</div>
                            <div class="context-grid">
                                <div>
                                    <span class="context-label">名称</span>
                                    <strong>{{ selectedIndicator.name }}</strong>
                                </div>
                                <div>
                                    <span class="context-label">Key</span>
                                    <strong>{{ selectedIndicator.key.toUpperCase() }}</strong>
                                </div>
                                <div>
                                    <span class="context-label">分类</span>
                                    <strong>{{ selectedIndicator.categoryLabel }}</strong>
                                </div>
                                <div>
                                    <span class="context-label">类型</span>
                                    <strong>{{ selectedIndicator.type }}</strong>
                                </div>
                            </div>
                            <p class="context-description">{{ selectedIndicator.description }}</p>
                        </div>

                        <div class="detail-grid">
                            <div class="detail-card">
                                <span class="detail-label">参数</span>
                                <strong class="detail-value">{{ selectedIndicatorParamsLabel }}</strong>
                                <p class="detail-note">当前指标注册表声明的参数配置。</p>
                            </div>
                            <div class="detail-card">
                                <span class="detail-label">筛选接入</span>
                                <strong class="detail-value">{{ screeningCapabilityLabel }}</strong>
                                <p class="detail-note">{{ technicalIndicatorSupportMessage }}</p>
                            </div>
                            <div class="detail-card">
                                <span class="detail-label">当前分类指标数</span>
                                <strong class="detail-value">{{ getCategoryCount(selectedIndicator.category) }}</strong>
                                <p class="detail-note">用于对比同类趋势、动量或形态指标。</p>
                            </div>
                        </div>

                        <div class="detail-actions">
                            <ArtDecoButton variant="outline" size="sm" @click="switchTab('indicators')">返回指标库</ArtDecoButton>
                            <ArtDecoButton variant="solid" size="sm" @click="switchTab('screener')">查看筛选条件</ArtDecoButton>
                        </div>
                    </div>

                    <div v-else class="detail-empty-state">
                        <p>从指标库选择一个指标</p>
                        <span>选择后会在这里展示指标用途、参数和筛选接入状态。</span>
                        <ArtDecoButton variant="outline" size="sm" @click="switchTab('indicators')">打开指标库</ArtDecoButton>
                    </div>
                </ArtDecoCard>
            </template>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard } from '@/components/artdeco'
import { useDataAnalysis } from '@/composables/market/useDataAnalysis'
import AnalysisIndicators from '@/views/artdeco-pages/components/AnalysisIndicators.vue'
import AnalysisResults from '@/views/artdeco-pages/components/AnalysisResults.vue'
import AnalysisScreener from '@/views/artdeco-pages/components/AnalysisScreener.vue'

const {
    activeTab, activeCategory, loading, error, staleError, hasLoaded, hasExecutedScreening, lastUpdateTime, stats,
    technicalIndicatorScreeningSupported, technicalIndicatorSupportMessage,
    selectedIndicator, selectedStock,
    indicatorCategories, indicators, filteredIndicators,
    screeningFilters, screeningResults, availableIndicatorsForFilter,
    switchTab, refreshData, runScreening, resetFilters, setSelectedIndicator, setSelectedStock
} = useDataAnalysis()

const mainTabs = [
    { key: 'indicators', label: '指标库', icon: '📊' },
    { key: 'editor', label: '指标详情', icon: '📘' },
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

const resultColumns = [
    { key: 'symbol', label: '代码' },
    { key: 'name', label: '名称' },
    { key: 'price', label: '最新价' },
    { key: 'change', label: '涨跌幅' }
]

const pageStatusText = computed(() => {
    if (loading.value) {
        return '同步中'
    }
    if (showRefreshWarning.value) {
        return '刷新异常'
    }
    if (error.value) {
        return '同步异常'
    }
    if (!hasLoaded.value) {
        return '待同步'
    }
    if (!hasExecutedScreening.value) {
        return '待执行筛选'
    }
    return screeningResults.value.length > 0 ? '筛选已就绪' : '无匹配结果'
})

const pageStatusType = computed(() => {
    if (showRefreshWarning.value) {
        return 'warning'
    }
    if (error.value) {
        return 'danger'
    }
    if (loading.value || !hasLoaded.value) {
        return 'info'
    }
    if (!hasExecutedScreening.value) {
        return 'warning'
    }
    return screeningResults.value.length > 0 ? 'success' : 'warning'
})

const showRefreshWarning = computed(() => !loading.value && staleError.value.length > 0)
const showErrorState = computed(() => Boolean(error.value) && !loading.value && !showRefreshWarning.value)
const showIndicatorsEmpty = computed(() => activeTab.value === 'indicators' && hasLoaded.value && filteredIndicators.value.length === 0 && !showErrorState.value)
const showResultsIdle = computed(() => activeTab.value === 'results' && hasLoaded.value && !hasExecutedScreening.value && !showErrorState.value)
const showResultsEmpty = computed(() => activeTab.value === 'results' && hasLoaded.value && hasExecutedScreening.value && screeningResults.value.length === 0 && !showErrorState.value)
const visibleIndicatorCount = computed(() => filteredIndicators.value.length)
const hasVerifiedSummaryEvidence = computed(() =>
    stats.value.availableIndicators > 0 ||
    visibleIndicatorCount.value > 0 ||
    stats.value.screenedStocks > 0 ||
    stats.value.screeningTimes > 0 ||
    stats.value.qualifiedStocks > 0
)
const showSummaryPlaceholders = computed(() =>
    loading.value || !hasLoaded.value || (showErrorState.value && !hasVerifiedSummaryEvidence.value)
)
const displayLastUpdateTime = computed(() => showSummaryPlaceholders.value ? '--' : (lastUpdateTime.value || '--'))
const displayAvailableIndicators = computed(() => showSummaryPlaceholders.value ? '--' : String(stats.value.availableIndicators))
const displayVisibleIndicatorCount = computed(() => showSummaryPlaceholders.value ? '--' : String(visibleIndicatorCount.value))
const displayScreenedStocks = computed(() => showSummaryPlaceholders.value ? '--' : String(stats.value.screenedStocks))
const displayScreeningTimes = computed(() => showSummaryPlaceholders.value ? '--' : String(stats.value.screeningTimes))
const displayQualifiedStocks = computed(() => showSummaryPlaceholders.value ? '--' : String(stats.value.qualifiedStocks))
const loadingMessage = computed(() => hasLoaded.value ? '正在刷新数据分析状态...' : '正在初始化数据分析工作台...')
const loadingHint = computed(() => hasLoaded.value
    ? '正在重新拉取指标注册表与股票池。'
    : '正在获取指标注册表与股票池，若后端异常服务层会自动重试。'
)
function formatIndicatorParam(value) {
    if (value === null || value === undefined) {
        return '未配置'
    }

    if (typeof value !== 'object') {
        return String(value)
    }

    const paramName = typeof value.displayName === 'string' && value.displayName
        ? value.displayName
        : typeof value.name === 'string' && value.name
            ? value.name
            : 'param'
    const paramValue = value.default ?? value.value ?? value.initial ?? null

    return paramValue === null || paramValue === undefined || paramValue === ''
        ? paramName
        : `${paramName}(${String(paramValue)})`
}
const selectedIndicatorParamsLabel = computed(() => {
    if (!selectedIndicator.value) {
        return '未选择'
    }

    if (!Array.isArray(selectedIndicator.value.params) || selectedIndicator.value.params.length === 0) {
        return '默认参数'
    }

    return selectedIndicator.value.params.map((value) => formatIndicatorParam(value)).join(' / ')
})
const screeningCapabilityLabel = computed(() => technicalIndicatorScreeningSupported ? '已接入' : '暂未接入')

function getCategoryCount(_key) {
    return indicators.value.filter((item) => item.category === _key).length
}

function selectIndicator(_ind) {
    setSelectedIndicator(_ind)
}

function addIndicatorFilter() {
    screeningFilters.value.indicators.push({ indicator: '', operator: '>', value: 0 })
}

function removeIndicatorFilter(index) {
    screeningFilters.value.indicators.splice(index, 1)
}

function handleRowClick(_row) {
    setSelectedStock(_row)
}

function handleRefresh() {
    void refreshData()
}

function handleRunScreening() {
    runScreening()
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

.header-meta {
    display: flex;
    gap: var(--artdeco-spacing-3);
    flex-wrap: wrap;
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
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

.loading-hint {
    max-width: 32rem;
    text-align: center;
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
}

.state-panel {
    display: grid;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-5);
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
}

.state-panel p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-display);
}

.state-panel span {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
}

.context-panel {
    display: grid;
    gap: var(--artdeco-spacing-3);
    margin-bottom: var(--artdeco-spacing-4);
    padding: var(--artdeco-spacing-4);
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 70%);
}

.inline-context {
    margin-bottom: var(--artdeco-spacing-5);
}

.context-eyebrow {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.context-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--artdeco-spacing-3);
}

.context-grid > div {
    display: grid;
    gap: var(--artdeco-spacing-1);
}

.context-label {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
}

.context-description {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
}

.editor-card {
    background: transparent;
}

.detail-workspace,
.detail-empty-state {
    padding: var(--artdeco-spacing-6);
    border: 1px solid var(--artdeco-border-default);
    background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 70%);
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--artdeco-spacing-4);
}

.detail-card {
    display: grid;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-4);
    border: 1px solid var(--artdeco-border-default);
    background: color-mix(in srgb, var(--artdeco-bg-card) 92%, transparent);
}

.detail-label {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
    font-family: var(--artdeco-font-mono);
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.detail-value {
    color: var(--artdeco-gold-primary);
    font-size: var(--artdeco-text-lg);
}

.detail-note {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
}

.detail-actions {
    display: flex;
    gap: var(--artdeco-spacing-3);
    justify-content: flex-end;
    margin-top: var(--artdeco-spacing-5);
}

.detail-empty-state {
    display: grid;
    gap: var(--artdeco-spacing-3);
    justify-items: start;
}

.detail-empty-state p {
    margin: 0;
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-xl);
}

.detail-empty-state span {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
}

@media (max-width: 1200px) {
    .detail-grid {
        grid-template-columns: 1fr;
    }
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (width <= 75rem) {
    .stats-overview {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .page-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .context-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
