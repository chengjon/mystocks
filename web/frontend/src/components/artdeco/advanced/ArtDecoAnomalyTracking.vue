<template>
    <div class="artdeco-anomaly-tracking">
        <!-- Overview Stats -->
        <div class="anomaly-overview">
            <ArtDecoStatCard label="检测异动数" :value="getAnomalyCount()" variant="gold" />
            <ArtDecoStatCard label="高风险异动" :value="getHighRiskCount()" variant="fall" />
            <ArtDecoStatCard label="异动成功率" :value="getDetectionAccuracy()" variant="gold" />
            <ArtDecoStatCard label="平均响应时间" :value="getAvgResponseTime()" variant="gold" />
        </div>

        <div class="anomaly-grid">
            <!-- Real-time Alerts -->
            <AnomalyAlerts :alerts="activeAlerts" />

            <!-- Pattern Recognition -->
            <AnomalyPatterns :patterns="patterns" />
        </div>
    </div>
</template>

<script setup>
import { ArtDecoStatCard } from '@/components/artdeco'
import { useAnomalyTracking } from '@/composables/advanced/useAnomalyTracking'

// Sub-components
import AnomalyAlerts from './components/AnomalyAlerts.vue'
import AnomalyPatterns from './components/AnomalyPatterns.vue'

const {
    activeAlerts, patterns,
    getAnomalyCount, getHighRiskCount, getDetectionAccuracy, getAvgResponseTime
} = useAnomalyTracking()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-anomaly-tracking {
    padding: 20px;
}

.anomaly-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.anomaly-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}
</style>