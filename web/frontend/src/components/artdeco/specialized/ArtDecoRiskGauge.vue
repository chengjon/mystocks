<template>
    <div class="artdeco-risk-gauge" :class="{ compact }">
        <div class="gauge-header">
            <h4 class="gauge-title">{{ title || 'RISK LEVEL' }}</h4>
            <ArtDecoBadge :text="riskLevelText" :variant="riskBadgeVariant" />
        </div>

        <div class="gauge-body">
            <div class="gauge-chart">
                <svg viewBox="0 0 200 120" class="gauge-svg">
                    <defs>
                        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stop-color="#00E676" />
                            <stop offset="50%" stop-color="#FFD700" />
                            <stop offset="100%" stop-color="#FF5252" />
                        </linearGradient>
                    </defs>

                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke="var(--artdeco-bg-primary)"
                        stroke-width="16"
                        stroke-linecap="round"
                    />

                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke="url(#gaugeGradient)"
                        stroke-width="16"
                        stroke-linecap="round"
                        :stroke-dasharray="`${dashArray} ${circumference}`"
                        :stroke-dashoffset="dashOffset"
                        class="gauge-progress"
                    />

                    <text x="100" y="85" text-anchor="middle" class="gauge-value" :fill="riskColor">
                        {{ riskScore }}%
                    </text>
                </svg>
            </div>

            <div v-if="showDetails" class="gauge-details">
                <div class="detail-item">
                    <span class="detail-label">VALUE AT RISK</span>
                    <span class="detail-value mono">{{ formatMoney(varValue) }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">EXPOSURE</span>
                    <span class="detail-value mono" :class="exposureClass">
                        {{ formatPercent(exposure) }}
                    </span>
                </div>
            </div>
        </div>

        <div v-if="showBreakdown" class="gauge-breakdown">
            <div class="breakdown-item" v-for="item in breakdown" :key="item.name">
                <div class="breakdown-label">{{ item.name }}</div>
                <div class="breakdown-bar">
                    <div
                        class="breakdown-fill"
                        :style="{ width: `${item.percentage}%`, backgroundColor: item.color }"
                    ></div>
                </div>
                <div class="breakdown-value mono">{{ formatPercent(item.percentage) }}</div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoBadge from '../base/ArtDecoBadge.vue'

    interface RiskBreakdown {
        name: string
        percentage: number
        color: string
    }

    interface Props {
        title?: string
        riskScore: number
        varValue?: number
        exposure?: number
        breakdown?: RiskBreakdown[]
        compact?: boolean
        showDetails?: boolean
        showBreakdown?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        title: '',
        riskScore: 0,
        varValue: 0,
        exposure: 0,
        breakdown: () => [],
        compact: false,
        showDetails: true,
        showBreakdown: false
    })

    const circumference = computed(() => {
        return Math.PI * 80
    })

    const dashArray = computed(() => {
        return (circumference.value * props.riskScore) / 100
    })

    const dashOffset = computed(() => {
        return circumference.value - dashArray.value
    })

    const riskColor = computed(() => {
        if (props.riskScore >= 70) return 'var(--artdeco-fall)'
        if (props.riskScore >= 40) return 'var(--artdeco-accent-gold)'
        return 'var(--artdeco-rise)'
    })

    const riskLevelText = computed(() => {
        if (props.riskScore >= 70) return 'HIGH'
        if (props.riskScore >= 40) return 'MEDIUM'
        return 'LOW'
    })

    const riskBadgeVariant = computed(() => {
        if (props.riskScore >= 70) return 'fall'
        if (props.riskScore >= 40) return 'gold'
        return 'rise'
    })

    const exposureClass = computed(() => {
        if (props.exposure >= 0.8) return 'profit-down'
        if (props.exposure >= 0.5) return 'gold'
        return 'profit-up'
    })

    const formatMoney = (value: number): string => {
        if (value >= 1000000) {
            return `¥${(value / 1000000).toFixed(2)}M`
        } else if (value >= 1000) {
            return `¥${(value / 1000).toFixed(2)}K`
        }
        return `¥${value.toFixed(2)}`
    }

    const formatPercent = (value: number): string => {
        return `${(value * 100).toFixed(1)}%`
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-risk-gauge {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-4);
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
    }

    .artdeco-risk-gauge.compact {
      padding: var(--artdeco-spacing-3);
    }

    .gauge-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: var(--artdeco-spacing-3);
    }

    .gauge-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .gauge-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
      align-items: center;
    }

    .gauge-chart {
      position: relative;
      width: 200px;
      height: 120px;
    }

    .gauge-svg {
      width: 100%;
      height: 100%;
    }

    .gauge-progress {
      transition: stroke-dasharray 0.6s ease-out, stroke-dashoffset 0.6s ease-out;
    }

    .gauge-value {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-xl) // 32px - Compact v3.1;
      font-weight: 700;
    }

    .gauge-details {
      display: flex;
      gap: var(--artdeco-spacing-5);
      width: 100%;
      justify-content: center;
    }

    .detail-item {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
      align-items: center;
    }

    .detail-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .detail-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-md) // 18px - Compact v3.1;
      font-weight: 700;
      color: var(--artdeco-fg-secondary);
    }

    .detail-value.profit-up {
      color: var(--artdeco-up);
    }

    .detail-value.profit-down {
      color: var(--artdeco-down);
    }

    .detail-value.gold {
      color: var(--artdeco-accent-gold);
    }

    .gauge-breakdown {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
    }

    .breakdown-item {
      display: grid;
      grid-template-columns: 1fr 2fr 80px;
      align-items: center;
      gap: var(--artdeco-spacing-3);
    }

    .breakdown-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      color: var(--artdeco-fg-secondary);
      text-transform: uppercase;
    }

    .breakdown-bar {
      height: 6px;
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      overflow: hidden;
    }

    .breakdown-fill {
      height: 100%;
      transition: width 0.6s ease-out;
    }

    .breakdown-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-secondary);
      text-align: right;
    }

    /* Compact variant */
    .artdeco-risk-gauge.compact .gauge-chart {
      width: 160px;
      height: 96px;
    }

    .artdeco-risk-gauge.compact .gauge-value {
      font-size: var(--artdeco-font-size-lg) // 24px - Compact v3.1;
    }

    .artdeco-risk-gauge.compact .gauge-details {
      gap: var(--artdeco-spacing-4);
    }

    .artdeco-risk-gauge.compact .detail-label {
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
    }

    .artdeco-risk-gauge.compact .detail-value {
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
    }
</style>
