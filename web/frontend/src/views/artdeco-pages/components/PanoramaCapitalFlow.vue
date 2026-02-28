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
@import '@/styles/artdeco-tokens';
.main-flows {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 25px;
}
.flow-item {
    text-align: center;
    .label {
      font-size: 12px;
      color: var(--artdeco-fg-muted);
      margin-bottom: 5px;
    }
    .value {
      font-size: 18px;
      font-weight: bold;
    }
    .value.rise { color: var(--artdeco-rise); }
    .value.fall { color: var(--artdeco-down); }
}
.sector-flows {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.sector-tag {
    padding: 4px 12px;
    font-size: 12px;
    border-radius: 4px;
    &.in {
      background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
      color: var(--artdeco-down);
    }
    &.out {
      background: color-mix(in srgb, var(--artdeco-up) 10%, transparent);
      color: var(--artdeco-down);
    }
}
</style>
