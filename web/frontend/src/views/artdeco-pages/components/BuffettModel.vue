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
    grid-template-columns: 1fr calc(var(--artdeco-spacing-20) * 3);
    gap: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}
.criteria-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--artdeco-spacing-5);
}
.criterion-item {
    .criterion-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: var(--artdeco-spacing-2);
    }
    .score-bar {
        height: var(--artdeco-spacing-1);
        background: var(--artdeco-gold-opacity-10);
        margin-bottom: var(--artdeco-spacing-2);
        .score-fill {
            height: 100%;
            background: var(--artdeco-gold-primary);
        }
    }
    .criterion-details {
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        display: flex;
        justify-content: space-between;
    }
}
.overall-score {
    display: flex;
    align-items: center;
    justify-content: center;
    border-left: 1px solid var(--artdeco-gold-opacity-20);
    .gauge {
        text-align: center;
        .value {
            font-size: var(--artdeco-spacing-12);
            font-family: var(--artdeco-font-display);
            color: var(--artdeco-gold-primary);
        }
    }
}

@media (width <= 75rem) {
    .buffett-analysis,
    .criteria-grid {
        grid-template-columns: 1fr;
    }

    .overall-score {
        border-left: none;
        border-top: 1px solid var(--artdeco-gold-opacity-20);
        padding-top: var(--artdeco-spacing-5);
    }
}

@media (width <= 48rem) {
    .criterion-item .criterion-details {
        flex-direction: column;
        gap: var(--artdeco-spacing-1);
    }
}
</style>
