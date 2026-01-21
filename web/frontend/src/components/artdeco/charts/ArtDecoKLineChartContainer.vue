<template>
    <ArtDecoCard class="artdeco-kline-container" :hoverable="false">
        <template #header>
            <div class="kline-header">
                <div class="header-left">
                    <h3 class="chart-title">{{ title || 'K线图表' }}</h3>
                    <ArtDecoBadge v-if="symbol" :text="symbol" variant="gold" />
                </div>
                <div class="header-right">
                    <span v-if="lastUpdate" class="update-time">更新时间: {{ formatTime(lastUpdate) }}</span>
                </div>
            </div>
        </template>

        <div class="kline-wrapper">
            <KLineChart
                ref="klineChartRef"
                :ohlcv-data="data"
                :indicators="indicators"
                :loading="loading"
                @indicator-remove="$emit('indicatorRemove', $event)"
            />

            <div v-if="!loading && (!data || !data.dates || data.dates.length === 0)" class="empty-state">
                <el-empty description="暂无数据" :image-size="120" />
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
    import { ref } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoBadge from '../base/ArtDecoBadge.vue'
    import KLineChart from '@/components/technical/KLineChart.vue'

    interface OHLCVData {
        dates: (string | Date)[]
        open: number[]
        high: number[]
        low: number[]
        close: number[]
        volume: number[]
        turnover?: number[]
    }

    interface Indicator {
        abbreviation: string
        panel_type: string
        outputs: unknown[]
    }

    interface Props {
        title?: string
        symbol?: string
        data?: OHLCVData
        indicators?: Indicator[]
        loading?: boolean
        lastUpdate?: Date | string | number
    }

    withDefaults(defineProps<Props>(), {
        title: '',
        symbol: '',
        data: undefined,
        indicators: () => [],
        loading: false,
        lastUpdate: undefined
    })

    defineEmits<{
        indicatorRemove: [event: unknown]
    }>()

    const klineChartRef = ref<InstanceType<typeof KLineChart>>()

    const formatTime = (time: Date | string | number): string => {
        if (!time) return ''
        const date = new Date(time)
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }

    defineExpose({
        chart: klineChartRef
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-kline-container {
      height: 600px;
      display: flex;
      flex-direction: column;
    }

    .kline-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: var(--artdeco-spacing-4);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
    }

    .chart-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-md); // 18px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
    }

    .update-time {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      color: var(--artdeco-fg-muted);
    }

    .kline-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
    }

    .empty-state {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--artdeco-fg-muted);
    }
</style>
