<template>
  <div class="data-quality-panel">
    <ArtDecoCard title="数据质量指标" hoverable class="quality-card">
      <div class="quality-overview">
        <ArtDecoStatCard
          label="数据完整性"
          :value="qualityData.integrity + '%'"
          change="0.2"
          change-percent
          variant="gold"
        />
        <ArtDecoStatCard
          label="数据准确性"
          :value="qualityData.accuracy + '%'"
          change="-0.1"
          change-percent
          variant="gold"
        />
        <ArtDecoStatCard
          label="更新及时性"
          :value="qualityData.timeliness + '%'"
          change="1.5"
          change-percent
          variant="rise"
        />
        <ArtDecoStatCard
          label="数据一致性"
          :value="qualityData.consistency + '%'"
          change="0.8"
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
</template>

<script setup lang="ts">
import { ArtDecoStatCard, ArtDecoCard } from '@/components/artdeco'

interface Props {
  qualityData: any
  dataSources: any[]
}

defineProps<Props>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.quality-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--artdeco-radius-none);
  
  .source-info {
    flex: 1;
    .source-name { font-weight: 600; color: var(--artdeco-fg-primary); }
    .source-type { font-size: 12px; color: var(--artdeco-fg-muted); }
  }

  .source-status {
    padding: 2px 8px;
    font-size: 12px;
    text-transform: uppercase;
    &.healthy { color: var(--artdeco-up); background: rgba(255, 82, 82, 0.1); }
    &.warning { color: var(--artdeco-gold-primary); background: rgba(212, 175, 55, 0.1); }
  }
}
</style>
