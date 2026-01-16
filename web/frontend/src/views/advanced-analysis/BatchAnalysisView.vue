<template>
    <div class="batch-analysis">
        <div class="batch-summary">
            <div class="summary-stats">
                <div class="stat-item">
                    <div class="stat-value">{{ analysesCount }}</div>
                    <div class="stat-label">分析模块</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ completedAnalyses }}</div>
                    <div class="stat-label">完成分析</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ avgScore }}</div>
                    <div class="stat-label">平均评分</div>
                </div>
            </div>
        </div>

        <div class="batch-results">
            <div v-for="(result, analysisType) in results" :key="analysisType" class="analysis-result">
                <div class="result-header">
                    <h5>{{ getAnalysisName(String(analysisType)) }}</h5>
                    <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                        {{ result.success ? '成功' : '失败' }}
                    </el-tag>
                </div>

                <div v-if="result.success" class="result-content">
                    <div class="key-metrics">
                        <div v-for="metric in getKeyMetrics(result.data)" :key="metric.key" class="metric">
                            <span class="metric-label">{{ metric.label }}:</span>
                            <span class="metric-value">{{ metric.value }}</span>
                        </div>
                    </div>
                </div>

                <div v-else class="result-error">
                    {{ result.error || '分析失败' }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        results: any
    }

    const props = defineProps<Props>()

    const results = computed(() => props.results || {})

    const analysesCount = computed(() => Object.keys(results.value).length)

    const completedAnalyses = computed(
        () => Object.values(results.value).filter((result: any) => result.success).length
    )

    const avgScore = computed(() => {
        const scores = Object.values(results.value)
            .filter((result: any) => result.success && result.data?.overall_score)
            .map((result: any) => result.data.overall_score)

        if (scores.length === 0) return 'N/A'
        return Math.round(scores.reduce((a: number, b: number) => a + b, 0) / scores.length)
    })

    const getAnalysisName = (analysisType: string): string => {
        const names: Record<string, string> = {
            fundamental: '基本面分析',
            technical: '技术面分析',
            'trading-signals': '交易信号分析'
        }
        return names[analysisType] || analysisType
    }

    const getKeyMetrics = (data: any) => {
        if (!data) return []

        const metrics = []
        if (data.overall_signal) {
            metrics.push({ key: 'signal', label: '信号', value: data.overall_signal })
        }
        if (data.score) {
            metrics.push({ key: 'score', label: '评分', value: data.score })
        }

        return metrics.slice(0, 3)
    }
</script>
