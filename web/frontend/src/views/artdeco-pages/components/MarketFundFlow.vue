<template>
    <div class="fund-flow-container">
        <div class="fund-overview">
            <ArtDecoStatCard
                label="沪股通净流入"
                :value="data.shanghai.amount"
                :change="data.shanghai.change"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="深股通净流入"
                :value="data.shenzhen.amount"
                :change="data.shenzhen.change"
                change-percent
                variant="gold"
            />
            <ArtDecoStatCard
                label="北向资金总额"
                :value="data.north.amount"
                :change="data.north.change"
                change-percent
                :variant="data.north.change > 0 ? 'rise' : 'fall'"
            />
            <ArtDecoStatCard
                label="主力净流入"
                :value="data.main.amount"
                :change="data.main.change"
                change-percent
                variant="gold"
            />
        </div>

        <ArtDecoCard title="近30日资金流向趋势" hoverable class="fund-chart-card">
            <div class="chart-placeholder">
                <div class="chart-title">资金流向趋势图</div>
                <div class="chart-area">
                    <!-- SVG Chart Logic extracted or kept simple -->
                    <svg width="100%" height="200" viewBox="0 0 800 200" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="fundPositive" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color: #e74c3c; stop-opacity: 0.6" />
                                <stop offset="100%" style="stop-color: #e74c3c; stop-opacity: 0.1" />
                            </linearGradient>
                            <linearGradient id="fundNegative" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color: #27ae60; stop-opacity: 0.6" />
                                <stop offset="100%" style="stop-color: #27ae60; stop-opacity: 0.1" />
                            </linearGradient>
                        </defs>
                        <!-- 模拟资金流向柱状图 (Simplified) -->
                        <rect x="20" y="60" width="25" height="80" fill="url(#fundPositive)" />
                        <rect x="55" y="40" width="25" height="100" fill="url(#fundPositive)" />
                        <rect x="90" y="100" width="25" height="40" fill="url(#fundNegative)" />
                        <!-- More bars would go here -->
                    </svg>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup>
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'

defineProps({
    data: {
        type: Object,
        required: true
    }
})
</script>

<style scoped>
.fund-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 24px;
}

.fund-chart-card {
    margin-bottom: 24px;
}

.chart-placeholder {
    height: 200px;
    display: flex;
    flex-direction: column;
}

.chart-title {
    font-size: 14px;
    color: var(--artdeco-text-secondary);
    margin-bottom: 10px;
}

.chart-area {
    flex: 1;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    overflow: hidden;
}
</style>
