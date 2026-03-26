<template>
    <div class="artdeco-market-panorama">
        <!-- Overview Stats -->
        <div class="panorama-overview">
            <ArtDecoStatCard label="总市值" :value="getTotalMarketCap()" variant="gold" />
            <ArtDecoStatCard label="成交额" :value="getTotalTurnover()" variant="gold" />
            <ArtDecoStatCard label="上涨" :value="getUpCount()" variant="rise" />
            <ArtDecoStatCard label="下跌" :value="getDownCount()" variant="fall" />
            <ArtDecoStatCard label="涨停" :value="getLimitUpCount()" variant="rise" />
            <ArtDecoStatCard label="跌停" :value="getLimitDownCount()" variant="fall" />
        </div>

        <div class="panorama-grid">
            <!-- Indices -->
            <PanoramaIndices :indices="marketIndices" />

            <!-- Capital Flow -->
            <PanoramaCapitalFlow 
                :north="northboundFlow" 
                :south="southboundFlow" 
                :mainForce="mainForceFlow" 
                :sectors="sectorFlows" 
            />

            <!-- Activity -->
            <ArtDecoCard title="交易活跃度分析">
                <div class="activity-summary">
                    <p>全市场活跃度：处于历史高位 (85%)</p>
                    <div class="activity-bar">
                        <div class="fill" style="width: 85%"></div>
                    </div>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'
import { useMarketPanorama } from '@/composables/advanced/useMarketPanorama'

// Components
import PanoramaIndices from '@/views/artdeco-pages/components/PanoramaIndices.vue'
import PanoramaCapitalFlow from '@/views/artdeco-pages/components/PanoramaCapitalFlow.vue'

const {
    marketIndices, northboundFlow, southboundFlow, mainForceFlow, sectorFlows,
    getTotalMarketCap, getTotalTurnover, getUpCount, getDownCount, getLimitUpCount, getLimitDownCount
} = useMarketPanorama()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.artdeco-market-panorama {
    padding: var(--artdeco-spacing-5);
}

.panorama-overview {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: var(--artdeco-spacing-5);
    margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.panorama-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.activity-summary {
    padding: var(--artdeco-spacing-5);
    .activity-bar {
        height: calc(var(--artdeco-spacing-sm) - var(--artdeco-radius-md));
        background: var(--artdeco-gold-opacity-10);
        margin-top: calc(var(--artdeco-spacing-sm) + var(--artdeco-spacing-xs) + var(--artdeco-radius-md) + var(--artdeco-radius-sm));
        .fill {
          height: 100%;
          background: var(--artdeco-gold-primary);
        }
    }
}
</style>
