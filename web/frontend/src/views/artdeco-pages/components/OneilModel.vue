<template>
    <ArtDecoCard class="oneil-model" title="欧内尔CANSLIM模型">
        <div class="oneil-analysis">
            <div class="factors-grid">
                <div v-for="factor in factors" :key="factor.letter" class="factor-item">
                    <div class="letter">{{ factor.letter }}</div>
                    <div class="content">
                        <div class="name">{{ factor.name }}</div>
                        <div class="score-bar">
                            <div class="score-fill" :style="{ width: factor.score + '%' }"></div>
                        </div>
                    </div>
                    <div class="score-text">{{ factor.score }}</div>
                </div>
            </div>
            <div class="signal-strength">
                <div class="gauge">
                    <div class="value">{{ strength }}</div>
                    <div class="label">信号强度</div>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    factors: Array,
    strength: Number
})
</script>

<style scoped lang="scss">
.oneil-analysis {
    display: grid;
    grid-template-columns: 1fr calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-10));
    gap: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2);
}
.factors-grid {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-3);
}
.factor-item {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-5) / 4);
    .letter {
        font-size: var(--artdeco-spacing-6);
        font-weight: bold;
        color: var(--artdeco-gold-primary);
        width: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-5) / 2);
    }
    .content {
        flex: 1;
        .name {
          font-size: var(--artdeco-text-sm);
          margin-bottom: var(--artdeco-spacing-1);
        }
        .score-bar {
            height: var(--artdeco-spacing-1);
            background: var(--artdeco-gold-opacity-10);
            .score-fill {
              height: 100%;
              background: var(--artdeco-gold-primary);
            }
        }
    }
}
.signal-strength {
    display: flex;
    align-items: center;
    justify-content: center;
    border-left: 1px solid var(--artdeco-gold-opacity-20);
    .gauge {
        text-align: center;
        .value {
            font-size: var(--artdeco-spacing-12);
            color: var(--artdeco-gold-primary);
        }
    }
}

@media (width <= 75rem) {
    .oneil-analysis {
        grid-template-columns: 1fr;
    }

    .signal-strength {
        border-left: none;
        border-top: 1px solid var(--artdeco-gold-opacity-20);
        padding-top: var(--artdeco-spacing-5);
    }
}

@media (width <= 48rem) {
    .factor-item {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
