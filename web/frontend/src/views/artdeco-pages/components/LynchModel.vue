<template>
    <ArtDecoCard class="lynch-model" title="林奇PEG估值模型">
        <div class="lynch-analysis">
            <div class="metrics">
                <div class="metric-card">
                    <div class="label">PEG比率</div>
                    <div class="value" :class="getPegClass(peg)">{{ peg.toFixed(2) }}</div>
                </div>
                <div class="metric-card">
                    <div class="label">市盈率 (PE)</div>
                    <div class="value">{{ pe.toFixed(1) }}</div>
                </div>
                <div class="metric-card">
                    <div class="label">增长率 (G)</div>
                    <div class="value">{{ growth.toFixed(1) }}%</div>
                </div>
            </div>
            <div class="valuation-scale">
                <div class="scale-track">
                    <div class="marker undervaluated" style="left: 25%">低估</div>
                    <div class="marker fair" style="left: 50%">合理</div>
                    <div class="marker overvaluated" style="left: 75%">高估</div>
                    <div class="pointer" :style="{ left: getPegPosition(peg) + '%' }"></div>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    peg: Number,
    pe: Number,
    growth: Number
})

function getPegClass(v) {
    if (v < 1) return 'good'
    if (v < 1.5) return 'neutral'
    return 'bad'
}

function getPegPosition(v) {
    return Math.min(Math.max(v * 50, 5), 95)
}
</script>

<style scoped lang="scss">
.metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--artdeco-spacing-5);
    margin-bottom: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2);
}
.metric-card {
    background: var(--artdeco-gold-opacity-05);
    padding: var(--artdeco-spacing-5);
    text-align: center;
    .label {
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-fg-muted);
      margin-bottom: calc(var(--artdeco-spacing-5) / 2);
    }
    .value {
      font-size: var(--artdeco-spacing-6);
      font-weight: bold;
    }
    .value.good { color: var(--artdeco-rise); }
}
.scale-track {
    height: calc(var(--artdeco-spacing-5) / 2);
    background: linear-gradient(to right, var(--artdeco-down), var(--artdeco-gold-light), var(--artdeco-up));
    position: relative;
    border-radius: calc(var(--artdeco-spacing-5) / 4);
    .marker {
      position: absolute;
      top: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4);
      font-size: calc(var(--artdeco-spacing-5) / 2);
      transform: translateX(-50%);
    }
    .pointer {
        position: absolute;
        top: calc(var(--artdeco-spacing-5) / -4);
        width: var(--artdeco-spacing-1);
        height: var(--artdeco-spacing-5);
        background: var(--artdeco-fg-primary);
        border: 1px solid var(--artdeco-border-default);
    }
}

@media (width <= 75rem) {
    .metrics {
        grid-template-columns: 1fr;
    }
}

@media (width <= 48rem) {
    .scale-track .marker {
        font-size: calc(var(--artdeco-spacing-5) / 2 - var(--artdeco-spacing-px));
    }
}
</style>
