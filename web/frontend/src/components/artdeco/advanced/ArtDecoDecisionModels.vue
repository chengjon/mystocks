<template>
    <div class="artdeco-decision-models">
        <!-- Overview Stats -->
        <div class="models-overview">
            <ArtDecoStatCard label="最佳决策模型" :value="getBestModel()" variant="gold" />
            <ArtDecoStatCard label="决策置信度" :value="getDecisionConfidence()" variant="gold" />
            <ArtDecoStatCard label="预期收益" :value="getExpectedReturn()" variant="rise" />
            <ArtDecoStatCard label="风险评估" :value="getRiskAssessment()" variant="gold" />
        </div>

        <!-- Comparison -->
        <ArtDecoCard title="模型对比分析" class="comparison-section">
            <ArtDecoTable :columns="columns" :data="decisionModels" />
        </ArtDecoCard>

        <!-- Domain Models -->
        <div class="models-grid">
            <BuffettModel :criteria="buffettCriteria" :overallScore="buffettOverallScore" />
            <OneilModel :factors="canslimFactors" :strength="oneilSignalStrength" />
            <LynchModel :peg="pegRatio" :pe="peRatio" :growth="growthRate" />
            
            <ArtDecoCard title="数据挖掘模型">
                <div class="mining-metrics">
                    <div class="metric">
                        <span class="label">模型准确率</span>
                        <span class="value">{{ miningAccuracy }}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">上涨概率</span>
                        <span class="value">{{ predictionProbability }}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">关键特征</span>
                        <span class="value">{{ topFeature }}</span>
                    </div>
                </div>
            </ArtDecoCard>
        </div>
    </div>
</template>

<script setup>
import { ArtDecoStatCard, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'
import { useDecisionModels } from '@/composables/advanced/useDecisionModels'

// Sub-components
import BuffettModel from './components/BuffettModel.vue'
import OneilModel from './components/OneilModel.vue'
import LynchModel from './components/LynchModel.vue'

const {
    decisionModels, buffettCriteria, canslimFactors,
    pegRatio, peRatio, growthRate,
    miningAccuracy, predictionProbability, topFeature,
    buffettOverallScore, oneilSignalStrength,
    getBestModel, getDecisionConfidence, getExpectedReturn, getRiskAssessment
} = useDecisionModels()

const columns = [
    { key: 'name', label: '模型名称' },
    { key: 'signal', label: '当前信号' },
    { key: 'confidence', label: '置信度', format: v => v + '%' },
    { key: 'expectedReturn', label: '预期收益', format: v => v + '%' },
    { key: 'riskLevel', label: '风险等级' }
]
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.artdeco-decision-models {
    padding: 20px;
}

.models-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.comparison-section {
    margin-bottom: 30px;
}

.models-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
}

.mining-metrics {
    display: flex;
    justify-content: space-around;
    padding: 20px;
    .metric {
        display: flex;
        flex-direction: column;
        align-items: center;
        .label { font-size: 12px; color: var(--artdeco-fg-muted); margin-bottom: 10px; }
        .value { font-size: 20px; font-weight: bold; color: var(--artdeco-gold-primary); }
    }
}
</style>