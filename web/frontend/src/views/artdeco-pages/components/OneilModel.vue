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
    grid-template-columns: 1fr 200px;
    gap: 30px;
}
.factors-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.factor-item {
    display: flex;
    align-items: center;
    gap: 15px;
    .letter {
        font-size: 24px;
        font-weight: bold;
        color: var(--artdeco-gold-primary);
        width: 30px;
    }
    .content {
        flex: 1;
        .name { font-size: 14px; margin-bottom: 4px; }
        .score-bar {
            height: 4px;
            background: rgba(212, 175, 55, 0.1);
            .score-fill { height: 100%; background: var(--artdeco-gold-primary); }
        }
    }
}
.signal-strength {
    display: flex;
    align-items: center;
    justify-content: center;
    border-left: 1px solid rgba(212, 175, 55, 0.2);
    .gauge {
        text-align: center;
        .value {
            font-size: 48px;
            color: var(--artdeco-gold-primary);
        }
    }
}
</style>
