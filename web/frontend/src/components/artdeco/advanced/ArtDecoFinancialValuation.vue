<template>
    <div class="artdeco-financial-valuation">
        <!-- Overview -->
        <div class="valuation-overview">
            <ArtDecoStatCard label="当前估值" :value="getCurrentValuation()" variant="gold" />
            <ArtDecoStatCard label="市盈率" :value="getPERatio()" variant="gold" />
            <ArtDecoStatCard label="市净率" :value="getPBRatio()" variant="gold" />
            <ArtDecoStatCard label="股息率" :value="getDividendYield()" variant="rise" />
            <ArtDecoStatCard label="估值状态" :value="getValuationStatus()" variant="gold" />
        </div>

        <div class="analysis-grid">
            <!-- Metrics -->
            <FinancialMetrics :metrics="keyMetrics" />

            <!-- Dupont -->
            <DupontAnalysis :data="dupontData" />

            <!-- Health -->
            <ArtDecoCard title="财务健康度">
                <div class="health-summary">
                    <div class="score">{{ financialHealthScore }}</div>
                    <div class="factors">
                        <div class="factor">盈利能力: {{ profitabilityScore }}</div>
                        <div class="factor">偿债能力: {{ solvencyScore }}</div>
                        <div class="factor">运营效率: {{ efficiencyScore }}</div>
                    </div>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'
import { useFinancialValuation } from '@/composables/advanced/useFinancialValuation'

// Components
import FinancialMetrics from '@/views/artdeco-pages/components/FinancialMetrics.vue'
import DupontAnalysis from '@/views/artdeco-pages/components/DupontAnalysis.vue'

const {
    keyMetrics, financialHealthScore, profitabilityScore,
    solvencyScore, efficiencyScore, dupontData,
    getCurrentValuation, getPERatio, getPBRatio, getDividendYield, getValuationStatus
} = useFinancialValuation()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-financial-valuation {
    padding: var(--artdeco-spacing-5);
}

.valuation-overview {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: var(--artdeco-spacing-5);
    margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.analysis-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.health-summary {
    display: flex;
    align-items: center;
    gap: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10));
    padding: var(--artdeco-spacing-5);
    .score {
        font-size: var(--artdeco-spacing-16);
        font-weight: bold;
        color: var(--artdeco-gold-primary);
    }
    .factors {
        display: flex;
        flex-direction: column;
        gap: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
    }
}
</style>
