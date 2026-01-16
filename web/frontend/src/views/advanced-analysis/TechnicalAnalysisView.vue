<template>
    <div class="technical-analysis">
        <div class="indicators-grid">
            <div v-for="indicator in indicators" :key="indicator.name" class="indicator-card">
                <div class="indicator-header">
                    <h5>{{ indicator.name }}</h5>
                    <el-tag :type="getSignalType(indicator.signal)" size="small">
                        {{ indicator.signal }}
                    </el-tag>
                </div>
                <div class="indicator-value">{{ indicator.value }}</div>
                <div class="indicator-description">{{ indicator.description }}</div>
            </div>
        </div>

        <div class="trend-analysis">
            <h4>趋势分析</h4>
            <div class="trend-chart">
                <!-- 这里可以放置技术指标图表 -->
                <div class="chart-placeholder">
                    <svg viewBox="0 0 400 200" class="trend-svg">
                        <path
                            d="M0,150 L50,120 L100,140 L150,100 L200,80 L250,90 L300,60 L350,70 L400,50"
                            stroke="#67C23A"
                            stroke-width="2"
                            fill="none"
                        />
                        <path
                            d="M0,160 L50,140 L100,150 L150,130 L200,110 L250,120 L300,100 L350,110 L400,90"
                            stroke="#E6A23C"
                            stroke-width="2"
                            fill="none"
                        />
                    </svg>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        data: any
    }

    const props = defineProps<Props>()

    const indicators = computed(() => {
        if (!props.data?.indicators) return []

        return props.data.indicators.map((indicator: any) => ({
            name: indicator.name,
            value: indicator.value,
            signal: indicator.signal || '中性',
            description: indicator.description || ''
        }))
    })

    const getSignalType = (signal: string): 'success' | 'warning' | 'danger' | 'info' => {
        if (!signal) return 'info'
        const signalLower = signal.toLowerCase()
        if (signalLower.includes('买') || signalLower.includes('强')) return 'success'
        if (signalLower.includes('卖') || signalLower.includes('弱')) return 'danger'
        return 'warning'
    }
</script>
