<template>
    <ArtDecoCard class="dupont-analysis" title="杜邦分析">
        <div class="dupont-tree">
            <div class="node roe">
                <div class="label">ROE</div>
                <div class="value">{{ data.roe }}%</div>
            </div>
            <div class="connector">=</div>
            <div class="children">
                <div class="node">
                    <div class="label">销售净利率</div>
                    <div class="value">{{ data.netProfitMargin }}%</div>
                </div>
                <div class="operator">×</div>
                <div class="node">
                    <div class="label">资产周转率</div>
                    <div class="value">{{ data.assetTurnover }}</div>
                </div>
                <div class="operator">×</div>
                <div class="node">
                    <div class="label">权益乘数</div>
                    <div class="value">{{ data.equityMultiplier }}</div>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup>
import { ArtDecoCard } from '@/components/artdeco'

defineProps({
    data: Object
})
</script>

<style scoped lang="scss">
.dupont-tree {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--artdeco-spacing-5);
    padding: var(--artdeco-spacing-5);
}
.children {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm));
}
.node {
    background: var(--artdeco-gold-opacity-10);
    border: 1px solid var(--artdeco-gold-primary);
    padding: calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm));
    text-align: center;
    min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10));
    .label {
      font-size: var(--artdeco-text-xs);
      margin-bottom: calc(var(--artdeco-spacing-xs) + var(--artdeco-spacing-px));
    }
    .value {
      font-size: calc(var(--artdeco-text-base) + var(--artdeco-radius-md));
      font-weight: bold;
      color: var(--artdeco-gold-primary);
    }
}
.roe {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    .value { color: var(--artdeco-bg-global); }
}

@media (width <= 75rem) {
    .children {
        flex-direction: column;
        width: 100%;
    }

    .node {
        width: 100%;
    }
}
</style>
