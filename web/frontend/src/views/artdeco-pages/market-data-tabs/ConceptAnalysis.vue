<template>
  <div class="concept-analysis">
    <ArtDecoCard title="概念板块热度排行" hoverable class="concepts-card">
      <div class="concepts-heat-map">
        <div 
          v-for="concept in conceptRanking" 
          :key="concept.name"
          class="concept-item" 
          :class="{ active: selectedConcept?.name === concept.name }"
          @click="emit('select-concept', concept)"
        >
          <div class="concept-info">
            <div class="concept-name">{{ concept.name }}</div>
            <div class="concept-stocks">{{ concept.stockCount }}只成分股</div>
          </div>
          <div class="concept-performance">
            <div class="concept-change" :class="concept.change >= 0 ? 'rise' : 'fall'">
              {{ concept.change >= 0 ? '+' : '' }}{{ concept.change }}%
            </div>
            <div class="concept-heat">
              <div class="heat-bar">
                <div class="heat-fill" :style="{ width: concept.heat + '%' }"></div>
              </div>
              <div class="heat-value">{{ concept.heat }}°</div>
            </div>
          </div>
        </div>
      </div>
    </ArtDecoCard>

    <ArtDecoCard title="热门概念详情" hoverable class="concept-detail-card">
      <div class="concept-detail" v-if="selectedConcept">
        <div class="detail-header">
          <h3>{{ selectedConcept.name }}</h3>
          <div class="detail-stats">
            <span>成分股: {{ selectedConcept.stockCount }}只</span>
            <span>
              平均涨跌幅:
              <span :class="selectedConcept.avgChange >= 0 ? 'rise' : 'fall'">
                {{ selectedConcept.avgChange >= 0 ? '+' : '' }}{{ selectedConcept.avgChange }}%
              </span>
            </span>
          </div>
        </div>
        <div class="top-stocks">
          <h4>涨幅前五</h4>
          <div class="stock-list">
            <div class="stock-item" v-for="stock in selectedConcept.topStocks" :key="stock.code">
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-code">{{ stock.code }}</div>
              <div class="stock-change rise">+{{ stock.change }}%</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-selection">
        <ArtDecoIcon name="info" size="xl" />
        <p>选择左侧概念板块查看详情</p>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ArtDecoCard, ArtDecoIcon } from '@/components/artdeco'

interface Props {
  conceptRanking: any[]
  selectedConcept: any | null
}

defineProps<Props>()
const emit = defineEmits(['select-concept'])
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.concept-analysis {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--artdeco-spacing-6);
}

.concepts-heat-map {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.concept-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);
  cursor: pointer;

  &:hover, &.active {
    border-color: var(--artdeco-gold-primary);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    box-shadow: var(--artdeco-glow-subtle);
  }

  .concept-info {
    .concept-name {
      font-family: var(--artdeco-font-body);
      font-weight: 600;
      color: var(--artdeco-fg-primary);
    }
    .concept-stocks {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }
  }

  .concept-performance {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-4);

    .concept-change {
      font-family: var(--artdeco-font-mono);
      font-weight: 700;
      min-width: 60px;
      text-align: right;
      &.rise { color: var(--artdeco-up); }
      &.fall { color: var(--artdeco-down); }
    }

    .concept-heat {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);

      .heat-bar {
        width: 80px;
        height: 6px;
        background: var(--artdeco-bg-base);
        border-radius: var(--artdeco-radius-sm);
        overflow: hidden;

        .heat-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-up));
        }
      }

      .heat-value {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-gold-primary);
        min-width: 35px;
      }
    }
  }
}

.concept-detail {
  .detail-header {
    margin-bottom: var(--artdeco-spacing-6);
    h3 {
      font-family: var(--artdeco-font-display);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }
    .detail-stats {
      display: flex;
      gap: var(--artdeco-spacing-4);
      color: var(--artdeco-fg-muted);
    }
  }
}

.no-selection {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--artdeco-fg-muted);
  gap: var(--artdeco-spacing-4);
}
</style>
