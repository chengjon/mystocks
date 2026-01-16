<template>
    <div class="artdeco-financial-valuation">
        <!-- 财务估值概览 -->
        <div class="valuation-overview">
            <ArtDecoStatCard
                label="当前估值"
                :value="getCurrentValuation()"
                description="基于多种方法的综合估值"
                variant="default"
            />

            <ArtDecoStatCard
                label="市盈率"
                :value="getPERatio()"
                description="价格/每股收益"
                variant="default"
            />

            <ArtDecoStatCard
                label="市净率"
                :value="getPBRatio()"
                description="价格/每股净资产"
                variant="default"
            />

            <ArtDecoStatCard
                label="市销率"
                :value="getPSRatio()"
                description="价格/每股销售额"
                variant="default"
            />

            <ArtDecoStatCard
                label="股息率"
                :value="getDividendYield()"
                description="年度股息/股价"
                variant="rise"
            />

            <ArtDecoStatCard
                label="估值状态"
                :value="getValuationStatus()"
                description="相对历史估值水平"
                :variant="getValuationStatusVariant()"
            />
        </div>

        <!-- 财务指标分析 -->
        <ArtDecoCard class="financial-metrics">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>财务指标分析</h4>
                        <p>FINANCIAL METRICS ANALYSIS</p>
                    </div>
                    <div class="metrics-controls">
                        <ArtDecoSelect v-model="metricsPeriod" :options="periodOptions" size="sm" />
                        <ArtDecoSelect v-model="metricsType" :options="metricsTypeOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="metrics-analysis">
                <div class="key-metrics">
                    <div class="metrics-grid">
                        <div
                            v-for="metric in keyMetrics"
                            :key="metric.key"
                            class="metric-item"
                            :class="getMetricTrendClass(metric)"
                        >
                            <div class="metric-header">
                                <div class="metric-name">{{ metric.name }}</div>
                                <div class="metric-trend" :class="metric.trend">
                                    <svg
                                        v-if="metric.trend === 'up'"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                    >
                                        <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                    </svg>
                                    <svg
                                        v-else-if="metric.trend === 'down'"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                    >
                                        <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                                    </svg>
                                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M5 12h14"></path>
                                    </svg>
                                </div>
                            </div>

                            <div class="metric-value">
                                <span class="current">{{ metric.current }}</span>
                                <span class="unit">{{ metric.unit }}</span>
                            </div>

                            <div class="metric-comparison">
                                <div class="comparison-item">
                                    <span class="label">行业均值:</span>
                                    <span class="value">{{ metric.industryAvg }}</span>
                                </div>
                                <div class="comparison-item">
                                    <span class="label">历史均值:</span>
                                    <span class="value">{{ metric.historicalAvg }}</span>
                                </div>
                            </div>

                            <div class="metric-chart">
                                <!-- 指标趋势小图 -->
                                <div class="mini-chart">
                                    <div
                                        class="chart-line"
                                        :style="{ height: getMiniChartHeight(metric.trendData) + '%' }"
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="metrics-insights">
                    <h5>财务健康度评估</h5>
                    <div class="health-score">
                        <div class="score-gauge">
                            <div class="gauge-container">
                                <div class="gauge-background">
                                    <div
                                        class="gauge-fill"
                                        :style="{ transform: `rotate(${(financialHealthScore / 100) * 180 - 90}deg)` }"
                                        :class="getHealthScoreClass(financialHealthScore)"
                                    ></div>
                                </div>
                                <div class="gauge-center">
                                    <div class="gauge-value">{{ financialHealthScore }}</div>
                                    <div class="gauge-label">健康度</div>
                                </div>
                            </div>
                        </div>

                        <div class="score-description">
                            <h6>{{ getHealthScoreText(financialHealthScore) }}</h6>
                            <p>{{ getHealthScoreDescription(financialHealthScore) }}</p>
                            <div class="score-factors">
                                <div class="factor-item">
                                    <span class="factor-label">盈利能力:</span>
                                    <span class="factor-value" :class="getFactorClass(profitabilityScore)">
                                        {{ profitabilityScore }}/100
                                    </span>
                                </div>
                                <div class="factor-item">
                                    <span class="factor-label">偿债能力:</span>
                                    <span class="factor-value" :class="getFactorClass(solvencyScore)">
                                        {{ solvencyScore }}/100
                                    </span>
                                </div>
                                <div class="factor-item">
                                    <span class="factor-label">运营效率:</span>
                                    <span class="factor-value" :class="getFactorClass(efficiencyScore)">
                                        {{ efficiencyScore }}/100
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 杜邦分析 -->
        <ArtDecoCard class="dupont-analysis">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M12 6v6l4 2"></path>
                            <circle cx="12" cy="12" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>杜邦分析</h4>
                        <p>DUPONT ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="dupont-analysis-content">
                <div class="dupont-tree">
                    <!-- 杜邦分析树状图 -->
                    <div class="tree-visualization">
                        <div class="tree-root">
                            <div class="metric-node roe-node">
                                <div class="node-label">净资产收益率</div>
                                <div class="node-value">{{ roe }}%</div>
                            </div>
                        </div>

                        <div class="tree-branches">
                            <div class="branch">
                                <div class="branch-line"></div>
                                <div class="metric-node equity-multiplier-node">
                                    <div class="node-label">权益乘数</div>
                                    <div class="node-value">{{ equityMultiplier }}</div>
                                </div>
                            </div>

                            <div class="branch">
                                <div class="branch-line"></div>
                                <div class="sub-tree">
                                    <div class="metric-node total-assets-turnover-node">
                                        <div class="node-label">总资产周转率</div>
                                        <div class="node-value">{{ totalAssetsTurnover }}</div>
                                    </div>

                                    <div class="branch">
                                        <div class="branch-line"></div>
                                        <div class="metric-node net-profit-margin-node">
                                            <div class="node-label">销售净利率</div>
                                            <div class="node-value">{{ netProfitMargin }}%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="dupont-insights">
                    <h5>杜邦分析洞察</h5>
                    <div class="insights-list">
                        <div class="insight-item">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">主要驱动因素</div>
                                <div class="insight-value">{{ getDupontDriver() }}</div>
                                <div class="insight-description">ROE提升的主要贡献因素</div>
                            </div>
                        </div>

                        <div class="insight-item">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">改进空间</div>
                                <div class="insight-value">{{ getDupontImprovement() }}</div>
                                <div class="insight-description">ROE提升的潜在机会</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 估值方法比较 -->
        <ArtDecoCard class="valuation-methods">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M3 3h18v18H3z"></path>
                            <path d="M9 9h6v6H9z"></path>
                            <circle cx="12" cy="12" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>估值方法比较</h4>
                        <p>VALUATION METHODS COMPARISON</p>
                    </div>
                    <div class="valuation-controls">
                        <ArtDecoSelect v-model="valuationMethod" :options="valuationMethodOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="valuation-comparison">
                <div class="methods-comparison">
                    <div class="comparison-table">
                        <div class="table-header">
                            <div class="col-method">估值方法</div>
                            <div class="col-value">估值结果</div>
                            <div class="col-premium">溢价率</div>
                            <div class="col-confidence">置信度</div>
                        </div>
                        <div class="table-body">
                            <div v-for="method in valuationMethods" :key="method.name" class="table-row">
                                <div class="col-method">
                                    <div class="method-name">{{ method.name }}</div>
                                    <div class="method-desc">{{ method.description }}</div>
                                </div>
                                <div class="col-value">
                                    <div class="value">{{ method.value }}</div>
                                    <div class="range">{{ method.range }}</div>
                                </div>
                                <div class="col-premium">
                                    <div class="premium" :class="getPremiumClass(method.premium)">
                                        {{ method.premium }}
                                    </div>
                                </div>
                                <div class="col-confidence">
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" :style="{ width: method.confidence + '%' }"></div>
                                    </div>
                                    <div class="confidence-text">{{ method.confidence }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="valuation-chart">
                    <div class="chart-placeholder">
                        <!-- 估值方法对比图 -->
                        <div class="valuation-visualization">
                            <div class="valuation-bars">
                                <div v-for="method in valuationMethods" :key="method.name" class="valuation-bar">
                                    <div class="bar-container">
                                        <div
                                            class="bar-fill"
                                            :style="{ height: (method.valueNum / maxValuationValue) * 100 + '%' }"
                                        ></div>
                                    </div>
                                    <div class="bar-label">
                                        <span class="method-code">{{ getMethodCode(method.name) }}</span>
                                        <span class="method-value">{{ method.value }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="current-price-line">
                                <div class="price-line"></div>
                                <div class="price-label">当前股价: {{ currentPrice }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 历史相似收益估值 -->
        <ArtDecoCard class="historical-valuation">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>历史相似收益估值</h4>
                        <p>HISTORICAL SIMILAR RETURNS VALUATION</p>
                    </div>
                </div>
            </template>

            <div class="historical-analysis">
                <div class="similar-companies">
                    <h5>相似公司比较</h5>
                    <div class="companies-table">
                        <div class="table-header">
                            <div class="col-company">公司</div>
                            <div class="col-metric">关键指标</div>
                            <div class="col-valuation">估值倍数</div>
                            <div class="col-similarity">相似度</div>
                        </div>
                        <div class="table-body">
                            <div v-for="company in similarCompanies" :key="company.code" class="table-row">
                                <div class="col-company">
                                    <div class="company-name">{{ company.name }}</div>
                                    <div class="company-code">{{ company.code }}</div>
                                </div>
                                <div class="col-metric">
                                    <div class="metric-grid">
                                        <div class="metric-item">
                                            <span class="label">PE:</span>
                                            <span class="value">{{ company.pe }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="label">PB:</span>
                                            <span class="value">{{ company.pb }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="label">ROE:</span>
                                            <span class="value">{{ company.roe }}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-valuation">
                                    <div class="valuation">{{ company.valuation }}</div>
                                    <div class="premium" :class="getPremiumClass(company.premium)">
                                        {{ company.premium }}
                                    </div>
                                </div>
                                <div class="col-similarity">
                                    <div class="similarity-bar">
                                        <div class="similarity-fill" :style="{ width: company.similarity + '%' }"></div>
                                    </div>
                                    <div class="similarity-text">{{ company.similarity }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="historical-insights">
                    <h5>历史估值洞察</h5>
                    <div class="insights-grid">
                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">相对估值</div>
                                <div class="insight-value">{{ getRelativeValuation() }}</div>
                                <div class="insight-description">相比相似公司的估值水平</div>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">历史分位数</div>
                                <div class="insight-value">{{ historicalPercentile }}%</div>
                                <div class="insight-description">在历史估值分布中的位置</div>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">目标价区间</div>
                                <div class="insight-value">{{ getTargetPriceRange() }}</div>
                                <div class="insight-description">基于相似公司估值的合理区间</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'

    interface Props {
        data: any
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const metricsPeriod = ref('annual')
    const metricsType = ref('profitability')
    const valuationMethod = ref('comprehensive')

    // 计算属性
    const valuationData = computed(() => props.data?.valuation || {})
    const financialData = computed(() => props.data?.financial || {})
    const dupontData = computed(() => props.data?.dupont || {})
    const historicalData = computed(() => props.data?.historical || {})

    const currentPrice = computed(() => valuationData.value?.currentPrice || 0)

    // 财务指标相关
    const keyMetrics = computed(() => financialData.value?.keyMetrics || [])
    const financialHealthScore = computed(() => financialData.value?.healthScore || 0)
    const profitabilityScore = computed(() => financialData.value?.profitabilityScore || 0)
    const solvencyScore = computed(() => financialData.value?.solvencyScore || 0)
    const efficiencyScore = computed(() => financialData.value?.efficiencyScore || 0)

    // 杜邦分析相关
    const roe = computed(() => dupontData.value?.roe || 0)
    const equityMultiplier = computed(() => dupontData.value?.equityMultiplier || 0)
    const totalAssetsTurnover = computed(() => dupontData.value?.totalAssetsTurnover || 0)
    const netProfitMargin = computed(() => dupontData.value?.netProfitMargin || 0)

    // 估值方法相关
    const valuationMethods = computed(() => valuationData.value?.methods || [])
    const maxValuationValue = computed(() => {
        const values = valuationMethods.value.map((m: any) => m.valueNum)
        return values.length > 0 ? Math.max(...values) : 1
    })

    // 历史估值相关
    const similarCompanies = computed(() => historicalData.value?.similarCompanies || [])
    const historicalPercentile = computed(() => historicalData.value?.percentile || 0)

    // 配置选项
    const periodOptions = [
        { label: '年度', value: 'annual' },
        { label: '季度', value: 'quarterly' },
        { label: 'TTM', value: 'ttm' }
    ]

    const metricsTypeOptions = [
        { label: '盈利能力', value: 'profitability' },
        { label: '偿债能力', value: 'solvency' },
        { label: '运营效率', value: 'efficiency' },
        { label: '成长能力', value: 'growth' }
    ]

    const valuationMethodOptions = [
        { label: '综合估值', value: 'comprehensive' },
        { label: 'PE估值', value: 'pe' },
        { label: 'PB估值', value: 'pb' },
        { label: 'DCF估值', value: 'dcf' }
    ]

    // 格式化函数
    const getCurrentValuation = (): string => {
        const valuation = valuationData.value?.current || 0
        return valuation.toFixed(2)
    }

    const getPERatio = (): string => {
        const pe = valuationData.value?.pe || 0
        return pe.toFixed(2)
    }

    const getPBRatio = (): string => {
        const pb = valuationData.value?.pb || 0
        return pb.toFixed(2)
    }

    const getPSRatio = (): string => {
        const ps = valuationData.value?.ps || 0
        return ps.toFixed(2)
    }

    const getDividendYield = (): string => {
        const dividend = valuationData.value?.dividendYield || 0
        return `${(dividend * 100).toFixed(2)}%`
    }

    const getValuationStatus = (): string => {
        const status = valuationData.value?.status || '正常'
        return status
    }

    const getValuationStatusVariant = (): 'rise' | 'fall' | 'default' => {
        const status = valuationData.value?.status || '正常'
        if (status === '低估') return 'rise'
        if (status === '高估') return 'fall'
        return 'default'
    }

    const getMetricTrendClass = (metric: any): string => {
        return metric.trend || 'neutral'
    }

    const getMiniChartHeight = (data: any[]): string => {
        if (!data || data.length === 0) return '50'
        const values = data.map(d => d.value)
        const max = Math.max(...values)
        const min = Math.min(...values)
        const range = max - min
        if (range === 0) return '50'
        const lastValue = values[values.length - 1]
        return (((lastValue - min) / range) * 80 + 10).toString()
    }

    const getHealthScoreClass = (score: number): string => {
        if (score >= 80) return 'excellent'
        if (score >= 60) return 'good'
        if (score >= 40) return 'fair'
        return 'poor'
    }

    const getHealthScoreText = (score: number): string => {
        if (score >= 80) return '财务状况优秀'
        if (score >= 60) return '财务状况良好'
        if (score >= 40) return '财务状况一般'
        return '财务状况堪忧'
    }

    const getHealthScoreDescription = (score: number): string => {
        if (score >= 80) return '公司财务状况非常健康，各项指标表现优秀'
        if (score >= 60) return '公司财务状况良好，主要指标符合行业标准'
        if (score >= 40) return '公司财务状况一般，部分指标需要关注'
        return '公司财务状况不佳，存在较多财务风险'
    }

    const getFactorClass = (score: number): string => {
        if (score >= 80) return 'excellent'
        if (score >= 60) return 'good'
        if (score >= 40) return 'fair'
        return 'poor'
    }

    const getDupontDriver = (): string => {
        const drivers = dupontData.value?.drivers || []
        return drivers[0]?.name || '销售净利率'
    }

    const getDupontImprovement = (): string => {
        const improvements = dupontData.value?.improvements || []
        return improvements[0]?.name || '提高资产周转率'
    }

    const getPremiumClass = (premium: string): string => {
        if (premium.includes('+')) return 'positive'
        if (premium.includes('-')) return 'negative'
        return 'neutral'
    }

    const getMethodCode = (methodName: string): string => {
        const codes: Record<string, string> = {
            市盈率估值: 'PE',
            市净率估值: 'PB',
            市销率估值: 'PS',
            股息折现估值: 'DDM',
            自由现金流估值: 'FCF'
        }
        return codes[methodName] || methodName.charAt(0)
    }

    const getRelativeValuation = (): string => {
        const relative = historicalData.value?.relativeValuation || '合理'
        return relative
    }

    const getTargetPriceRange = (): string => {
        const range = historicalData.value?.targetPriceRange || '25.00-35.00'
        return range
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-financial-valuation {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   VALUATION OVERVIEW - 估值概览
    // ============================================

    .valuation-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   FINANCIAL METRICS - 财务指标分析
    // ============================================

    .financial-metrics {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .metrics-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .metrics-analysis {
            .key-metrics {
                margin-bottom: var(--artdeco-spacing-5);

                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .metric-item {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        &.up {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.down {
                            border-left: 3px solid var(--artdeco-down);
                        }

                        .metric-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .metric-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }

                            .metric-trend {
                                width: 24px;
                                height: 24px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: var(--artdeco-fg-primary);

                                &.up {
                                    color: var(--artdeco-up);
                                }

                                &.down {
                                    color: var(--artdeco-down);
                                }
                            }
                        }

                        .metric-value {
                            display: flex;
                            align-items: baseline;
                            gap: var(--artdeco-spacing-1);
                            margin-bottom: var(--artdeco-spacing-3);

                            .current {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xl);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                            }

                            .unit {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                            }
                        }

                        .metric-comparison {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: var(--artdeco-spacing-2);
                            margin-bottom: var(--artdeco-spacing-3);

                            .comparison-item {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;

                                .label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }

                                .value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;
                                }
                            }
                        }

                        .metric-chart {
                            .mini-chart {
                                height: 40px;
                                background: var(--artdeco-bg-muted);
                                border-radius: 4px;
                                position: relative;
                                overflow: hidden;

                                .chart-line {
                                    width: 100%;
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-gold-primary),
                                        var(--artdeco-gold-secondary)
                                    );
                                    border-radius: 4px;
                                    transition: height var(--artdeco-transition-base);
                                }
                            }
                        }
                    }
                }
            }

            .metrics-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .health-score {
                    display: grid;
                    grid-template-columns: 200px 1fr;
                    gap: var(--artdeco-spacing-5);

                    .score-gauge {
                        .gauge-container {
                            position: relative;
                            width: 150px;
                            height: 150px;
                            margin: 0 auto;

                            .gauge-background {
                                position: relative;
                                width: 100%;
                                height: 100%;
                                border-radius: 50%;
                                background: conic-gradient(
                                    from 0deg,
                                    rgba(239, 68, 68, 0.2) 0deg,
                                    rgba(245, 158, 11, 0.4) 45deg,
                                    rgba(34, 197, 94, 0.6) 90deg,
                                    rgba(34, 197, 94, 0.6) 180deg,
                                    rgba(34, 197, 94, 0.6) 180deg
                                );

                                .gauge-fill {
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    width: 100%;
                                    height: 100%;
                                    border-radius: 50%;
                                    background: conic-gradient(
                                        from 0deg,
                                        transparent 0deg,
                                        transparent 180deg,
                                        rgba(34, 197, 94, 0.9) 180deg,
                                        rgba(34, 197, 94, 0.9) 360deg
                                    );
                                    clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%);
                                    transition: transform var(--artdeco-transition-base);
                                }
                            }

                            .gauge-center {
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                text-align: center;

                                .gauge-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xl);
                                    font-weight: 600;
                                    color: var(--artdeco-up);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .gauge-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                }
                            }
                        }
                    }

                    .score-description {
                        h6 {
                            font-family: var(--artdeco-font-display);
                            font-size: var(--artdeco-font-size-md);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin: 0 0 var(--artdeco-spacing-2) 0;
                        }

                        p {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-secondary);
                            line-height: 1.5;
                            margin-bottom: var(--artdeco-spacing-3);
                        }

                        .score-factors {
                            .factor-item {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                margin-bottom: var(--artdeco-spacing-2);

                                .factor-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }

                                .factor-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-primary);
                                    font-weight: 600;

                                    &.excellent {
                                        color: var(--artdeco-up);
                                    }

                                    &.good {
                                        color: var(--artdeco-gold-primary);
                                    }

                                    &.fair {
                                        color: #f59e0b;
                                    }

                                    &.poor {
                                        color: var(--artdeco-down);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   DUPONT ANALYSIS - 杜邦分析
    // ============================================

    .dupont-analysis {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .dupont-analysis-content {
            .dupont-tree {
                margin-bottom: var(--artdeco-spacing-5);

                .tree-visualization {
                    position: relative;
                    height: 300px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: var(--artdeco-spacing-4);

                    .tree-root {
                        .metric-node {
                            background: var(--artdeco-gold-primary);
                            color: var(--artdeco-bg-dark);
                            padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                            border-radius: 8px;
                            text-align: center;
                            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);

                            .node-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                font-weight: 600;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .node-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                            }
                        }
                    }

                    .tree-branches {
                        display: flex;
                        justify-content: space-between;
                        width: 100%;
                        margin-top: var(--artdeco-spacing-4);

                        .branch {
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            flex: 1;

                            .branch-line {
                                width: 2px;
                                height: 40px;
                                background: var(--artdeco-gold-primary);
                                margin-bottom: var(--artdeco-spacing-2);
                            }

                            .metric-node {
                                background: var(--artdeco-bg-card);
                                border: 1px solid var(--artdeco-border-default);
                                padding: var(--artdeco-spacing-3);
                                border-radius: 6px;
                                text-align: center;
                                min-width: 120px;
                                transition: all var(--artdeco-transition-base);

                                &:hover {
                                    border-color: var(--artdeco-gold-primary);
                                    box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                                }

                                .node-label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .node-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                }
                            }

                            .sub-tree {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                margin-top: var(--artdeco-spacing-4);

                                .branch {
                                    .branch-line {
                                        height: 30px;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .dupont-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-list {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-4);

                    .insight-item {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .insight-icon {
                            flex-shrink: 0;
                            width: 24px;
                            height: 24px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                        }

                        .insight-content {
                            flex: 1;

                            .insight-title {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .insight-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   VALUATION METHODS - 估值方法比较
    // ============================================

    .valuation-methods {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .valuation-controls {
                display: flex;
                align-items: center;
            }
        }

        .valuation-comparison {
            .methods-comparison {
                margin-bottom: var(--artdeco-spacing-5);

                .comparison-table {
                    .table-header {
                        display: grid;
                        grid-template-columns: 2fr 1fr 1fr 1fr;
                        gap: var(--artdeco-spacing-4);
                        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                        background: linear-gradient(135deg, var(--artdeco-bg-muted), rgba(212, 175, 55, 0.05));
                        border-bottom: 1px solid var(--artdeco-border-default);
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        color: var(--artdeco-fg-muted);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                    }

                    .table-body {
                        .table-row {
                            display: grid;
                            grid-template-columns: 2fr 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-4);
                            padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                background: rgba(212, 175, 55, 0.02);
                            }

                            .col-method {
                                .method-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .method-desc {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .col-value {
                                .value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .range {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .col-premium {
                                .premium {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;

                                    &.positive {
                                        color: var(--artdeco-up);
                                    }

                                    &.negative {
                                        color: var(--artdeco-down);
                                    }

                                    &.neutral {
                                        color: var(--artdeco-gold-primary);
                                    }
                                }
                            }

                            .col-confidence {
                                .confidence-bar {
                                    width: 60px;
                                    height: 6px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 3px;
                                    overflow: hidden;
                                    margin-bottom: var(--artdeco-spacing-1);

                                    .confidence-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 3px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .confidence-text {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }
                            }
                        }
                    }
                }
            }

            .valuation-chart {
                .chart-placeholder {
                    height: 300px;
                    background: var(--artdeco-bg-card);
                    border: 1px solid var(--artdeco-border-default);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    overflow: hidden;

                    // 几何装饰
                    @include artdeco-geometric-corners(
                        $color: var(--artdeco-gold-primary),
                        $size: 16px,
                        $border-width: 1px
                    );

                    .valuation-visualization {
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        padding: var(--artdeco-spacing-4);

                        .valuation-bars {
                            flex: 1;
                            display: flex;
                            align-items: end;
                            justify-content: space-around;
                            gap: var(--artdeco-spacing-2);

                            .valuation-bar {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .bar-container {
                                    width: 50px;
                                    height: 200px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 4px 4px 0 0;
                                    position: relative;
                                    overflow: hidden;

                                    .bar-fill {
                                        position: absolute;
                                        bottom: 0;
                                        left: 0;
                                        right: 0;
                                        background: linear-gradient(
                                            180deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 4px 4px 0 0;
                                        transition: height var(--artdeco-transition-base);
                                    }
                                }

                                .bar-label {
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    gap: var(--artdeco-spacing-1);

                                    .method-code {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xs);
                                        font-weight: 600;
                                        color: var(--artdeco-fg-primary);
                                    }

                                    .method-value {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
                                    }
                                }
                            }
                        }

                        .current-price-line {
                            position: absolute;
                            bottom: 0;
                            left: 0;
                            right: 0;
                            height: 2px;
                            background: linear-gradient(90deg, transparent, var(--artdeco-up), transparent);
                            box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);

                            .price-label {
                                position: absolute;
                                top: -25px;
                                right: var(--artdeco-spacing-2);
                                background: var(--artdeco-bg-card);
                                padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                border-radius: 4px;
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                font-weight: 600;
                                color: var(--artdeco-up);
                                border: 1px solid var(--artdeco-up);
                                white-space: nowrap;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   HISTORICAL VALUATION - 历史相似收益估值
    // ============================================

    .historical-valuation {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .historical-analysis {
            .similar-companies {
                margin-bottom: var(--artdeco-spacing-5);

                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .companies-table {
                    .table-header {
                        display: grid;
                        grid-template-columns: 1.5fr 1fr 1fr 1fr;
                        gap: var(--artdeco-spacing-4);
                        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                        background: linear-gradient(135deg, var(--artdeco-bg-muted), rgba(212, 175, 55, 0.05));
                        border-bottom: 1px solid var(--artdeco-border-default);
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        color: var(--artdeco-fg-muted);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                    }

                    .table-body {
                        .table-row {
                            display: grid;
                            grid-template-columns: 1.5fr 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-4);
                            padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                background: rgba(212, 175, 55, 0.02);
                            }

                            .col-company {
                                .company-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .company-code {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .col-metric {
                                .metric-grid {
                                    display: flex;
                                    flex-direction: column;
                                    gap: var(--artdeco-spacing-1);

                                    .metric-item {
                                        display: flex;
                                        justify-content: space-between;
                                        align-items: center;

                                        .label {
                                            font-family: var(--artdeco-font-body);
                                            font-size: var(--artdeco-font-size-xs);
                                            color: var(--artdeco-fg-muted);
                                            font-weight: 600;
                                        }

                                        .value {
                                            font-family: var(--artdeco-font-mono);
                                            font-size: var(--artdeco-font-size-xs);
                                            color: var(--artdeco-fg-primary);
                                            font-weight: 600;
                                        }
                                    }
                                }
                            }

                            .col-valuation {
                                .valuation {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .premium {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;

                                    &.positive {
                                        color: var(--artdeco-up);
                                    }

                                    &.negative {
                                        color: var(--artdeco-down);
                                    }

                                    &.neutral {
                                        color: var(--artdeco-gold-primary);
                                    }
                                }
                            }

                            .col-similarity {
                                .similarity-bar {
                                    width: 60px;
                                    height: 6px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 3px;
                                    overflow: hidden;
                                    margin-bottom: var(--artdeco-spacing-1);

                                    .similarity-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 3px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .similarity-text {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }
                            }
                        }
                    }
                }
            }

            .historical-insights {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .insights-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .insight-card {
                        display: flex;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .insight-icon {
                            flex-shrink: 0;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: var(--artdeco-fg-primary);
                        }

                        .insight-content {
                            flex: 1;

                            .insight-title {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .insight-description {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-secondary);
                                line-height: 1.5;
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-financial-valuation {
            gap: var(--artdeco-spacing-4);
        }

        .valuation-overview {
            grid-template-columns: 1fr;
        }

        .financial-metrics {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .metrics-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }

            .metrics-analysis {
                .key-metrics {
                    .metrics-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .dupont-analysis {
            .dupont-analysis-content {
                .dupont-tree {
                    .tree-visualization {
                        .tree-branches {
                            flex-direction: column;
                            gap: var(--artdeco-spacing-4);

                            .branch {
                                width: 100%;
                            }
                        }
                    }
                }

                .dupont-insights {
                    .insights-list {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .valuation-methods {
            .valuation-comparison {
                .methods-comparison {
                    .comparison-table {
                        .table-header,
                        .table-row {
                            grid-template-columns: 1fr;
                            gap: var(--artdeco-spacing-2);
                        }
                    }
                }
            }
        }

        .historical-valuation {
            .historical-analysis {
                .similar-companies {
                    .companies-table {
                        .table-header,
                        .table-row {
                            grid-template-columns: 1fr;
                            gap: var(--artdeco-spacing-2);
                        }
                    }
                }

                .historical-insights {
                    .insights-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
