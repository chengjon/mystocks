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
import PanoramaIndices from './components/PanoramaIndices.vue'
import PanoramaCapitalFlow from './components/PanoramaCapitalFlow.vue'

const {
    marketIndices, northboundFlow, southboundFlow, mainForceFlow, sectorFlows,
    getTotalMarketCap, getTotalTurnover, getUpCount, getDownCount, getLimitUpCount, getLimitDownCount
} = useMarketPanorama()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-market-panorama {
    padding: 20px;
}

.panorama-overview {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.panorama-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}

.activity-summary {
    padding: 20px;
    .activity-bar {
        height: 6px;
        background: rgba(212, 175, 55, 0.1);
        margin-top: 15px;
        .fill { height: 100%; background: var(--artdeco-gold-primary); }
    }
}
</style>