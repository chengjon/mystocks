<template>
    <ArtDecoCard class="buffett-model" title="巴菲特价值投资模型">
        <div class="buffett-analysis">
            <div class="criteria-grid">
                <div v-for="criterion in criteria" :key="criterion.name" class="criterion-item">
                    <div class="criterion-header">
                        <span class="name">{{ criterion.name }}</span>
                        <span class="score">{{ criterion.score }}/100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-fill" :style="{ width: criterion.score + '%' }"></div>
                    </div>
                    <div class="criterion-details">
                        <span>当前: {{ criterion.currentValue }}</span>
                        <span>标准: {{ criterion.standardValue }}</span>
                    </div>
                </div>
            </div>
            <div class="overall-score">
                <div class="gauge">
                    <div class="value">{{ overallScore }}</div>
                    <div class="label">价值评分</div>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    criteria: Array,
    overallScore: Number
})
</script>

<style scoped lang="scss">
.buffett-analysis {
    display: grid;
    grid-template-columns: 1fr 200px;
    gap: 30px;
}
.criteria-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}
.criterion-item {
    .criterion-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .score-bar {
        height: 4px;
        background: rgba(212, 175, 55, 0.1);
        margin-bottom: 8px;
        .score-fill {
            height: 100%;
            background: var(--artdeco-gold-primary);
        }
    }
    .criterion-details {
        font-size: 12px;
        color: var(--artdeco-fg-muted);
        display: flex;
        justify-content: space-between;
    }
}
.overall-score {
    display: flex;
    align-items: center;
    justify-content: center;
    border-left: 1px solid rgba(212, 175, 55, 0.2);
    .gauge {
        text-align: center;
        .value {
            font-size: 48px;
            font-family: var(--artdeco-font-display);
            color: var(--artdeco-gold-primary);
        }
    }
}
</style>
