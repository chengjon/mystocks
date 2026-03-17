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
                                        v-for="(segment, _idx) in sentimentSegments"
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
                                v-for="(news, _idx) in recentNews"
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
    import { computed } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import _ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import { useArtDecoSentimentAnalysis } from './composables/useArtDecoSentimentAnalysis'

    interface ReportItem {
        id: string | number
        broker: string
        title: string
        rating: number
        targetPrice: number
        upside: number
        date: string
    }

    interface SegmentItem {
        type: string
        startAngle: number
        endAngle: number
        percentage: number
        count: number
    }

    interface NewsItem {
        id: string | number
        sentiment: string
        title: string
        source: string
        time: string
    }

	    const {
	        radarTimeframe,
	        showHistorical,
	        radarCanvas,
	        overallSentimentIndex,
	        totalReports,
        avgRating: rawAvgRating,
        avgTargetPrice: rawAvgTargetPrice,
        avgUpside: rawAvgUpside,
        recentReports: rawRecentReports,
        sentimentSegments: rawSentimentSegments,
        totalNews,
        recentNews: rawRecentNews,
        searchHeatIndex: rawSearchHeatIndex,
        forumDiscussion: rawForumDiscussion,
        socialMedia: rawSocialMedia,
        newsCoverage: rawNewsCoverage,
        consensusLevel: rawConsensusLevel,
        sentimentVolatility: rawSentimentVolatility,
        timeframeOptions,
        getOverallSentimentIndex,
        getBullishPercentage,
        getBearishPercentage,
        getNeutralPercentage,
        getRatingClass,
        getRatingText,
        getUpsideClass,
        formatPrice,
        formatDate,
        formatTime,
	        getSentimentColor,
	        getSentimentTypeText,
	        getSentimentClass,
	        getHeatClass,
	        getAttentionTrend
	    } = useArtDecoSentimentAnalysis()

    const avgRating = computed((): number => Number(rawAvgRating.value || 0))
    const avgTargetPrice = computed((): number => Number(rawAvgTargetPrice.value || 0))
    const avgUpside = computed((): number => Number(rawAvgUpside.value || 0))

    const recentReports = computed((): ReportItem[] => {
        return rawRecentReports.value.map((report) => ({
            id: report.id,
            broker: report.broker,
            title: report.title,
            rating: report.rating,
            targetPrice: report.targetPrice,
            upside: report.upside,
            date: report.date
        }))
    })

    const sentimentSegments = computed((): SegmentItem[] => {
        return rawSentimentSegments.value.map((segment) => ({
            type: segment.type,
            startAngle: segment.startAngle,
            endAngle: segment.endAngle,
            percentage: segment.percentage,
            count: segment.count
        }))
    })

    const recentNews = computed((): NewsItem[] => {
        return rawRecentNews.value.map((news) => ({
            id: news.id,
            sentiment: news.sentiment,
            title: news.title,
            source: news.source,
            time: news.time
        }))
    })

    const searchHeatIndex = computed((): number => Number(rawSearchHeatIndex.value || 0))
    const forumDiscussion = computed((): number => Number(rawForumDiscussion.value || 0))
    const socialMedia = computed((): number => Number(rawSocialMedia.value || 0))
    const newsCoverage = computed((): number => Number(rawNewsCoverage.value || 0))
    const consensusLevel = computed((): number => Number(rawConsensusLevel.value || 0))
    const sentimentVolatility = computed((): number => Number(rawSentimentVolatility.value || 0))
</script>

<style scoped lang="scss">
@import './styles/ArtDecoSentimentAnalysis';
</style>
