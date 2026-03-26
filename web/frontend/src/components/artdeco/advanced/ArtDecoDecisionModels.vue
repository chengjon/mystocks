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
import BuffettModel from '@/views/artdeco-pages/components/BuffettModel.vue'
import OneilModel from '@/views/artdeco-pages/components/OneilModel.vue'
import LynchModel from '@/views/artdeco-pages/components/LynchModel.vue'

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
@import '@/styles/artdeco-tokens';

.artdeco-decision-models {
    padding: var(--artdeco-spacing-5);
}

.models-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--artdeco-spacing-5);
    margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.comparison-section {
    margin-bottom: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.models-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
}

.mining-metrics {
    display: flex;
    justify-content: space-around;
    padding: var(--artdeco-spacing-5);
    .metric {
        display: flex;
        flex-direction: column;
        align-items: center;
        .label {
          font-size: var(--artdeco-text-xs);
          color: var(--artdeco-fg-muted);
          margin-bottom: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
        }
        .value {
          font-size: calc(var(--artdeco-spacing-md) + var(--artdeco-spacing-xs));
          font-weight: bold;
          color: var(--artdeco-gold-primary);
        }
    }
}
</style>
