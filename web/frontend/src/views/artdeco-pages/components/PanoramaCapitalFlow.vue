<template>
    <ArtDecoCard class="capital-flow" title="资金流向全景">
        <div class="flow-overview">
            <div class="main-flows">
                <div class="flow-item">
                    <div class="label">北向资金</div>
                    <div class="value" :class="north >= 0 ? 'rise' : 'fall'">{{ north }} 亿</div>
                </div>
                <div class="flow-item">
                    <div class="label">南向资金</div>
                    <div class="value" :class="south >= 0 ? 'rise' : 'fall'">{{ south }} 亿</div>
                </div>
                <div class="flow-item">
                    <div class="label">主力净流入</div>
                    <div class="value" :class="mainForce >= 0 ? 'rise' : 'fall'">{{ mainForce }} 亿</div>
                </div>
            </div>
            <div class="sector-flows">
                <div v-for="sector in sectors" :key="sector.name" class="sector-tag" :class="sector.flow >= 0 ? 'in' : 'out'">
                    {{ sector.name }} {{ sector.flow > 0 ? '+' : '' }}{{ sector.flow }}
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    north: Number,
    south: Number,
    mainForce: Number,
    sectors: Array
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
.main-flows {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--artdeco-spacing-5);
    margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-radius-md) - var(--artdeco-radius-sm));
}
.flow-item {
    text-align: center;
    .label {
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-fg-muted);
      margin-bottom: calc(var(--artdeco-spacing-xs) + var(--artdeco-spacing-px));
    }
    .value {
      font-size: calc(var(--artdeco-text-base) + var(--artdeco-radius-md));
      font-weight: bold;
    }
    .value.rise { color: var(--artdeco-rise); }
    .value.fall { color: var(--artdeco-down); }
}
.sector-flows {
    display: flex;
    flex-wrap: wrap;
    gap: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}
.sector-tag {
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
    font-size: var(--artdeco-text-xs);
    border-radius: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
    &.in {
      background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
      color: var(--artdeco-down);
    }
    &.out {
      background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
      color: var(--artdeco-down);
    }
}

@media (width <= 48rem) {
    .main-flows {
      grid-template-columns: 1fr;
    }
}
</style>
