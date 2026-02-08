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
    gap: 20px;
    margin-bottom: 30px;
}
.metric-card {
    background: rgba(212, 175, 55, 0.05);
    padding: 20px;
    text-align: center;
    .label { font-size: 12px; color: var(--artdeco-fg-muted); margin-bottom: 10px; }
    .value { font-size: 24px; font-weight: bold; }
    .value.good { color: var(--artdeco-rise); }
}
.scale-track {
    height: 10px;
    background: linear-gradient(to right, #4caf50, #ffeb3b, #f44336);
    position: relative;
    border-radius: 5px;
    .marker { position: absolute; top: 15px; font-size: 10px; transform: translateX(-50%); }
    .pointer {
        position: absolute;
        top: -5px;
        width: 4px;
        height: 20px;
        background: white;
        border: 1px solid black;
    }
}
</style>
