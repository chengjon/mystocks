<template>
    <div class="radar-analysis">
        <!-- 雷达图容器 -->
        <div class="radar-container">
            <div class="radar-chart" ref="radarChart"></div>
            <div class="radar-legend">
                <div v-for="dimension in dimensions" :key="dimension.key" class="legend-item">
                    <div class="legend-color" :style="{ backgroundColor: dimension.color }"></div>
                    <span class="legend-label">{{ dimension.label }}</span>
                    <span class="legend-score">{{ dimension.score }}/100</span>
                </div>
            </div>
        </div>

        <!-- 维度详情 -->
        <div class="dimensions-detail">
            <div class="detail-header">
                <h4>维度分析详情</h4>
                <div class="overall-score">
                    <div class="score-circle" :style="{ background: getScoreGradient(overallScore) }">
                        <div class="score-value">{{ overallScore }}</div>
                        <div class="score-label">综合评分</div>
                    </div>
                </div>
            </div>

            <div class="dimensions-grid">
                <div v-for="dimension in dimensions" :key="dimension.key" class="dimension-card">
                    <div class="dimension-header">
                        <div class="dimension-icon" :style="{ color: dimension.color }">
                            <component :is="dimension.icon" />
                        </div>
                        <div class="dimension-info">
                            <h5>{{ dimension.label }}</h5>
                            <div class="dimension-score">{{ dimension.score }}/100</div>
                        </div>
                    </div>

                    <div class="dimension-progress">
                        <div class="progress-bar">
                            <div
                                class="progress-fill"
                                :style="{
                                    width: `${dimension.score}%`,
                                    backgroundColor: dimension.color
                                }"
                            ></div>
                        </div>
                        <div class="progress-labels">
                            <span>弱</span>
                            <span>中</span>
                            <span>强</span>
                        </div>
                    </div>

                    <div class="dimension-insights">
                        <div v-for="insight in dimension.insights" :key="insight.id" class="insight-item">
                            <el-tag :type="getInsightType(insight.type)" size="small">
                                {{ insight.label }}
                            </el-tag>
                            <span class="insight-desc">{{ insight.description }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 投资建议 -->
        <div class="investment-advice">
            <h4>投资建议</h4>
            <div class="advice-content">
                <div class="primary-advice">
                    <el-alert
                        :title="primaryAdvice.title"
                        :description="primaryAdvice.description"
                        :type="primaryAdvice.type"
                        show-icon
                        :closable="false"
                    />
                </div>

                <div class="secondary-advices">
                    <div v-for="advice in secondaryAdvices" :key="advice.id" class="advice-item">
                        <div class="advice-icon" :class="advice.type">
                            <svg
                                v-if="advice.type === 'success'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                            <svg
                                v-else-if="advice.type === 'warning'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                            </svg>
                            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="16" x2="12" y2="12"></line>
                                <line x1="12" y1="8" x2="12.01" y2="8"></line>
                            </svg>
                        </div>
                        <div class="advice-text">
                            <div class="advice-title">{{ advice.title }}</div>
                            <div class="advice-desc">{{ advice.description }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted, watch, nextTick } from 'vue'

    interface Props {
        data: any
    }

    const props = defineProps<Props>()
    const radarChart = ref<HTMLElement>()

    // 雷达图维度数据
    const dimensions = ref([
        {
            key: 'fundamental',
            label: '基本面',
            score: 75,
            color: '#67C23A',
            icon: 'TrendingUpIcon',
            insights: [
                { id: 1, type: 'success', label: '财务健康', description: '资产负债率合理，现金流稳定' },
                { id: 2, type: 'warning', label: '盈利增长', description: '净利润增速放缓，需要关注' }
            ]
        },
        {
            key: 'technical',
            label: '技术面',
            score: 82,
            color: '#E6A23C',
            icon: 'BarChartIcon',
            insights: [
                { id: 1, type: 'success', label: '趋势向上', description: '多条均线呈金叉格局' },
                { id: 2, type: 'info', label: '成交活跃', description: '成交量放大，市场关注度高' }
            ]
        },
        {
            key: 'sentiment',
            label: '情绪面',
            score: 65,
            color: '#F56C6C',
            icon: 'SmileIcon',
            insights: [
                { id: 1, type: 'warning', label: '市场情绪', description: '投资者情绪偏向谨慎' },
                { id: 2, type: 'info', label: '新闻关注', description: '近期利好消息较多' }
            ]
        },
        {
            key: 'capital_flow',
            label: '资金面',
            score: 78,
            color: '#409EFF',
            icon: 'DollarSignIcon',
            insights: [
                { id: 1, type: 'success', label: '主力流入', description: '大单资金持续净流入' },
                { id: 2, type: 'success', label: '北向资金', description: '外资持续增持态势' }
            ]
        },
        {
            key: 'industry',
            label: '行业面',
            score: 70,
            color: '#909399',
            icon: 'BriefcaseIcon',
            insights: [
                { id: 1, type: 'info', label: '行业景气', description: '所在行业整体向好' },
                { id: 2, type: 'warning', label: '政策风险', description: '行业政策不确定性较高' }
            ]
        },
        {
            key: 'macro',
            label: '宏观面',
            score: 68,
            color: '#C71585',
            icon: 'GlobeIcon',
            insights: [
                { id: 1, type: 'warning', label: '经济数据', description: '宏观经济数据波动较大' },
                { id: 2, type: 'info', label: '流动性', description: '市场流动性相对充足' }
            ]
        }
    ])

    const overallScore = ref(73)

    const primaryAdvice = ref({
        type: 'success' as 'success' | 'warning' | 'error',
        title: '建议买入',
        description: '综合分析显示，该股票具有较好的投资价值，建议投资者适量买入并长期持有。'
    })

    const secondaryAdvices = ref([
        {
            id: 1,
            type: 'success',
            title: '财务稳健',
            description: '公司基本面良好，盈利能力稳定，现金流健康。'
        },
        {
            id: 2,
            type: 'warning',
            title: '注意风险',
            description: '行业竞争激烈，需关注市场变化和政策调整。'
        },
        {
            id: 3,
            type: 'info',
            title: '长期看好',
            description: '符合长期投资逻辑，建议价值投资者关注。'
        }
    ])

    // 更新数据
    watch(
        () => props.data,
        newData => {
            if (newData) {
                updateDimensions(newData)
                nextTick(() => {
                    renderRadarChart()
                })
            }
        },
        { immediate: true }
    )

    const updateDimensions = (data: any) => {
        if (data.dimensions) {
            dimensions.value = data.dimensions.map((dim: any) => ({
                ...dim,
                insights: dim.insights || []
            }))
        }

        if (data.overall_score) {
            overallScore.value = data.overall_score
        }

        if (data.primary_advice) {
            primaryAdvice.value = data.primary_advice
        }

        if (data.secondary_advices) {
            secondaryAdvices.value = data.secondary_advices
        }
    }

    const renderRadarChart = () => {
        if (!radarChart.value) return

        // 这里实现雷达图的绘制逻辑
        // 使用Canvas或SVG绘制雷达图
        const canvas = document.createElement('canvas')
        canvas.width = 400
        canvas.height = 400
        radarChart.value.innerHTML = ''
        radarChart.value.appendChild(canvas)

        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const centerX = canvas.width / 2
        const centerY = canvas.height / 2
        const radius = Math.min(centerX, centerY) - 40
        const angles = dimensions.value.map((_, i) => (Math.PI * 2 * i) / dimensions.value.length - Math.PI / 2)

        // 绘制背景网格
        drawRadarGrid(ctx, centerX, centerY, radius, angles)

        // 绘制数据区域
        drawRadarData(ctx, centerX, centerY, radius, angles, dimensions.value)
    }

    const drawRadarGrid = (
        ctx: CanvasRenderingContext2D,
        centerX: number,
        centerY: number,
        radius: number,
        angles: number[]
    ) => {
        ctx.strokeStyle = '#E5E7EB'
        ctx.lineWidth = 1

        // 绘制同心圆
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath()
            ctx.arc(centerX, centerY, (radius * i) / 5, 0, Math.PI * 2)
            ctx.stroke()
        }

        // 绘制径向线
        angles.forEach(angle => {
            ctx.beginPath()
            ctx.moveTo(centerX, centerY)
            ctx.lineTo(centerX + Math.cos(angle) * radius, centerY + Math.sin(angle) * radius)
            ctx.stroke()
        })
    }

    const drawRadarData = (
        ctx: CanvasRenderingContext2D,
        centerX: number,
        centerY: number,
        radius: number,
        angles: number[],
        data: any[]
    ) => {
        ctx.beginPath()
        angles.forEach((angle, i) => {
            const score = data[i].score / 100
            const x = centerX + Math.cos(angle) * radius * score
            const y = centerY + Math.sin(angle) * radius * score

            if (i === 0) {
                ctx.moveTo(x, y)
            } else {
                ctx.lineTo(x, y)
            }
        })
        ctx.closePath()

        ctx.fillStyle = 'rgba(67, 200, 58, 0.3)'
        ctx.fill()
        ctx.strokeStyle = '#67C23A'
        ctx.lineWidth = 2
        ctx.stroke()
    }

    const getScoreGradient = (score: number): string => {
        if (score >= 80) return 'linear-gradient(135deg, #67C23A, #409EFF)'
        if (score >= 60) return 'linear-gradient(135deg, #E6A23C, #F56C6C)'
        return 'linear-gradient(135deg, #F56C6C, #C71585)'
    }

    const getInsightType = (type: string): 'success' | 'warning' | 'info' | 'danger' => {
        switch (type) {
            case 'success':
                return 'success'
            case 'warning':
                return 'warning'
            case 'error':
            case 'danger':
                return 'danger'
            default:
                return 'info'
        }
    }

    onMounted(() => {
        nextTick(() => {
            renderRadarChart()
        })
    })
</script>
