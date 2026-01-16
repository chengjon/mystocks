<template>
    <PageHeader title="高级分析" subtitle="ADVANCED QUANTITATIVE ANALYSIS" />

    <!-- 分析配置面板 -->
    <div class="card config-card">
        <div class="card-header">
            <div class="header-title">
                <div class="title-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        ></path>
                    </svg>
                </div>
                <span class="title-text">分析配置</span>
                <span class="title-sub">ANALYSIS CONFIGURATION</span>
            </div>
            <div class="action-buttons">
                <button class="button button-secondary" @click="runAnalysis" :class="{ loading: loading }">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    开始分析
                </button>
                <button class="button button-outline" @click="runBatchAnalysis" :class="{ loading: batchLoading }">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        ></path>
                    </svg>
                    批量分析
                </button>
            </div>
        </div>
        <div class="card-body">
            <div class="analysis-form">
                <div class="form-row">
                    <label class="form-label">股票代码</label>
                    <input type="text" v-model="form.symbol" placeholder="如: 000001" class="input" />
                </div>

                <div class="form-row">
                    <label class="form-label">分析模块</label>
                    <select v-model="form.analysisType" class="select">
                        <optgroup label="基础分析">
                            <option value="fundamental">基本面分析</option>
                            <option value="technical">技术面分析</option>
                        </optgroup>
                        <optgroup label="量化分析">
                            <option value="trading-signals">交易信号分析</option>
                            <option value="time-series">时序分析</option>
                            <option value="market-panorama">市场全景分析</option>
                            <option value="capital-flow">资金流向分析</option>
                            <option value="chip-distribution">筹码分布分析</option>
                        </optgroup>
                        <optgroup label="风险与评估">
                            <option value="anomaly-tracking">异常追踪分析</option>
                            <option value="financial-valuation">财务估值分析</option>
                            <option value="sentiment">情绪分析</option>
                            <option value="decision-models">决策模型分析</option>
                            <option value="multidimensional-radar">多维度雷达分析</option>
                        </optgroup>
                    </select>
                </div>

                <div class="form-row">
                    <label class="form-label">分析选项</label>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" v-model="form.includeRawData" />
                            <span>包含原始数据</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" v-model="form.enableRealtime" />
                            <span>启用实时更新</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 分析结果展示 -->
    <div v-if="analysisResult" class="analysis-results">
        <!-- 总体概览卡片 -->
        <div class="overview-grid">
            <div class="card overview-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                            </svg>
                        </div>
                        <span class="title-text">{{ getAnalysisTitle() }}</span>
                        <span class="title-sub">{{ form.symbol }}</span>
                    </div>
                    <el-tag :type="getOverallSignalType()" size="large">
                        {{ analysisResult.overall_signal || '分析中...' }}
                    </el-tag>
                </div>
                <div class="card-body">
                    <div class="overview-metrics">
                        <div v-for="metric in overviewMetrics" :key="metric.key" class="metric-item">
                            <div class="metric-value" :class="metric.class">{{ metric.value }}</div>
                            <div class="metric-label">{{ metric.label }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 健康状态卡片 -->
            <div class="card health-card">
                <div class="card-header">
                    <div class="header-title">
                        <span class="title-text">系统状态</span>
                        <span class="title-sub">SYSTEM HEALTH</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="health-indicators">
                        <div class="health-item">
                            <div class="health-icon" :class="healthStatus.database">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                                    <path d="m21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                                    <path d="m3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                                </svg>
                            </div>
                            <span>数据库</span>
                        </div>
                        <div class="health-item">
                            <div class="health-icon" :class="healthStatus.api">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                                </svg>
                            </div>
                            <span>API服务</span>
                        </div>
                        <div class="health-item">
                            <div class="health-icon" :class="healthStatus.gpu">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                                    <line x1="8" y1="21" x2="16" y2="21"></line>
                                    <line x1="12" y1="17" x2="12" y2="21"></line>
                                </svg>
                            </div>
                            <span>GPU加速</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 详细分析结果 -->
        <div class="detail-results">
            <!-- 基本面分析 -->
            <div v-if="analysisResult.fundamental" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path
                                    d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                ></path>
                            </svg>
                        </div>
                        <span class="title-text">基本面分析</span>
                        <span class="title-sub">FUNDAMENTAL ANALYSIS</span>
                    </div>
                </div>
                <div class="card-body">
                    <FundamentalAnalysisView :data="analysisResult.fundamental" />
                </div>
            </div>

            <!-- 技术面分析 -->
            <div v-if="analysisResult.technical" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M3 3v18h18"></path>
                                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
                            </svg>
                        </div>
                        <span class="title-text">技术面分析</span>
                        <span class="title-sub">TECHNICAL ANALYSIS</span>
                    </div>
                </div>
                <div class="card-body">
                    <TechnicalAnalysisView :data="analysisResult.technical" />
                </div>
            </div>

            <!-- 多维度雷达分析 -->
            <div v-if="analysisResult.multidimensional_radar" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polygon points="10,8 16,12 10,16 4,12"></polygon>
                            </svg>
                        </div>
                        <span class="title-text">多维度雷达分析</span>
                        <span class="title-sub">MULTIDIMENSIONAL RADAR</span>
                    </div>
                </div>
                <div class="card-body">
                    <RadarAnalysisView :data="analysisResult.multidimensional_radar" />
                </div>
            </div>

            <!-- 交易信号分析 -->
            <div v-if="analysisResult.trading_signals" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path
                                    d="M13 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                ></path>
                                <path d="M12 2v20"></path>
                            </svg>
                        </div>
                        <span class="title-text">交易信号分析</span>
                        <span class="title-sub">TRADING SIGNALS</span>
                    </div>
                </div>
                <div class="card-body">
                    <TradingSignalsView :data="analysisResult.trading_signals" />
                </div>
            </div>

            <!-- 时序分析 -->
            <div v-if="analysisResult.time_series" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <rect x="3" y="4" width="18" height="12" rx="2"></rect>
                                <path d="M7 8h.01"></path>
                                <path d="M12 8h.01"></path>
                                <path d="M17 8h.01"></path>
                                <path d="M7 12h.01"></path>
                                <path d="M12 12h.01"></path>
                                <path d="M17 12h.01"></path>
                            </svg>
                        </div>
                        <span class="title-text">时序分析</span>
                        <span class="title-sub">TIME SERIES ANALYSIS</span>
                    </div>
                </div>
                <div class="card-body">
                    <TimeSeriesView :data="analysisResult.time_series" />
                </div>
            </div>

            <!-- 市场全景分析 -->
            <div v-if="analysisResult.market_panorama" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="22" y1="12" x2="18" y2="12"></line>
                                <line x1="6" y1="12" x2="2" y2="12"></line>
                                <path
                                    d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"
                                ></path>
                            </svg>
                        </div>
                        <span class="title-text">市场全景分析</span>
                        <span class="title-sub">MARKET PANORAMA</span>
                    </div>
                </div>
                <div class="card-body">
                    <MarketPanoramaView :data="analysisResult.market_panorama" />
                </div>
            </div>

            <!-- 资金流向分析 -->
            <div v-if="analysisResult.capital_flow" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                            </svg>
                        </div>
                        <span class="title-text">资金流向分析</span>
                        <span class="title-sub">CAPITAL FLOW ANALYSIS</span>
                    </div>
                </div>
                <div class="card-body">
                    <CapitalFlowView :data="analysisResult.capital_flow" />
                </div>
            </div>

            <!-- 筹码分布分析 -->
            <div v-if="analysisResult.chip_distribution" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <rect x="7" y="7" width="3" height="3"></rect>
                                <rect x="14" y="7" width="3" height="3"></rect>
                                <rect x="7" y="14" width="3" height="3"></rect>
                                <rect x="14" y="14" width="3" height="3"></rect>
                            </svg>
                        </div>
                        <span class="title-text">筹码分布分析</span>
                        <span class="title-sub">CHIP DISTRIBUTION</span>
                    </div>
                </div>
                <div class="card-body">
                    <ChipDistributionView :data="analysisResult.chip_distribution" />
                </div>
            </div>

            <!-- 异常追踪分析 -->
            <div v-if="analysisResult.anomaly_tracking" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M12 8v4"></path>
                                <path d="M12 16h.01"></path>
                            </svg>
                        </div>
                        <span class="title-text">异常追踪分析</span>
                        <span class="title-sub">ANOMALY TRACKING</span>
                    </div>
                </div>
                <div class="card-body">
                    <AnomalyTrackingView :data="analysisResult.anomaly_tracking" />
                </div>
            </div>

            <!-- 财务估值分析 -->
            <div v-if="analysisResult.financial_valuation" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14,2 14,8 20,8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                                <polyline points="10,9 9,9 8,9"></polyline>
                            </svg>
                        </div>
                        <span class="title-text">财务估值分析</span>
                        <span class="title-sub">FINANCIAL VALUATION</span>
                    </div>
                </div>
                <div class="card-body">
                    <FinancialValuationView :data="analysisResult.financial_valuation" />
                </div>
            </div>

            <!-- 情绪分析 -->
            <div v-if="analysisResult.sentiment" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                                <line x1="9" y1="9" x2="9.01" y2="9"></line>
                                <line x1="15" y1="9" x2="15.01" y2="9"></line>
                            </svg>
                        </div>
                        <span class="title-text">情绪分析</span>
                        <span class="title-sub">SENTIMENT ANALYSIS</span>
                    </div>
                </div>
                <div class="card-body">
                    <SentimentAnalysisView :data="analysisResult.sentiment" />
                </div>
            </div>

            <!-- 决策模型分析 -->
            <div v-if="analysisResult.decision_models" class="card analysis-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path
                                    d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
                                ></path>
                            </svg>
                        </div>
                        <span class="title-text">决策模型分析</span>
                        <span class="title-sub">DECISION MODELS</span>
                    </div>
                </div>
                <div class="card-body">
                    <DecisionModelsView :data="analysisResult.decision_models" />
                </div>
            </div>
        </div>

        <!-- 批量分析结果 -->
        <div v-if="batchResults" class="batch-results">
            <div class="card batch-card">
                <div class="card-header">
                    <div class="header-title">
                        <div class="title-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path
                                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                                ></path>
                            </svg>
                        </div>
                        <span class="title-text">批量分析结果</span>
                        <span class="title-sub">BATCH ANALYSIS RESULTS</span>
                    </div>
                </div>
                <div class="card-body">
                    <BatchAnalysisView :results="batchResults" />
                </div>
            </div>
        </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="card empty-card">
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                ></path>
            </svg>
            <h3>高级量化分析中心</h3>
            <p>选择股票代码和分析模块，开始专业的量化分析</p>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import { ElMessage } from 'element-plus'
    import { advancedAnalysisApi } from '@/api/advancedAnalysis'
    import { PageHeader } from '@/components/shared'

    // 分析结果视图组件
    import FundamentalAnalysisView from './advanced-analysis/FundamentalAnalysisView.vue'
    import TechnicalAnalysisView from './advanced-analysis/TechnicalAnalysisView.vue'
    import RadarAnalysisView from './advanced-analysis/RadarAnalysisView.vue'
    import TradingSignalsView from './advanced-analysis/TradingSignalsView.vue'
    import TimeSeriesView from './advanced-analysis/TimeSeriesView.vue'
    import MarketPanoramaView from './advanced-analysis/MarketPanoramaView.vue'
    import CapitalFlowView from './advanced-analysis/CapitalFlowView.vue'
    import ChipDistributionView from './advanced-analysis/ChipDistributionView.vue'
    import AnomalyTrackingView from './advanced-analysis/AnomalyTrackingView.vue'
    import FinancialValuationView from './advanced-analysis/FinancialValuationView.vue'
    import SentimentAnalysisView from './advanced-analysis/SentimentAnalysisView.vue'
    import DecisionModelsView from './advanced-analysis/DecisionModelsView.vue'
    import BatchAnalysisView from './advanced-analysis/BatchAnalysisView.vue'

    interface AnalysisForm {
        symbol: string
        analysisType: string
        includeRawData: boolean
        enableRealtime: boolean
    }

    interface AnalysisResult {
        overall_signal?: string
        fundamental?: any
        technical?: any
        trading_signals?: any
        time_series?: any
        market_panorama?: any
        capital_flow?: any
        chip_distribution?: any
        anomaly_tracking?: any
        financial_valuation?: any
        sentiment?: any
        decision_models?: any
        multidimensional_radar?: any
    }

    interface HealthStatus {
        database: string
        api: string
        gpu: string
    }

    const loading = ref(false)
    const batchLoading = ref(false)
    const analysisResult = ref<AnalysisResult | null>(null)
    const batchResults = ref<any>(null)
    const realtimeInterval = ref<NodeJS.Timeout | null>(null)

    const form = ref<AnalysisForm>({
        symbol: '',
        analysisType: 'fundamental',
        includeRawData: false,
        enableRealtime: false
    })

    const healthStatus = ref<HealthStatus>({
        database: 'healthy',
        api: 'healthy',
        gpu: 'warning'
    })

    const overviewMetrics = computed(() => {
        if (!analysisResult.value) return []

        const metrics = []
        const result = analysisResult.value

        // 添加关键指标
        if (result.overall_signal) {
            metrics.push({
                key: 'signal',
                label: '总体信号',
                value: result.overall_signal,
                class: getSignalClass(result.overall_signal)
            })
        }

        return metrics
    })

    const getAnalysisTitle = (): string => {
        const titles: Record<string, string> = {
            fundamental: '基本面分析',
            technical: '技术面分析',
            'trading-signals': '交易信号分析',
            'time-series': '时序分析',
            'market-panorama': '市场全景分析',
            'capital-flow': '资金流向分析',
            'chip-distribution': '筹码分布分析',
            'anomaly-tracking': '异常追踪分析',
            'financial-valuation': '财务估值分析',
            sentiment: '情绪分析',
            'decision-models': '决策模型分析',
            'multidimensional-radar': '多维度雷达分析'
        }
        return titles[form.value.analysisType] || '高级分析'
    }

    const getOverallSignalType = (): 'success' | 'danger' | 'warning' | 'info' => {
        if (!analysisResult.value?.overall_signal) return 'info'
        const signal = analysisResult.value.overall_signal.toLowerCase()
        if (signal.includes('买') || signal.includes('强')) return 'success'
        if (signal.includes('卖') || signal.includes('弱')) return 'danger'
        return 'warning'
    }

    const getSignalClass = (signal: string): string => {
        if (!signal) return ''
        const signalLower = signal.toLowerCase()
        if (signalLower.includes('买') || signalLower.includes('强')) return 'positive'
        if (signalLower.includes('卖') || signalLower.includes('弱')) return 'negative'
        return 'neutral'
    }

    const runAnalysis = async (): Promise<void> => {
        if (!form.value.symbol) {
            ElMessage.warning('请输入股票代码')
            return
        }

        loading.value = true
        try {
            const params = {
                symbol: form.value.symbol,
                include_raw_data: form.value.includeRawData
            }

            const response = await (advancedAnalysisApi as any)[form.value.analysisType](params)

            if (response.data?.success) {
                analysisResult.value = response.data.data
                ElMessage.success('分析完成')

                // 如果启用了实时更新，设置定时器
                if (form.value.enableRealtime) {
                    startRealtimeUpdates()
                }
            } else {
                ElMessage.error(response.data?.message || '分析失败')
            }
        } catch (error: any) {
            console.error('分析失败:', error)
            ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
        } finally {
            loading.value = false
        }
    }

    const runBatchAnalysis = async (): Promise<void> => {
        if (!form.value.symbol) {
            ElMessage.warning('请输入股票代码')
            return
        }

        batchLoading.value = true
        try {
            const batchData = {
                analyses: ['fundamental', 'technical', 'trading-signals'],
                symbol: form.value.symbol,
                options: {
                    include_raw_data: form.value.includeRawData
                }
            }

            const response = await advancedAnalysisApi.batch(batchData)

            if (response.data?.success) {
                batchResults.value = response.data.data
                ElMessage.success('批量分析完成')
            } else {
                ElMessage.error(response.data?.message || '批量分析失败')
            }
        } catch (error: any) {
            console.error('批量分析失败:', error)
            ElMessage.error('批量分析失败: ' + (error.response?.data?.detail || error.message))
        } finally {
            batchLoading.value = false
        }
    }

    const startRealtimeUpdates = (): void => {
        if (realtimeInterval.value) {
            clearInterval(realtimeInterval.value)
        }

        realtimeInterval.value = setInterval(async () => {
            try {
                await runAnalysis()
            } catch (error) {
                console.error('实时更新失败:', error)
            }
        }, 30000) // 30秒更新一次
    }

    const stopRealtimeUpdates = (): void => {
        if (realtimeInterval.value) {
            clearInterval(realtimeInterval.value)
            realtimeInterval.value = null
        }
    }

    // WebSocket连接管理
    let websocket: WebSocket | null = null

    const connectWebSocket = () => {
        if (websocket) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws/events?channels=analysis:all,analysis:${form.value.symbol}`

        websocket = new WebSocket(wsUrl)

        websocket.onopen = () => {
            console.log('WebSocket connected for advanced analysis')
        }

        websocket.onmessage = event => {
            try {
                const data = JSON.parse(event.data)
                handleWebSocketMessage(data)
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error)
            }
        }

        websocket.onclose = () => {
            console.log('WebSocket disconnected')
            websocket = null
        }

        websocket.onerror = error => {
            console.error('WebSocket error:', error)
        }
    }

    const disconnectWebSocket = () => {
        if (websocket) {
            websocket.close()
            websocket = null
        }
    }

    const handleWebSocketMessage = (data: any) => {
        if (data.type === 'analysis_progress') {
            // 处理分析进度更新
            updateAnalysisProgress(data)
        } else if (data.type === 'analysis_complete') {
            // 处理分析完成事件
            updateAnalysisResult(data)
        }
    }

    const updateAnalysisProgress = (data: any) => {
        // 更新UI显示分析进度
        console.log('Analysis progress:', data)

        // 可以在这里更新进度条或状态指示器
        if (data.status === 'completed') {
            // 分析完成，更新结果
            if (data.data) {
                analysisResult.value = {
                    ...analysisResult.value,
                    [data.analysis_type]: data.data
                }
            }
        }
    }

    const updateAnalysisResult = (data: any) => {
        // 更新分析结果
        console.log('Analysis complete:', data)

        if (data.result) {
            analysisResult.value = {
                ...analysisResult.value,
                [data.analysis_type]: data.result
            }
        }
    }

    // 生命周期
    onMounted(() => {
        // 检查系统健康状态
        checkSystemHealth()

        // 连接WebSocket用于实时更新
        connectWebSocket()
    })

    onUnmounted(() => {
        stopRealtimeUpdates()
        disconnectWebSocket()
    })

    const checkSystemHealth = async (): Promise<void> => {
        try {
            // 这里可以添加实际的健康检查逻辑
            // 暂时使用模拟状态
            healthStatus.value = {
                database: 'healthy',
                api: 'healthy',
                gpu: 'healthy'
            }
        } catch (error) {
            console.error('健康检查失败:', error)
        }
    }
</script>
