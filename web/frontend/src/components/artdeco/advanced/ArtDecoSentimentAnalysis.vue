<template>
    <div class="artdeco-sentiment-analysis">
        <!-- 情绪分析概览 -->
        <div class="sentiment-overview">
            <ArtDecoStatCard
                label="整体情绪指数"
                :value="getOverallSentimentIndex()"
                description="综合市场情绪指标"
                variant="default"
            />

            <ArtDecoStatCard
                label="乐观占比"
                :value="getBullishPercentage()"
                description="乐观情绪投资者比例"
                variant="rise"
            />

            <ArtDecoStatCard
                label="悲观占比"
                :value="getBearishPercentage()"
                description="悲观情绪投资者比例"
                variant="fall"
            />

            <ArtDecoStatCard
                label="中性占比"
                :value="getNeutralPercentage()"
                description="中性情绪投资者比例"
                variant="default"
            />
        </div>

        <!-- 情绪雷达图 -->
        <ArtDecoCard class="sentiment-radar">
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
                        <h4>情绪雷达图</h4>
                        <p>SENTIMENT RADAR CHART</p>
                    </div>
                    <div class="radar-controls">
                        <ArtDecoSelect v-model="radarTimeframe" :options="timeframeOptions" size="sm" />
                        <ArtDecoSwitch v-model="showHistorical" label="显示历史" />
                    </div>
                </div>
            </template>

            <div class="radar-container">
                <div class="radar-placeholder">
                    <!-- 情绪雷达图可视化 -->
                    <div class="sentiment-radar-visualization">
                        <canvas ref="radarCanvas" class="radar-canvas"></canvas>
                        <div class="radar-overlay">
                            <div class="radar-legend">
                                <div class="legend-item">
                                    <div class="legend-color current"></div>
                                    <span>当前情绪</span>
                                </div>
                                <div v-if="showHistorical" class="legend-item">
                                    <div class="legend-color historical"></div>
                                    <span>历史平均</span>
                                </div>
                            </div>
                            <div class="radar-center">
                                <div class="center-value">{{ overallSentimentIndex }}</div>
                                <div class="center-label">情绪指数</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 研报分析 -->
        <ArtDecoCard class="research-reports">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>研报分析</h4>
                        <p>RESEARCH REPORTS ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="reports-analysis">
                <div class="reports-summary">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <div class="stat-label">研报总数</div>
                            <div class="stat-value">{{ totalReports }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">平均评级</div>
                            <div class="stat-value" :class="getRatingClass(avgRating)">
                                {{ getRatingText(avgRating) }}
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">目标价均值</div>
                            <div class="stat-value">{{ formatPrice(avgTargetPrice) }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">上涨空间</div>
                            <div class="stat-value" :class="getUpsideClass(avgUpside)">{{ avgUpside.toFixed(1) }}%</div>
                        </div>
                    </div>
                </div>

                <div class="reports-list">
                    <div class="reports-table">
                        <div class="table-header">
                            <div class="col-broker">券商</div>
                            <div class="col-rating">评级</div>
                            <div class="col-target">目标价</div>
                            <div class="col-date">日期</div>
                        </div>
                        <div class="table-body">
                            <div v-for="report in recentReports" :key="report.id" class="table-row">
                                <div class="col-broker">
                                    <div class="broker-name">{{ report.broker }}</div>
                                    <div class="report-title">{{ report.title }}</div>
                                </div>
                                <div class="col-rating">
                                    <span :class="getRatingClass(report.rating)">
                                        {{ getRatingText(report.rating) }}
                                    </span>
                                </div>
                                <div class="col-target">
                                    <div class="target-price">{{ formatPrice(report.targetPrice) }}</div>
                                    <div class="upside" :class="getUpsideClass(report.upside)">
                                        {{ report.upside.toFixed(1) }}%
                                    </div>
                                </div>
                                <div class="col-date">
                                    {{ formatDate(report.date) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 新闻情绪分析 -->
        <ArtDecoCard class="news-sentiment">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>新闻情绪分析</h4>
                        <p>NEWS SENTIMENT ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="news-analysis">
                <div class="sentiment-distribution">
                    <div class="distribution-chart">
                        <!-- 新闻情绪分布饼图 -->
                        <div class="pie-chart-placeholder">
                            <div class="pie-chart-visualization">
                                <div class="pie-segments">
                                    <div
                                        v-for="segment in sentimentSegments"
                                        :key="segment.type"
                                        class="pie-segment"
                                        :style="{
                                            background: getSentimentColor(segment.type),
                                            transform: `rotate(${segment.startAngle}deg)`,
                                            clipPath: `polygon(50% 50%, 50% 0%, ${segment.endAngle > 180 ? '100%' : Math.cos(((segment.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'} ${Math.sin(((segment.endAngle - 90) * Math.PI) / 180) * 50 + 50 + '%'})`
                                        }"
                                    >
                                        <div class="segment-label">
                                            <span class="type">{{ getSentimentTypeText(segment.type) }}</span>
                                            <span class="percentage">{{ segment.percentage }}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="pie-center">
                                    <div class="center-text">新闻情绪</div>
                                    <div class="center-value">{{ totalNews }}篇</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="sentiment-details">
                        <div class="sentiment-list">
                            <div v-for="segment in sentimentSegments" :key="segment.type" class="sentiment-item">
                                <div class="sentiment-info">
                                    <div
                                        class="sentiment-color"
                                        :style="{ background: getSentimentColor(segment.type) }"
                                    ></div>
                                    <div class="sentiment-name">{{ getSentimentTypeText(segment.type) }}</div>
                                </div>
                                <div class="sentiment-stats">
                                    <div class="stat-count">{{ segment.count }}篇</div>
                                    <div class="stat-percentage">{{ segment.percentage }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="news-timeline">
                    <h5>新闻时间线</h5>
                    <div class="timeline-container">
                        <div class="timeline">
                            <div
                                v-for="news in recentNews"
                                :key="news.id"
                                class="timeline-item"
                                :class="getSentimentClass(news.sentiment)"
                            >
                                <div
                                    class="timeline-dot"
                                    :style="{ background: getSentimentColor(news.sentiment) }"
                                ></div>
                                <div class="timeline-content">
                                    <div class="news-title">{{ news.title }}</div>
                                    <div class="news-meta">
                                        <span class="news-source">{{ news.source }}</span>
                                        <span class="news-time">{{ formatTime(news.time) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 人气指标分析 -->
        <ArtDecoCard class="popularity-indicators">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path
                                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                            ></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>人气指标分析</h4>
                        <p>POPULARITY INDICATORS ANALYSIS</p>
                    </div>
                </div>
            </template>

            <div class="popularity-analysis">
                <div class="popularity-metrics">
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-label">搜索热度指数</div>
                            <div class="metric-chart">
                                <!-- 搜索热度仪表图 -->
                                <div class="popularity-gauge">
                                    <div class="gauge-background">
                                        <div
                                            class="gauge-fill"
                                            :style="{ transform: `rotate(${(searchHeatIndex / 100) * 180 - 90}deg)` }"
                                            :class="getHeatClass(searchHeatIndex)"
                                        ></div>
                                    </div>
                                    <div class="gauge-center">
                                        <div class="gauge-value">{{ searchHeatIndex }}</div>
                                        <div class="gauge-label">搜索热度</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-item">
                            <div class="metric-label">讨论度指数</div>
                            <div class="metric-chart">
                                <!-- 讨论度条形图 -->
                                <div class="discussion-bars">
                                    <div class="discussion-bar">
                                        <div class="bar-label">论坛讨论</div>
                                        <div class="bar-container">
                                            <div class="bar-fill" :style="{ width: forumDiscussion + '%' }"></div>
                                        </div>
                                        <div class="bar-value">{{ forumDiscussion }}%</div>
                                    </div>
                                    <div class="discussion-bar">
                                        <div class="bar-label">社交媒体</div>
                                        <div class="bar-container">
                                            <div class="bar-fill" :style="{ width: socialMedia + '%' }"></div>
                                        </div>
                                        <div class="bar-value">{{ socialMedia }}%</div>
                                    </div>
                                    <div class="discussion-bar">
                                        <div class="bar-label">新闻报道</div>
                                        <div class="bar-container">
                                            <div class="bar-fill" :style="{ width: newsCoverage + '%' }"></div>
                                        </div>
                                        <div class="bar-value">{{ newsCoverage }}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="popularity-insights">
                    <h5>人气洞察</h5>
                    <div class="insights-grid">
                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">关注度趋势</div>
                                <div class="insight-value">{{ getAttentionTrend() }}</div>
                                <div class="insight-description">投资者关注度变化趋势</div>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path
                                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                                    ></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">市场共识度</div>
                                <div class="insight-value">{{ consensusLevel.toFixed(1) }}%</div>
                                <div class="insight-description">投资者意见一致程度</div>
                            </div>
                        </div>

                        <div class="insight-card">
                            <div class="insight-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path
                                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                    ></path>
                                </svg>
                            </div>
                            <div class="insight-content">
                                <div class="insight-title">情绪波动指数</div>
                                <div class="insight-value">{{ sentimentVolatility.toFixed(2) }}</div>
                                <div class="insight-description">市场情绪波动程度</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, nextTick, watch } from 'vue'
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
    const radarTimeframe = ref('1d')
    const showHistorical = ref(false)

    const radarCanvas = ref<HTMLCanvasElement>()

    // 计算属性
    const sentimentData = computed(() => props.data?.sentiment || {})
    const researchData = computed(() => props.data?.research || {})
    const newsData = computed(() => props.data?.news || {})
    const popularityData = computed(() => props.data?.popularity || {})

    // 情绪分析相关
    const overallSentimentIndex = computed(() => sentimentData.value?.overallIndex || 0)
    const bullishPercentage = computed(() => sentimentData.value?.bullish || 0)
    const bearishPercentage = computed(() => sentimentData.value?.bearish || 0)
    const neutralPercentage = computed(() => sentimentData.value?.neutral || 0)

    // 研报分析相关
    const totalReports = computed(() => researchData.value?.total || 0)
    const avgRating = computed(() => researchData.value?.avgRating || 0)
    const avgTargetPrice = computed(() => researchData.value?.avgTargetPrice || 0)
    const avgUpside = computed(() => researchData.value?.avgUpside || 0)
    const recentReports = computed(() => researchData.value?.recent || [])

    // 新闻分析相关
    const sentimentSegments = computed(() => newsData.value?.segments || [])
    const totalNews = computed(() => newsData.value?.total || 0)
    const recentNews = computed(() => newsData.value?.recent || [])

    // 人气指标相关
    const searchHeatIndex = computed(() => popularityData.value?.searchHeat || 0)
    const forumDiscussion = computed(() => popularityData.value?.forum || 0)
    const socialMedia = computed(() => popularityData.value?.social || 0)
    const newsCoverage = computed(() => popularityData.value?.news || 0)
    const consensusLevel = computed(() => popularityData.value?.consensus || 0)
    const sentimentVolatility = computed(() => popularityData.value?.volatility || 0)

    // 配置选项
    const timeframeOptions = [
        { label: '今日', value: '1d' },
        { label: '3日', value: '3d' },
        { label: '1周', value: '1w' },
        { label: '1月', value: '1M' }
    ]

    // 格式化函数
    const getOverallSentimentIndex = (): string => {
        return overallSentimentIndex.value.toFixed(1)
    }

    const getBullishPercentage = (): string => {
        return `${bullishPercentage.value.toFixed(1)}%`
    }

    const getBearishPercentage = (): string => {
        return `${bearishPercentage.value.toFixed(1)}%`
    }

    const getNeutralPercentage = (): string => {
        return `${neutralPercentage.value.toFixed(1)}%`
    }

    const getRatingClass = (rating: number): string => {
        if (rating >= 4) return 'buy'
        if (rating >= 3) return 'hold'
        return 'sell'
    }

    const getRatingText = (rating: number): string => {
        if (rating >= 4.5) return '强烈推荐'
        if (rating >= 4) return '推荐'
        if (rating >= 3.5) return '谨慎推荐'
        if (rating >= 3) return '中性'
        if (rating >= 2.5) return '谨慎减持'
        if (rating >= 2) return '减持'
        return '卖出'
    }

    const getUpsideClass = (upside: number): string => {
        if (upside >= 20) return 'strong-positive'
        if (upside >= 10) return 'positive'
        if (upside >= 0) return 'neutral'
        return 'negative'
    }

    const formatPrice = (price: number): string => {
        return price.toFixed(2)
    }

    const formatDate = (date: string): string => {
        return new Date(date).toLocaleDateString('zh-CN', {
            month: '2-digit',
            day: '2-digit'
        })
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const getSentimentColor = (type: string): string => {
        const colors: Record<string, string> = {
            positive: '#22c55e',
            negative: '#ef4444',
            neutral: '#6b7280'
        }
        return colors[type] || '#6b7280'
    }

    const getSentimentTypeText = (type: string): string => {
        const texts: Record<string, string> = {
            positive: '积极',
            negative: '消极',
            neutral: '中性'
        }
        return texts[type] || type
    }

    const getSentimentClass = (sentiment: string): string => {
        return sentiment
    }

    const getHeatClass = (heat: number): string => {
        if (heat >= 80) return 'high'
        if (heat >= 60) return 'medium'
        return 'low'
    }

    const getAttentionTrend = (): string => {
        const trend = popularityData.value?.attentionTrend || '稳定'
        return trend
    }

    // 雷达图渲染
    const renderRadarChart = async () => {
        await nextTick()
        if (!radarCanvas.value) return

        const ctx = radarCanvas.value.getContext('2d')
        if (!ctx) return

        // 这里可以集成Chart.js或其他雷达图库
        // 暂时绘制示例雷达图
        const canvas = radarCanvas.value
        const width = (canvas.width = canvas.offsetWidth)
        const height = (canvas.height = canvas.offsetHeight)

        ctx.clearRect(0, 0, width, height)

        const centerX = width / 2
        const centerY = height / 2
        const radius = (Math.min(width, height) / 2) * 0.8

        // 绘制背景圆圈
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.1)'
        ctx.lineWidth = 1

        for (let i = 1; i <= 5; i++) {
            ctx.beginPath()
            ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI)
            ctx.stroke()
        }

        // 绘制轴线
        const axes = 6
        for (let i = 0; i < axes; i++) {
            const angle = (i * 2 * Math.PI) / axes - Math.PI / 2
            const x = centerX + Math.cos(angle) * radius
            const y = centerY + Math.sin(angle) * radius

            ctx.beginPath()
            ctx.moveTo(centerX, centerY)
            ctx.lineTo(x, y)
            ctx.stroke()
        }

        // 绘制情绪雷达图
        const sentimentValues = [
            bullishPercentage.value / 100,
            neutralPercentage.value / 100,
            bearishPercentage.value / 100,
            0.5, // 示例值
            0.3, // 示例值
            0.7 // 示例值
        ]

        ctx.strokeStyle = '#D4AF37'
        ctx.lineWidth = 2
        ctx.fillStyle = 'rgba(212, 175, 55, 0.1)'
        ctx.beginPath()

        sentimentValues.forEach((value, index) => {
            const angle = (index * 2 * Math.PI) / axes - Math.PI / 2
            const x = centerX + Math.cos(angle) * radius * value
            const y = centerY + Math.sin(angle) * radius * value

            if (index === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })

        ctx.closePath()
        ctx.fill()
        ctx.stroke()
    }

    // 生命周期
    onMounted(() => {
        renderRadarChart()
    })

    // 监听数据变化重新渲染
    watch(
        () => props.data,
        () => {
            renderRadarChart()
        },
        { deep: true }
    )
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-sentiment-analysis {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   SENTIMENT OVERVIEW - 情绪概览
    // ============================================

    .sentiment-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   SENTIMENT RADAR - 情绪雷达图
    // ============================================

    .sentiment-radar {
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

            .radar-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .radar-container {
            .radar-placeholder {
                height: 400px;
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

                .sentiment-radar-visualization {
                    width: 100%;
                    height: 100%;
                    position: relative;

                    .radar-canvas {
                        width: 100% !important;
                        height: 100% !important;
                        background: transparent;
                    }

                    .radar-overlay {
                        position: absolute;
                        top: var(--artdeco-spacing-4);
                        right: var(--artdeco-spacing-4);
                        left: var(--artdeco-spacing-4);
                        bottom: var(--artdeco-spacing-4);
                        pointer-events: none;

                        .radar-legend {
                            position: absolute;
                            top: 0;
                            right: 0;
                            display: flex;
                            flex-direction: column;
                            gap: var(--artdeco-spacing-2);
                            background: rgba(0, 0, 0, 0.8);
                            padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                            border-radius: 6px;
                            backdrop-filter: blur(10px);

                            .legend-item {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-2);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-secondary);

                                .legend-color {
                                    width: 12px;
                                    height: 12px;
                                    border-radius: 2px;

                                    &.current {
                                        background: var(--artdeco-gold-primary);
                                    }

                                    &.historical {
                                        background: rgba(212, 175, 55, 0.6);
                                    }
                                }
                            }
                        }

                        .radar-center {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            text-align: center;

                            .center-value {
                                font-family: var(--artdeco-font-mono);
                                font-size: var(--artdeco-font-size-xl);
                                font-weight: 600;
                                color: var(--artdeco-gold-primary);
                                display: block;
                                margin-bottom: var(--artdeco-spacing-1);
                            }

                            .center-label {
                                font-family: var(--artdeco-font-body);
                                font-size: var(--artdeco-font-size-xs);
                                color: var(--artdeco-fg-muted);
                                text-transform: uppercase;
                                letter-spacing: var(--artdeco-tracking-wide);
                            }
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RESEARCH REPORTS - 研报分析
    // ============================================

    .research-reports {
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

        .reports-analysis {
            .reports-summary {
                margin-bottom: var(--artdeco-spacing-5);

                .summary-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: var(--artdeco-spacing-4);

                    .stat-item {
                        text-align: center;
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;

                        .stat-label {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-sm);
                            color: var(--artdeco-fg-muted);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin-bottom: var(--artdeco-spacing-2);
                        }

                        .stat-value {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xl);
                            font-weight: 600;

                            &.buy {
                                color: var(--artdeco-up);
                            }

                            &.hold {
                                color: var(--artdeco-gold-primary);
                            }

                            &.sell {
                                color: var(--artdeco-down);
                            }
                        }
                    }
                }
            }

            .reports-list {
                .reports-table {
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

                            .col-broker {
                                .broker-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .report-title {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    line-height: 1.4;
                                }
                            }

                            .col-rating {
                                span {
                                    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
                                    border-radius: 4px;
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;
                                    text-transform: uppercase;
                                    letter-spacing: var(--artdeco-tracking-wide);

                                    &.buy {
                                        background: var(--artdeco-up);
                                        color: white;
                                    }

                                    &.hold {
                                        background: var(--artdeco-gold-primary);
                                        color: var(--artdeco-bg-dark);
                                    }

                                    &.sell {
                                        background: var(--artdeco-down);
                                        color: white;
                                    }
                                }
                            }

                            .col-target {
                                .target-price {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-md);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                    display: block;
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .upside {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    font-weight: 600;

                                    &.strong-positive {
                                        color: var(--artdeco-up);
                                    }

                                    &.positive {
                                        color: #10b981;
                                    }

                                    &.neutral {
                                        color: var(--artdeco-fg-muted);
                                    }

                                    &.negative {
                                        color: var(--artdeco-down);
                                    }
                                }
                            }

                            .col-date {
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

    // ============================================
    //   NEWS SENTIMENT - 新闻情绪分析
    // ============================================

    .news-sentiment {
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

        .news-analysis {
            .sentiment-distribution {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: var(--artdeco-spacing-5);
                margin-bottom: var(--artdeco-spacing-5);

                .distribution-chart {
                    .pie-chart-placeholder {
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

                        .pie-chart-visualization {
                            position: relative;
                            width: 200px;
                            height: 200px;

                            .pie-segments {
                                position: absolute;
                                width: 100%;
                                height: 100%;
                                border-radius: 50%;

                                .pie-segment {
                                    position: absolute;
                                    width: 100%;
                                    height: 100%;
                                    clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%);
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;

                                    .segment-label {
                                        position: absolute;
                                        top: 40%;
                                        left: 50%;
                                        transform: translate(-50%, -50%);
                                        text-align: center;
                                        color: white;
                                        font-size: var(--artdeco-font-size-xs);
                                        font-weight: 600;
                                        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);

                                        .type {
                                            display: block;
                                            font-size: var(--artdeco-font-size-xs);
                                            margin-bottom: 2px;
                                        }

                                        .percentage {
                                            display: block;
                                            font-size: var(--artdeco-font-size-xs);
                                            opacity: 0.9;
                                        }
                                    }
                                }
                            }

                            .pie-center {
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                text-align: center;

                                .center-text {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    color: var(--artdeco-fg-muted);
                                    margin-bottom: var(--artdeco-spacing-1);
                                }

                                .center-value {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-lg);
                                    font-weight: 600;
                                    color: var(--artdeco-gold-primary);
                                }
                            }
                        }
                    }
                }

                .sentiment-details {
                    .sentiment-list {
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-3);

                        .sentiment-item {
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: var(--artdeco-spacing-3);
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 6px;
                            transition: all var(--artdeco-transition-base);

                            &:hover {
                                border-color: var(--artdeco-gold-primary);
                                box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                            }

                            .sentiment-info {
                                display: flex;
                                align-items: center;
                                gap: var(--artdeco-spacing-3);

                                .sentiment-color {
                                    width: 16px;
                                    height: 16px;
                                    border-radius: 3px;
                                }

                                .sentiment-name {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                }
                            }

                            .sentiment-stats {
                                text-align: right;

                                .stat-count {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    display: block;
                                }

                                .stat-percentage {
                                    font-family: var(--artdeco-font-mono);
                                    font-size: var(--artdeco-font-size-xs);
                                    color: var(--artdeco-fg-muted);
                                    display: block;
                                }
                            }
                        }
                    }
                }
            }

            .news-timeline {
                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .timeline-container {
                    .timeline {
                        position: relative;
                        padding-left: var(--artdeco-spacing-4);

                        &::before {
                            content: '';
                            position: absolute;
                            left: 8px;
                            top: 0;
                            bottom: 0;
                            width: 2px;
                            background: var(--artdeco-gold-primary);
                        }

                        .timeline-item {
                            position: relative;
                            margin-bottom: var(--artdeco-spacing-4);
                            padding-left: var(--artdeco-spacing-4);

                            .timeline-dot {
                                position: absolute;
                                left: -20px;
                                top: 8px;
                                width: 12px;
                                height: 12px;
                                border-radius: 50%;
                                border: 2px solid white;
                                box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
                            }

                            .timeline-content {
                                background: var(--artdeco-bg-card);
                                border: 1px solid var(--artdeco-border-default);
                                border-radius: 6px;
                                padding: var(--artdeco-spacing-3);

                                &:hover {
                                    border-color: var(--artdeco-gold-primary);
                                    box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                                }

                                .news-title {
                                    font-family: var(--artdeco-font-body);
                                    font-size: var(--artdeco-font-size-sm);
                                    font-weight: 600;
                                    color: var(--artdeco-fg-primary);
                                    margin-bottom: var(--artdeco-spacing-2);
                                    line-height: 1.4;
                                }

                                .news-meta {
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;

                                    .news-source {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-xs);
                                        color: var(--artdeco-fg-muted);
                                        font-weight: 600;
                                    }

                                    .news-time {
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
    //   POPULARITY INDICATORS - 人气指标分析
    // ============================================

    .popularity-indicators {
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

        .popularity-analysis {
            .popularity-metrics {
                margin-bottom: var(--artdeco-spacing-5);

                .metrics-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--artdeco-spacing-5);

                    .metric-item {
                        .metric-label {
                            font-family: var(--artdeco-font-display);
                            font-size: var(--artdeco-font-size-md);
                            font-weight: 600;
                            color: var(--artdeco-gold-primary);
                            text-transform: uppercase;
                            letter-spacing: var(--artdeco-tracking-wide);
                            margin: 0 0 var(--artdeco-spacing-4) 0;
                        }

                        .metric-chart {
                            height: 200px;
                            background: var(--artdeco-bg-card);
                            border: 1px solid var(--artdeco-border-default);
                            border-radius: 8px;
                            padding: var(--artdeco-spacing-4);
                            position: relative;
                            overflow: hidden;

                            // 几何装饰
                            @include artdeco-geometric-corners(
                                $color: var(--artdeco-gold-primary),
                                $size: 12px,
                                $border-width: 1px
                            );

                            .popularity-gauge {
                                position: relative;
                                width: 120px;
                                height: 120px;
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

                            .discussion-bars {
                                display: flex;
                                flex-direction: column;
                                gap: var(--artdeco-spacing-3);

                                .discussion-bar {
                                    display: flex;
                                    align-items: center;
                                    gap: var(--artdeco-spacing-3);

                                    .bar-label {
                                        font-family: var(--artdeco-font-body);
                                        font-size: var(--artdeco-font-size-sm);
                                        color: var(--artdeco-fg-primary);
                                        font-weight: 600;
                                        min-width: 80px;
                                    }

                                    .bar-container {
                                        flex: 1;
                                        height: 12px;
                                        background: var(--artdeco-bg-muted);
                                        border-radius: 6px;
                                        overflow: hidden;

                                        .bar-fill {
                                            height: 100%;
                                            background: linear-gradient(
                                                90deg,
                                                var(--artdeco-gold-primary),
                                                var(--artdeco-gold-secondary)
                                            );
                                            border-radius: 6px;
                                            transition: width var(--artdeco-transition-base);
                                        }
                                    }

                                    .bar-value {
                                        font-family: var(--artdeco-font-mono);
                                        font-size: var(--artdeco-font-size-sm);
                                        color: var(--artdeco-fg-muted);
                                        font-weight: 600;
                                        min-width: 50px;
                                        text-align: right;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .popularity-insights {
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
        .artdeco-sentiment-analysis {
            gap: var(--artdeco-spacing-4);
        }

        .sentiment-overview {
            grid-template-columns: 1fr;
        }

        .sentiment-radar {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .radar-controls {
                    width: 100%;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
            }
        }

        .research-reports {
            .reports-analysis {
                .reports-summary {
                    .summary-stats {
                        grid-template-columns: 1fr;
                    }
                }

                .reports-list {
                    .reports-table {
                        .table-header,
                        .table-row {
                            grid-template-columns: 1fr;
                            gap: var(--artdeco-spacing-2);
                        }
                    }
                }
            }
        }

        .news-sentiment {
            .news-analysis {
                .sentiment-distribution {
                    grid-template-columns: 1fr;
                }
            }
        }

        .popularity-indicators {
            .popularity-analysis {
                .popularity-metrics {
                    .metrics-grid {
                        grid-template-columns: 1fr;
                    }
                }

                .popularity-insights {
                    .insights-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
