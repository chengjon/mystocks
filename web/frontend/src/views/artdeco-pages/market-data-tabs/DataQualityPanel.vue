<template>
  <div class="data-quality-panel">
    <div class="module-shell">
      <div class="module-header">
        <div class="module-copy">
          <span class="module-eyebrow">quality governance lens</span>
          <h3 class="module-title">数据质量与源健康面板</h3>
          <p class="module-subtitle">统一观察完整性、准确性、时效性和各数据源健康度，作为市场数据工作台里的治理模块。</p>
        </div>
        <div class="module-meta">
          <span>SOURCES: {{ dataSources.length }}</span>
          <span>HEALTHY: {{ healthySourceCount }}</span>
          <span>AVG: {{ averageQualityLabel }}</span>
        </div>
      </div>

      <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
        <div class="quality-overview">
          <ArtDecoStatCard
            label="数据完整性"
            :value="qualityData.integrity + '%'"
            :change="0.2"
            change-percent
            variant="gold"
          />
          <ArtDecoStatCard
            label="数据准确性"
            :value="qualityData.accuracy + '%'"
            :change="-0.1"
            change-percent
            variant="gold"
          />
          <ArtDecoStatCard
            label="更新及时性"
            :value="qualityData.timeliness + '%'"
            :change="1.5"
            change-percent
            variant="rise"
          />
          <ArtDecoStatCard
            label="数据一致性"
            :value="qualityData.consistency + '%'"
            :change="0.8"
            change-percent
            variant="gold"
          />
        </div>

        <div class="quality-details">
          <div class="quality-section">
            <h4>数据源健康状态</h4>
            <div class="data-sources">
              <div class="source-item" v-for="source in dataSources" :key="source.name">
                <div class="source-info">
                  <div class="source-name">{{ source.name }}</div>
                  <div class="source-type">{{ source.type }}</div>
                </div>
                <div class="source-status" :class="source.status">
                  {{ source.statusText }}
                </div>
                <div class="source-quality">{{ source.quality }}%</div>
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'

interface QualityData {
  integrity: number
  accuracy: number
  timeliness: number
  consistency: number
}

interface DataSourceItem {
  name: string
  type: string
  status: 'healthy' | 'warning' | 'error'
  statusText: string
  quality: number
}

interface Props {
  qualityData: QualityData
  dataSources: DataSourceItem[]
}

const props = defineProps<Props>()

const healthySourceCount = computed(() => props.dataSources.filter((source) => source.status === 'healthy').length)
const averageQualityLabel = computed(() => {
  if (props.dataSources.length === 0) return '--'
  const total = props.dataSources.reduce((sum, source) => sum + source.quality, 0)
  return `${(total / props.dataSources.length).toFixed(1)}%`
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.module-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.module-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.module-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.module-eyebrow {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.module-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.module-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.module-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.quality-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);
}

.quality-section h4 {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-accent-gold);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  margin-bottom: var(--artdeco-spacing-4);
}

.data-sources {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-opacity-10);
  border-radius: var(--artdeco-radius-none);
  
  .source-info {
    flex: 1;
    .source-name {
      font-weight: 600;
      color: var(--artdeco-fg-primary);
    }
    .source-type {
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-fg-muted);
    }
  }

  .source-status {
    padding: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px)) var(--artdeco-spacing-2);
    font-size: var(--artdeco-text-xs);
    text-transform: uppercase;
    &.healthy {
      color: var(--artdeco-up);
      background: color-mix(in srgb, var(--artdeco-rise) 10%, transparent);
    }
    &.warning {
      color: var(--artdeco-gold-primary);
      background: var(--artdeco-gold-opacity-10);
    }
  }
}

@media (width <= 48rem) {
  .module-meta {
    width: 100%;
  }

  .source-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-2);
  }
}
</style>
