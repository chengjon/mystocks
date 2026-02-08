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
    gap: 20px;
    padding: 20px;
}
.children {
    display: flex;
    align-items: center;
    gap: 15px;
}
.node {
    background: rgba(212, 175, 55, 0.1);
    border: 1px solid var(--artdeco-gold-primary);
    padding: 15px;
    text-align: center;
    min-width: 120px;
    .label { font-size: 12px; margin-bottom: 5px; }
    .value { font-size: 18px; font-weight: bold; color: var(--artdeco-gold-primary); }
}
.roe {
    background: var(--artdeco-gold-primary);
    color: white;
    .value { color: white; }
}
</style>
