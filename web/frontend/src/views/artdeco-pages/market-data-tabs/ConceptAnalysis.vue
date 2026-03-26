<template>
  <div class="concept-analysis">
    <div class="module-shell">
      <div class="module-header">
        <div class="module-copy">
          <span class="module-eyebrow">concept heat lens</span>
          <h3 class="module-title">概念热度与详情面板</h3>
          <p class="module-subtitle">同步观察概念热度、平均涨跌幅和龙头样本，作为板块情绪扩散的内部分析模块。</p>
        </div>
        <div class="module-meta">
          <span>CONCEPTS: {{ conceptRanking.length }}</span>
          <span>RISING: {{ risingConceptCount }}</span>
          <span>FOCUS: {{ selectedConceptName }}</span>
        </div>
      </div>

      <div class="module-stats">
        <ArtDecoStatCard label="概念总数" :value="conceptRanking.length" variant="gold" />
        <ArtDecoStatCard label="上涨概念" :value="risingConceptCount" variant="rise" />
        <ArtDecoStatCard label="最高热度" :value="topHeatLabel" variant="gold" />
        <ArtDecoStatCard label="当前焦点" :value="selectedConceptName" variant="gold" />
      </div>

      <div class="concept-grid">
        <ArtDecoCard title="概念板块热度排行" hoverable class="concepts-card">
          <div class="concepts-heat-map">
            <div 
              v-for="(concept, _idx) in conceptRanking" 
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoCard, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'

interface TopStock {
  code: string
  name: string
  change: number
}

interface ConceptItem {
  name: string
  stockCount: number
  change: number
  heat: number
}

interface SelectedConceptDetail {
  name: string
  stockCount: number
  avgChange: number
  topStocks: TopStock[]
}

interface Props {
  conceptRanking: ConceptItem[]
  selectedConcept: SelectedConceptDetail | null
}

const props = defineProps<Props>()
const emit = defineEmits(['select-concept'])

const risingConceptCount = computed(() => props.conceptRanking.filter((concept) => concept.change >= 0).length)
const topHeat = computed(() => props.conceptRanking.length ? Math.max(...props.conceptRanking.map((concept) => concept.heat)) : 0)
const topHeatLabel = computed(() => `${topHeat.value}°`)
const selectedConceptName = computed(() => props.selectedConcept?.name || '未选择')
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.concept-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

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

.module-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.concept-grid {
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
  border: 1px solid var(--artdeco-gold-opacity-10);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);
  cursor: pointer;

  &:hover, &.active {
    border-color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-05);
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
      min-width: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
      text-align: right;
      &.rise { color: var(--artdeco-up); }
      &.fall { color: var(--artdeco-down); }
    }

    .concept-heat {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);

      .heat-bar {
        width: var(--artdeco-spacing-20);
        height: calc(var(--artdeco-spacing-sm) - var(--artdeco-radius-md));
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
        min-width: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1) + var(--artdeco-spacing-px));
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

@media (width <= 75rem) {
  .module-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .concept-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
  .module-stats {
    grid-template-columns: 1fr;
  }

  .module-meta {
    width: 100%;
  }
}
</style>
