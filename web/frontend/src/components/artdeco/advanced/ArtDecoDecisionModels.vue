<template>
    <div class="artdeco-decision-models">
        <!-- 决策模型概览 -->
        <div class="models-overview">
            <ArtDecoStatCard
                label="最佳决策模型"
                :value="getBestModel()"
                description="当前最优决策建议"
                variant="default"
            />

            <ArtDecoStatCard
                label="决策置信度"
                :value="getDecisionConfidence()"
                description="模型决策信心水平"
                variant="default"
            />

            <ArtDecoStatCard
                label="预期收益"
                :value="getExpectedReturn()"
                description="模型预测年化收益"
                variant="rise"
            />

            <ArtDecoStatCard
                label="风险评估"
                :value="getRiskAssessment()"
                description="综合风险等级"
                :variant="getRiskVariant()"
            />
        </div>

        <!-- 模型对比分析 -->
        <ArtDecoCard class="model-comparison">
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
                        <h4>模型对比分析</h4>
                        <p>MODEL COMPARISON ANALYSIS</p>
                    </div>
                    <div class="comparison-controls">
                        <ArtDecoSelect v-model="comparisonMetric" :options="metricOptions" size="sm" />
                        <ArtDecoSwitch v-model="showHistorical" label="显示历史" />
                    </div>
                </div>
            </template>

            <div class="comparison-analysis">
                <div class="models-performance">
                    <div class="performance-table">
                        <div class="table-header">
                            <div class="col-model">决策模型</div>
                            <div class="col-signal">当前信号</div>
                            <div class="col-confidence">置信度</div>
                            <div class="col-return">预期收益</div>
                            <div class="col-risk">风险等级</div>
                        </div>
                        <div class="table-body">
                            <div
                                v-for="model in decisionModels"
                                :key="model.name"
                                class="table-row"
                                :class="getModelClass(model)"
                            >
                                <div class="col-model">
                                    <div class="model-name">{{ model.name }}</div>
                                    <div class="model-desc">{{ model.description }}</div>
                                </div>
                                <div class="col-signal">
                                    <span :class="getSignalClass(model.signal)">{{ getSignalText(model.signal) }}</span>
                                </div>
                                <div class="col-confidence">
                                    <div class="confidence-bar">
                                        <div class="confidence-fill" :style="{ width: model.confidence + '%' }"></div>
                                    </div>
                                    <div class="confidence-text">{{ model.confidence }}%</div>
                                </div>
                                <div class="col-return">
                                    <span :class="getReturnClass(model.expectedReturn)">
                                        {{ model.expectedReturn }}%
                                    </span>
                                </div>
                                <div class="col-risk">
                                    <span :class="getRiskClass(model.riskLevel)">{{ model.riskLevel }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="models-chart">
                    <div class="chart-placeholder">
                        <!-- 模型性能对比图 -->
                        <div class="models-performance-visualization">
                            <div class="performance-bars">
                                <div v-for="model in decisionModels" :key="model.name" class="performance-bar">
                                    <div class="bar-container">
                                        <div
                                            class="bar-fill"
                                            :style="{ height: (model.confidence / maxConfidence) * 100 + '%' }"
                                            :class="getModelBarClass(model)"
                                        ></div>
                                    </div>
                                    <div class="bar-label">
                                        <span class="model-code">{{ getModelCode(model.name) }}</span>
                                        <span class="model-confidence">{{ model.confidence }}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 巴菲特模型分析 -->
        <ArtDecoCard class="buffett-model">
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
                        <h4>巴菲特价值投资模型</h4>
                        <p>BUFFETT VALUE INVESTING MODEL</p>
                    </div>
                </div>
            </template>

            <div class="buffett-analysis">
                <div class="buffett-criteria">
                    <div class="criteria-grid">
                        <div
                            v-for="criterion in buffettCriteria"
                            :key="criterion.name"
                            class="criterion-item"
                            :class="getCriterionClass(criterion)"
                        >
                            <div class="criterion-header">
                                <div class="criterion-name">{{ criterion.name }}</div>
                                <div class="criterion-score">
                                    <div class="score-bar">
                                        <div class="score-fill" :style="{ width: criterion.score + '%' }"></div>
                                    </div>
                                    <span class="score-value">{{ criterion.score }}/100</span>
                                </div>
                            </div>

                            <div class="criterion-details">
                                <div class="detail-item">
                                    <span class="label">当前值:</span>
                                    <span class="value">{{ criterion.currentValue }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">标准值:</span>
                                    <span class="value">{{ criterion.standardValue }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="buffett-insights">
                    <div class="buffett-score">
                        <div class="score-gauge">
                            <div class="gauge-container">
                                <div class="gauge-background">
                                    <div
                                        class="gauge-fill"
                                        :style="{ transform: `rotate(${(buffettOverallScore / 100) * 180 - 90}deg)` }"
                                        :class="getBuffettScoreClass(buffettOverallScore)"
                                    ></div>
                                </div>
                                <div class="gauge-center">
                                    <div class="gauge-value">{{ buffettOverallScore }}</div>
                                    <div class="gauge-label">价值评分</div>
                                </div>
                            </div>
                        </div>

                        <div class="score-description">
                            <h5>{{ getBuffettScoreText(buffettOverallScore) }}</h5>
                            <p>{{ getBuffettScoreDescription(buffettOverallScore) }}</p>
                        </div>
                    </div>

                    <div class="buffett-recommendations">
                        <h5>巴菲特投资建议</h5>
                        <div class="recommendations-list">
                            <div
                                v-for="rec in buffettRecommendations"
                                :key="rec.id"
                                class="recommendation-item"
                                :class="rec.type"
                            >
                                <div class="rec-icon">
                                    <svg
                                        v-if="rec.type === 'buy'"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                    >
                                        <path d="M9 11l3 3L22 4"></path>
                                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                                    </svg>
                                    <svg
                                        v-else-if="rec.type === 'hold'"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                    >
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <path d="M9 12l2 2 4-4"></path>
                                    </svg>
                                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                                    </svg>
                                </div>
                                <div class="rec-content">
                                    <div class="rec-title">{{ rec.title }}</div>
                                    <div class="rec-description">{{ rec.description }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 欧内尔模型分析 -->
        <ArtDecoCard class="oneil-model">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>欧内尔CANSLIM模型</h4>
                        <p>ONEIL CANSLIM MODEL</p>
                    </div>
                </div>
            </template>

            <div class="oneil-analysis">
                <div class="canslim-factors">
                    <div class="factors-grid">
                        <div v-for="factor in canslimFactors" :key="factor.letter" class="factor-item">
                            <div class="factor-header">
                                <div class="factor-letter">{{ factor.letter }}</div>
                                <div class="factor-name">{{ factor.name }}</div>
                            </div>

                            <div class="factor-score">
                                <div class="score-bar">
                                    <div
                                        class="score-fill"
                                        :style="{ width: factor.score + '%' }"
                                        :class="getFactorScoreClass(factor.score)"
                                    ></div>
                                </div>
                                <div class="score-value">{{ factor.score }}/100</div>
                            </div>

                            <div class="factor-description">{{ factor.description }}</div>
                        </div>
                    </div>
                </div>

                <div class="oneil-signal">
                    <div class="signal-strength">
                        <div class="strength-gauge">
                            <div class="gauge-container">
                                <div class="gauge-background">
                                    <div
                                        class="gauge-fill"
                                        :style="{ transform: `rotate(${(oneilSignalStrength / 100) * 180 - 90}deg)` }"
                                        :class="getOneilSignalClass(oneilSignalStrength)"
                                    ></div>
                                </div>
                                <div class="gauge-center">
                                    <div class="gauge-value">{{ oneilSignalStrength }}</div>
                                    <div class="gauge-label">信号强度</div>
                                </div>
                            </div>
                        </div>

                        <div class="signal-details">
                            <h5>欧内尔信号强度</h5>
                            <p>{{ getOneilSignalDescription(oneilSignalStrength) }}</p>
                            <div class="signal-breakdown">
                                <div class="breakdown-item">
                                    <span class="label">基础因素:</span>
                                    <span class="value">{{ oneilFundamentalScore }}/100</span>
                                </div>
                                <div class="breakdown-item">
                                    <span class="label">技术因素:</span>
                                    <span class="value">{{ oneilTechnicalScore }}/100</span>
                                </div>
                                <div class="breakdown-item">
                                    <span class="label">市场因素:</span>
                                    <span class="value">{{ oneilMarketScore }}/100</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 林奇模型分析 -->
        <ArtDecoCard class="lynch-model">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 2v20m9-9H3"></path>
                            <circle cx="12" cy="9" r="2"></circle>
                            <circle cx="7" cy="15" r="2"></circle>
                            <circle cx="17" cy="15" r="2"></circle>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>林奇PEG估值模型</h4>
                        <p>LYNCH PEG VALUATION MODEL</p>
                    </div>
                </div>
            </template>

            <div class="lynch-analysis">
                <div class="peg-analysis">
                    <div class="peg-metrics">
                        <div class="metric-item">
                            <div class="metric-label">PEG比率</div>
                            <div class="metric-value" :class="getPegClass(pegRatio)">
                                {{ pegRatio.toFixed(2) }}
                            </div>
                            <div class="metric-desc">{{ getPegDescription(pegRatio) }}</div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">市盈率</div>
                            <div class="metric-value">{{ peRatio.toFixed(2) }}</div>
                            <div class="metric-desc">当前PE估值</div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">增长率</div>
                            <div class="metric-value" :class="getGrowthClass(growthRate)">
                                {{ growthRate.toFixed(1) }}%
                            </div>
                            <div class="metric-desc">预期年增长率</div>
                        </div>
                    </div>
                </div>

                <div class="lynch-valuation">
                    <div class="valuation-zones">
                        <div class="zones-visualization">
                            <div class="valuation-scale">
                                <div class="scale-marker" :style="{ left: '20%' }">
                                    <div class="marker-line"></div>
                                    <div class="marker-label">低估</div>
                                </div>
                                <div class="scale-marker" :style="{ left: '50%' }">
                                    <div class="marker-line"></div>
                                    <div class="marker-label">合理</div>
                                </div>
                                <div class="scale-marker" :style="{ left: '80%' }">
                                    <div class="marker-line"></div>
                                    <div class="marker-label">高估</div>
                                </div>
                            </div>
                            <div class="current-position" :style="{ left: getPegPosition() + '%' }">
                                <div class="position-dot"></div>
                                <div class="position-label">当前PEG</div>
                            </div>
                        </div>
                    </div>

                    <div class="lynch-insights">
                        <h5>林奇投资洞察</h5>
                        <div class="insights-list">
                            <div class="insight-item">
                                <div class="insight-icon">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="insight-content">
                                    <div class="insight-title">成长性评估</div>
                                    <div class="insight-value">{{ getGrowthAssessment() }}</div>
                                    <div class="insight-description">基于PEG模型的成长性判断</div>
                                </div>
                            </div>

                            <div class="insight-item">
                                <div class="insight-icon">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="insight-content">
                                    <div class="insight-title">投资时点</div>
                                    <div class="insight-value">{{ getInvestmentTiming() }}</div>
                                    <div class="insight-description">基于PEG的买入时机建议</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 数据挖掘模型 -->
        <ArtDecoCard class="mining-model">
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
                        <h4>数据挖掘模型</h4>
                        <p>DATA MINING MODEL</p>
                    </div>
                    <div class="mining-controls">
                        <ArtDecoSelect v-model="miningAlgorithm" :options="algorithmOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="mining-analysis">
                <div class="mining-results">
                    <div class="results-metrics">
                        <div class="metric-item">
                            <div class="metric-label">模型准确率</div>
                            <div class="metric-value" :class="getAccuracyClass(miningAccuracy)">
                                {{ miningAccuracy.toFixed(1) }}%
                            </div>
                            <div class="metric-desc">历史数据回测准确率</div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">预测概率</div>
                            <div class="metric-value" :class="getProbabilityClass(predictionProbability)">
                                {{ predictionProbability.toFixed(1) }}%
                            </div>
                            <div class="metric-desc">上涨概率预测</div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">置信区间</div>
                            <div class="metric-value">{{ predictionConfidenceInterval }}</div>
                            <div class="metric-desc">预测结果置信范围</div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">特征重要性</div>
                            <div class="metric-value">{{ topFeature }}</div>
                            <div class="metric-desc">最重要预测因子</div>
                        </div>
                    </div>
                </div>

                <div class="mining-features">
                    <h5>关键特征分析</h5>
                    <div class="features-list">
                        <div v-for="feature in miningFeatures" :key="feature.name" class="feature-item">
                            <div class="feature-name">{{ feature.name }}</div>
                            <div class="feature-importance">
                                <div class="importance-bar">
                                    <div class="importance-fill" :style="{ width: feature.importance + '%' }"></div>
                                </div>
                                <div class="importance-value">{{ feature.importance }}%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mining-prediction">
                    <div class="prediction-result">
                        <div class="prediction-signal" :class="miningPredictionSignal">
                            <div class="signal-icon">
                                <svg
                                    v-if="miningPredictionSignal === 'bullish'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                >
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                                <svg
                                    v-else-if="miningPredictionSignal === 'bearish'"
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
                            <div class="signal-content">
                                <div class="signal-title">{{ getMiningSignalText(miningPredictionSignal) }}</div>
                                <div class="signal-probability">{{ miningPredictionProbability }}% 概率</div>
                            </div>
                        </div>

                        <div class="prediction-details">
                            <div class="detail-item">
                                <span class="label">预测周期:</span>
                                <span class="value">{{ miningPredictionPeriod }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">预期收益:</span>
                                <span class="value" :class="getReturnClass(miningExpectedReturn)">
                                    {{ miningExpectedReturn }}%
                                </span>
                            </div>
                            <div class="detail-item">
                                <span class="label">风险水平:</span>
                                <span class="value" :class="getRiskClass(miningRiskLevel)">
                                    {{ miningRiskLevel }}
                                </span>
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
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'

    interface Props {
        data: any
        symbol: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const comparisonMetric = ref('confidence')
    const showHistorical = ref(false)
    const miningAlgorithm = ref('random_forest')

    // 计算属性
    const decisionModels = computed(() => props.data?.decisionModels || [])
    const buffettData = computed(() => props.data?.buffett || {})
    const oneilData = computed(() => props.data?.oneil || {})
    const lynchData = computed(() => props.data?.lynch || {})
    const miningData = computed(() => props.data?.mining || {})

    // 模型对比相关
    const maxConfidence = computed(() => {
        const confidences = decisionModels.value.map((m: any) => m.confidence)
        return confidences.length > 0 ? Math.max(...confidences) : 100
    })

    // 巴菲特模型相关
    const buffettCriteria = computed(() => buffettData.value?.criteria || [])
    const buffettOverallScore = computed(() => buffettData.value?.overallScore || 0)
    const buffettRecommendations = computed(() => buffettData.value?.recommendations || [])

    // 欧内尔模型相关
    const canslimFactors = computed(() => oneilData.value?.factors || [])
    const oneilSignalStrength = computed(() => oneilData.value?.signalStrength || 0)
    const oneilFundamentalScore = computed(() => oneilData.value?.fundamentalScore || 0)
    const oneilTechnicalScore = computed(() => oneilData.value?.technicalScore || 0)
    const oneilMarketScore = computed(() => oneilData.value?.marketScore || 0)

    // 林奇模型相关
    const pegRatio = computed(() => lynchData.value?.pegRatio || 0)
    const peRatio = computed(() => lynchData.value?.peRatio || 0)
    const growthRate = computed(() => lynchData.value?.growthRate || 0)

    // 数据挖掘相关
    const miningAccuracy = computed(() => miningData.value?.accuracy || 0)
    const predictionProbability = computed(() => miningData.value?.predictionProbability || 0)
    const predictionConfidenceInterval = computed(() => miningData.value?.confidenceInterval || '±5%')
    const topFeature = computed(() => miningData.value?.topFeature || '成交量')
    const miningFeatures = computed(() => miningData.value?.features || [])
    const miningPredictionSignal = computed(() => miningData.value?.predictionSignal || 'neutral')
    const miningPredictionProbability = computed(() => miningData.value?.predictionProbability || 0)
    const miningPredictionPeriod = computed(() => miningData.value?.predictionPeriod || '1个月')
    const miningExpectedReturn = computed(() => miningData.value?.expectedReturn || 0)
    const miningRiskLevel = computed(() => miningData.value?.riskLevel || '中等')

    // 配置选项
    const metricOptions = [
        { label: '置信度', value: 'confidence' },
        { label: '预期收益', value: 'return' },
        { label: '风险等级', value: 'risk' },
        { label: '历史表现', value: 'historical' }
    ]

    const algorithmOptions = [
        { label: '随机森林', value: 'random_forest' },
        { label: '梯度提升', value: 'gradient_boosting' },
        { label: '神经网络', value: 'neural_network' },
        { label: '支持向量机', value: 'svm' }
    ]

    // 格式化函数
    const getBestModel = (): string => {
        if (!decisionModels.value.length) return '暂无'
        const best = decisionModels.value.reduce((prev: any, current: any) =>
            prev.confidence > current.confidence ? prev : current
        )
        return best.name
    }

    const getDecisionConfidence = (): string => {
        const best = decisionModels.value.find((m: any) => m.name === getBestModel())
        return best ? `${best.confidence}%` : 'N/A'
    }

    const getExpectedReturn = (): string => {
        const best = decisionModels.value.find((m: any) => m.name === getBestModel())
        return best ? `${best.expectedReturn}%` : 'N/A'
    }

    const getRiskAssessment = (): string => {
        const best = decisionModels.value.find((m: any) => m.name === getBestModel())
        return best ? best.riskLevel : 'N/A'
    }

    const getRiskVariant = (): 'rise' | 'fall' | 'default' => {
        const risk = getRiskAssessment()
        if (risk === '低风险') return 'rise'
        if (risk === '高风险') return 'fall'
        return 'default'
    }

    const getModelClass = (model: any): string => {
        return model.signal || 'neutral'
    }

    const getSignalClass = (signal: string): string => {
        if (signal === 'buy') return 'buy'
        if (signal === 'sell') return 'sell'
        return 'hold'
    }

    const getSignalText = (signal: string): string => {
        const texts: Record<string, string> = {
            buy: '买入',
            sell: '卖出',
            hold: '持有'
        }
        return texts[signal] || signal
    }

    const getReturnClass = (returnValue: number): string => {
        if (returnValue >= 10) return 'positive'
        if (returnValue <= -10) return 'negative'
        return 'neutral'
    }

    const getRiskClass = (risk: string): string => {
        if (risk === '低风险') return 'positive'
        if (risk === '高风险') return 'negative'
        return 'neutral'
    }

    const getModelCode = (modelName: string): string => {
        const codes: Record<string, string> = {
            巴菲特价值投资模型: 'B',
            欧内尔CANSLIM模型: 'O',
            林奇PEG估值模型: 'L',
            数据挖掘模型: 'M'
        }
        return codes[modelName] || modelName.charAt(0)
    }

    const getModelBarClass = (model: any): string => {
        if (model.signal === 'buy') return 'buy-signal'
        if (model.signal === 'sell') return 'sell-signal'
        return 'hold-signal'
    }

    const getCriterionClass = (criterion: any): string => {
        if (criterion.score >= 80) return 'excellent'
        if (criterion.score >= 60) return 'good'
        if (criterion.score >= 40) return 'fair'
        return 'poor'
    }

    const getBuffettScoreClass = (score: number): string => {
        if (score >= 80) return 'excellent'
        if (score >= 60) return 'good'
        if (score >= 40) return 'fair'
        return 'poor'
    }

    const getBuffettScoreText = (score: number): string => {
        if (score >= 80) return '优秀价值投资标的'
        if (score >= 60) return '良好价值投资标的'
        if (score >= 40) return '一般价值投资标的'
        return '不适合价值投资'
    }

    const getBuffettScoreDescription = (score: number): string => {
        if (score >= 80) return '满足巴菲特大部分投资标准，值得长期持有'
        if (score >= 60) return '基本符合巴菲特投资理念，可适当关注'
        if (score >= 40) return '部分符合投资标准，需要谨慎判断'
        return '不符合巴菲特投资原则，建议回避'
    }

    const getFactorScoreClass = (score: number): string => {
        if (score >= 80) return 'high'
        if (score >= 60) return 'medium'
        if (score >= 40) return 'low'
        return 'very-low'
    }

    const getOneilSignalClass = (strength: number): string => {
        if (strength >= 80) return 'strong'
        if (strength >= 60) return 'medium'
        return 'weak'
    }

    const getOneilSignalDescription = (strength: number): string => {
        if (strength >= 80) return 'CANSLIM因素表现优秀，强烈看好'
        if (strength >= 60) return 'CANSLIM因素表现良好，值得关注'
        if (strength >= 40) return 'CANSLIM因素表现一般，需要观察'
        return 'CANSLIM因素表现较差，建议谨慎'
    }

    const getPegClass = (peg: number): string => {
        if (peg <= 0.8) return 'positive'
        if (peg >= 2.0) return 'negative'
        return 'neutral'
    }

    const getPegDescription = (peg: number): string => {
        if (peg <= 0.8) return 'PEG ≤ 0.8，低估且高增长'
        if (peg <= 1.2) return 'PEG 0.8-1.2，估值合理'
        if (peg <= 2.0) return 'PEG 1.2-2.0，略显偏高'
        return 'PEG > 2.0，高估或低增长'
    }

    const getPegPosition = (): number => {
        // 将PEG转换为位置百分比 (0.5 = 10%, 3.0 = 90%)
        const position = Math.min(Math.max(((pegRatio.value - 0.5) / 2.5) * 80 + 10, 10), 90)
        return position
    }

    const getGrowthClass = (growth: number): string => {
        if (growth >= 20) return 'positive'
        if (growth >= 10) return 'neutral'
        return 'negative'
    }

    const getGrowthAssessment = (): string => {
        const peg = pegRatio.value
        if (peg <= 1.0) return '高成长性'
        if (peg <= 1.5) return '中高成长性'
        if (peg <= 2.0) return '中等成长性'
        return '低成长性'
    }

    const getInvestmentTiming = (): string => {
        const peg = pegRatio.value
        if (peg <= 0.8) return '强烈推荐买入'
        if (peg <= 1.2) return '适度推荐买入'
        if (peg <= 1.8) return '谨慎观望'
        return '建议等待回调'
    }

    const getAccuracyClass = (accuracy: number): string => {
        if (accuracy >= 80) return 'positive'
        if (accuracy >= 60) return 'neutral'
        return 'negative'
    }

    const getProbabilityClass = (probability: number): string => {
        if (probability >= 70) return 'positive'
        if (probability >= 50) return 'neutral'
        return 'negative'
    }

    const getMiningSignalText = (signal: string): string => {
        const texts: Record<string, string> = {
            bullish: '看涨信号',
            bearish: '看跌信号',
            neutral: '观望信号'
        }
        return texts[signal] || signal
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-decision-models {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   MODELS OVERVIEW - 模型概览
    // ============================================

    .models-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   MODEL COMPARISON - 模型对比分析
    // ============================================

    .model-comparison {
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

            .comparison-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .comparison-analysis {
            .models-performance {
                margin-bottom: var(--artdeco-spacing-5);

                .performance-table {
                    .table-header {
                        display: grid;
                        grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
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
                            grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
                            gap: var(--artdeco-spacing-4);
                            padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                background: rgba(212, 175, 55, 0.02);
                            }

                            &.buy {
                                border-left: 3px solid var(--artdeco-up);
                            }

                            &.sell {
                                border-left: 3px solid var(--artdeco-down);
                            }

                            .col-model {
                                .model-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .model-desc {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                }
                            }

                            .col-signal {
                                span {
                                    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                    border-radius: 4px;
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);

                                    &.buy {
                                        background: var(--artdeco-up);
                                        color: white;
                                    }

                                    &.sell {
                                        background: var(--artdeco-down);
                                        color: white;
                                    }

                                    &.hold {
                                        background: var(--artdeco-gold-primary);
                                        color: var(--artdeco-bg-dark);
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

                            .col-return {
                                span {
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

                            .col-risk {
                                span {
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
                        }
                    }
                }
            }

            .models-chart {
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

                    .models-performance-visualization {
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        padding: var(--artdeco-spacing-4);

                        .performance-bars {
                            flex: 1;
                            display: flex;
                            align-items: end;
                            justify-content: space-around;
                            gap: var(--artdeco-spacing-2);

                            .performance-bar {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .bar-container {
                                    width: 60px;
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

                                        &.buy-signal {
                                            background: linear-gradient(
                                                180deg,
                                                var(--artdeco-up),
                                                rgba(34, 197, 94, 0.6)
                                            );
                                        }

                                        &.sell-signal {
                                            background: linear-gradient(
                                                180deg,
                                                var(--artdeco-down),
                                                rgba(239, 68, 68, 0.6)
                                            );
                                        }

                                        &.hold-signal {
                                            background: linear-gradient(
                                                180deg,
                                                var(--artdeco-gold-primary),
                                                rgba(212, 175, 55, 0.6)
                                            );
                                        }
                                    }
                                }

                                .bar-label {
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    gap: var(--artdeco-spacing-1);

                                    .model-code {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xs);
                                        font-weight: 600;
                                        color: var(--artdeco-fg-primary);
                                    }

                                    .model-confidence {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
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
    //   BUFFETT MODEL - 巴菲特模型分析
    // ============================================

    .buffett-model {
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

        .buffett-analysis {
            .buffett-criteria {
                margin-bottom: var(--artdeco-spacing-5);

                .criteria-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .criterion-item {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        &.excellent {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.good {
                            border-left: 3px solid var(--artdeco-gold-primary);
                        }

                        &.fair {
                            border-left: 3px solid #f59e0b;
                        }

                        &.poor {
                            border-left: 3px solid var(--artdeco-down);
                        }

                        .criterion-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-3);

                            .criterion-name {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }

                            .criterion-score {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);

                                .score-bar {
                                    width: 80px;
                                    height: 8px;
                                    background: var(--artdeco-bg-muted);
                                    border-radius: 4px;
                                    overflow: hidden;

                                    .score-fill {
                                        height: 100%;
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            var(--artdeco-gold-secondary)
                                        );
                                        border-radius: 4px;
                                        transition: width var(--artdeco-transition-base);
                                    }
                                }

                                .score-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                    font-weight: 600;
                                }
                            }
                        }

                        .criterion-details {
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: var(--artdeco-spacing-2);

                            .detail-item {
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
                    }
                }
            }

            .buffett-insights {
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: var(--artdeco-spacing-5);

                .buffett-score {
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
                        h5 {
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
                    }
                }

                .buffett-recommendations {
                    h5 {
                        font-family: var(--artdeco-font-display);
                        font-size: var(--artdeco-font-size-md);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                        margin: 0 0 var(--artdeco-spacing-4) 0;
                    }

                    .recommendations-list {
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-3);

                        .recommendation-item {
                            display: flex;
                            gap: var(--artdeco-spacing-3);
                            padding: var(--artdeco-spacing-4);
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 6px;
                            transition: all var(--artdeco-transition-base);

                            &.buy {
                                border-left: 3px solid var(--artdeco-up);
                            }

                            &.hold {
                                border-left: 3px solid var(--artdeco-gold-primary);
                            }

                            &.sell {
                                border-left: 3px solid var(--artdeco-down);
                            }

                            &:hover {
                                border-color: var(--artdeco-gold-primary);
                                box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                            }

                            .rec-icon {
                                flex-shrink: 0;
                                width: 24px;
                                height: 24px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: var(--artdeco-fg-primary);
                            }

                            .rec-content {
                                flex: 1;

                                .rec-title {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .rec-description {
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
    }

    // ============================================
    //   ONEIL MODEL - 欧内尔模型分析
    // ============================================

    .oneil-model {
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

        .oneil-analysis {
            .canslim-factors {
                margin-bottom: var(--artdeco-spacing-5);

                .factors-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .factor-item {
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        padding: var(--artdeco-spacing-4);
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .factor-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: var(--artdeco-spacing-2);

                            .factor-letter {
                                width: 32px;
                                height: 32px;
                                background: var(--artdeco-gold-primary);
                                color: var(--artdeco-bg-dark);
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-lg);
                                font-weight: 600;
                            }

                            .factor-name {
                                flex: 1;
                                margin-left: var(--artdeco-spacing-3);
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-md);
                                font-weight: 600;
                                color: var(--artdeco-fg-primary);
                            }
                        }

                        .factor-score {
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            margin-bottom: var(--artdeco-spacing-2);

                            .score-bar {
                                flex: 1;
                                height: 8px;
                                background: var(--artdeco-bg-muted);
                                border-radius: 4px;
                                overflow: hidden;
                                margin-right: var(--artdeco-spacing-2);

                                .score-fill {
                                    height: 100%;
                                    border-radius: 4px;
                                    transition: width var(--artdeco-transition-base);

                                    &.high {
                                        background: linear-gradient(90deg, var(--artdeco-up), rgba(34, 197, 94, 0.6));
                                    }

                                    &.medium {
                                        background: linear-gradient(
                                            90deg,
                                            var(--artdeco-gold-primary),
                                            rgba(212, 175, 55, 0.6)
                                        );
                                    }

                                    &.low {
                                        background: linear-gradient(90deg, #f59e0b, rgba(245, 158, 11, 0.6));
                                    }

                                    &.very-low {
                                        background: linear-gradient(90deg, var(--artdeco-down), rgba(239, 68, 68, 0.6));
                                    }
                                }
                            }

                            .score-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                            }
                        }

                        .factor-description {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-secondary);
                            line-height: 1.5;
                        }
                    }
                }
            }

            .oneil-signal {
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: var(--artdeco-spacing-5);

                .signal-strength {
                    .strength-gauge {
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
                                        rgba(212, 175, 55, 0.9) 180deg,
                                        rgba(212, 175, 55, 0.9) 360deg
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
                                    color: var(--artdeco-gold-primary);
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

                    .signal-details {
                        h5 {
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

                        .signal-breakdown {
                            .breakdown-item {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                margin-bottom: var(--artdeco-spacing-2);

                                .label {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
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
                    }
                }
            }
        }
    }

    // ============================================
    //   LYNCH MODEL - 林奇模型分析
    // ============================================

    .lynch-model {
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

        .lynch-analysis {
            .peg-analysis {
                margin-bottom: var(--artdeco-spacing-5);

                .peg-metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .metric-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .metric-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .metric-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;
                            margin-bottom: var(--artdeco-spacing-1);

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

                        .metric-desc {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                        }
                    }
                }
            }

            .lynch-valuation {
                .valuation-zones {
                    margin-bottom: var(--artdeco-spacing-5);

                    .zones-visualization {
                        height: 100px;
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 8px;
                        position: relative;
                        padding: var(--artdeco-spacing-4);
                        margin-bottom: var(--artdeco-spacing-4);

                        // 几何装饰
                        @include artdeco-geometric-corners(
                            $color: var(--artdeco-gold-primary),
                            $size: 12px,
                            $border-width: 1px
                        );

                        .valuation-scale {
                            position: absolute;
                            top: 20px;
                            left: 20px;
                            right: 20px;
                            bottom: 20px;

                            .scale-marker {
                                position: absolute;
                                top: 0;
                                bottom: 0;
                                width: 2px;
                                background: var(--artdeco-fg-muted);

                                .marker-line {
                                    width: 100%;
                                    height: 20px;
                                    background: var(--artdeco-gold-primary);
                                    margin: 0 auto;
                                }

                                .marker-label {
                                    position: absolute;
                                    top: -25px;
                                    left: 50%;
                                    transform: translateX(-50%);
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);
                                    white-space: nowrap;
                                }
                            }
                        }

                        .current-position {
                            position: absolute;
                            top: 10px;
                            bottom: 10px;

                            .position-dot {
                                width: 12px;
                                height: 12px;
                                background: var(--artdeco-up);
                                border: 2px solid white;
                                border-radius: 50%;
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
                            }

                            .position-label {
                                position: absolute;
                                top: -20px;
                                left: 50%;
                                transform: translateX(-50%);
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

                .lynch-insights {
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
    }

    // ============================================
    //   MINING MODEL - 数据挖掘模型
    // ============================================

    .mining-model {
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

            .mining-controls {
                display: flex;
                align-items: center;
            }
        }

        .mining-analysis {
            .mining-results {
                margin-bottom: var(--artdeco-spacing-5);

                .results-metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .metric-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .metric-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .metric-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;
                            margin-bottom: var(--artdeco-spacing-1);

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

                        .metric-desc {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                        }
                    }
                }
            }

            .mining-features {
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

                .features-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-2);

                    .feature-item {
                        display: flex;
                        align-items: center;
                        gap: var(--artdeco-spacing-3);
                        padding: var(--artdeco-spacing-2);
                        background: var(--artdeco-bg-muted);
                        border-radius: 4px;

                        .feature-name {
                            flex: 1;
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-primary);
                            font-weight: 600;
                        }

                        .feature-importance {
                            display: flex;
                            align-items: center;
                            gap: var(--artdeco-spacing-2);

                            .importance-bar {
                                width: 80px;
                                height: 6px;
                                background: var(--artdeco-bg-card);
                                border-radius: 3px;
                                overflow: hidden;

                                .importance-fill {
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

                            .importance-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                                min-width: 35px;
                                text-align: right;
                            }
                        }
                    }
                }
            }

            .mining-prediction {
                .prediction-result {
                    display: grid;
                    grid-template-columns: 200px 1fr;
                    gap: var(--artdeco-spacing-5);

                    .prediction-signal {
                        padding: var(--artdeco-spacing-4);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        text-align: center;

                        &.bullish {
                            border-left: 3px solid var(--artdeco-up);
                        }

                        &.bearish {
                            border-left: 3px solid var(--artdeco-down);
                        }

                        &.neutral {
                            border-left: 3px solid var(--artdeco-gold-primary);
                        }

                        .signal-icon {
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .signal-title {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-lg);
                            font-weight: 600;
                            color: var(--artdeco-fg-primary);
                            margin-bottom: var(--artdeco-spacing-1);
                        }

                        .signal-probability {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-md);
                            color: var(--artdeco-gold-primary);
                            font-weight: 600;
                        }
                    }

                    .prediction-details {
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-2);

                        .detail-item {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: var(--artdeco-spacing-2);
                            background: var(--artdeco-bg-muted);
                            border-radius: 4px;

                            .label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-muted);
                                font-weight: 600;
                            }

                            .value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-sm);
                                color: var(--artdeco-fg-primary);
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
                    }
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-decision-models {
            gap: var(--artdeco-spacing-4);
        }

        .models-overview {
            grid-template-columns: 1fr;
        }

        .model-comparison {
            .comparison-analysis {
                .models-performance {
                    .performance-table {
                        .table-header,
                        .table-row {
                            grid-template-columns: 1fr;
                            gap: var(--artdeco-spacing-2);
                        }
                    }
                }
            }
        }

        .buffett-model {
            .buffett-analysis {
                .buffett-criteria {
                    .criteria-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .buffett-insights {
                    grid-template-columns: 1fr;
                }
            }
        }

        .oneil-model {
            .oneil-analysis {
                .canslim-factors {
                    .factors-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .lynch-model {
            .lynch-analysis {
                .peg-analysis {
                    .peg-metrics {
                        grid-template-columns: 1fr;
                    }
                }

                .lynch-insights {
                    .insights-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }

        .mining-model {
            .mining-analysis {
                .mining-results {
                    .results-metrics {
                        grid-template-columns: 1fr;
                    }
                }

                .mining-prediction {
                    .prediction-result {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
