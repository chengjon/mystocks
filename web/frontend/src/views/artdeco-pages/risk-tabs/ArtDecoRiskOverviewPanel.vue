<script setup lang="ts">
import { computed } from 'vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'
import {
  getRiskLevelLabel,
  getStopStatusLabel,
  sectorColors,
  type ConcentrationMetric,
  type RiskAlertItem,
  type SectorDistributionItem,
} from './riskManagementHelpers'

const props = withDefaults(defineProps<{
  riskAlerts: RiskAlertItem[]
  sectorDistribution?: SectorDistributionItem[]
  concentrationMetrics?: ConcentrationMetric[]
}>(), {
  sectorDistribution: () => [],
  concentrationMetrics: () => [],
})

const emit = defineEmits<{
  action: [stock: RiskAlertItem]
}>()

const observationMode = computed(() =>
  props.riskAlerts.length > 0 && props.riskAlerts.some((stock) => !stock.policyReady),
)

const alertTableTitle = computed(() => (observationMode.value ? '风险观察列表' : '风险预警列表'))
const alertCountLabel = computed(() => (observationMode.value ? '条观察项' : '条预警'))
const stopStatusColumnLabel = computed(() => (observationMode.value ? '策略状态' : '止损状态'))
const actionColumnLabel = computed(() => (observationMode.value ? '复核状态' : '操作建议'))
</script>

<template>
  <div
    id="risk-panel-overview"
    class="tab-panel"
    role="tabpanel"
    aria-labelledby="risk-tab-overview"
  >
    <div class="position-grid">
      <ArtDecoCard class="distribution-card">
        <template #header>
          <div class="card-header-custom">
            <div class="card-title-custom">
              <span class="title-bar"></span>
              行业持仓分布
            </div>
          </div>
        </template>
        <div v-if="props.sectorDistribution.length > 0" class="sector-list">
          <div
            v-for="(sector, index) in props.sectorDistribution"
            :key="sector.name"
            class="sector-item"
          >
            <span class="sector-name">{{ sector.name }}</span>
            <div class="sector-bar">
              <div
                class="sector-fill"
                :style="{ width: sector.percent + '%', background: sectorColors[index] }"
              ></div>
            </div>
            <span class="sector-percent">{{ sector.percent }}%</span>
          </div>
        </div>
        <p v-else class="empty-copy">行业分布待接入，当前持仓数据未提供可验证的行业字段。</p>
      </ArtDecoCard>

      <ArtDecoCard class="concentration-card">
        <template #header>
          <div class="card-header-custom">
            <div class="card-title-custom">
              <span class="title-bar"></span>
              仓位集中度分析
            </div>
          </div>
        </template>
        <div v-if="props.concentrationMetrics.length > 0" class="progress-list">
          <div
            v-for="item in props.concentrationMetrics"
            :key="item.label"
            class="progress-container"
          >
            <div class="progress-header">
              <span class="progress-label">{{ item.label }}</span>
              <span class="progress-value">
                <template v-if="item.limit !== null">{{ item.current }} / {{ item.limit }}</template>
                <template v-else>{{ item.current }}%</template>
              </span>
            </div>
            <div class="progress-bar-bg">
              <div
                class="progress-fill"
                :class="item.variant"
                :style="{ width: (item.limit !== null ? item.current / item.limit * 100 : item.current) + '%' }"
              ></div>
            </div>
          </div>
        </div>
        <p v-else class="empty-copy">集中度指标待接入，当前仅保留真实持仓告警与总览统计。</p>
      </ArtDecoCard>
    </div>

    <ArtDecoCard class="risk-table-card">
      <template #header>
        <div class="card-header-custom">
          <div class="card-title-custom">
            <span class="title-bar"></span>
            {{ alertTableTitle }}
          </div>
          <ArtDecoBadge v-if="riskAlerts.length > 0" variant="danger">
            {{ riskAlerts.length }} {{ alertCountLabel }}
          </ArtDecoBadge>
        </div>
      </template>
      <p v-if="observationMode" class="observation-note">
        当前仅基于真实持仓暴露生成风险观察项，未接入止损/减仓策略参数。
      </p>
      <div class="table-container">
        <table class="risk-table">
          <thead>
            <tr>
              <th>股票名称</th>
              <th>风险等级</th>
              <th>仓位占比</th>
              <th>{{ stopStatusColumnLabel }}</th>
              <th>{{ actionColumnLabel }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in riskAlerts" :key="stock.code">
              <td>
                <div class="stock-info">
                  <span class="stock-name">{{ stock.name }}</span>
                  <span class="stock-code">{{ stock.code }}</span>
                </div>
              </td>
              <td>
                <span class="risk-badge" :class="stock.riskLevel">
                  {{ getRiskLevelLabel(stock.riskLevel) }}
                </span>
              </td>
              <td>{{ stock.position }}%</td>
              <td>
                <span class="stop-status" :class="stock.stopStatus">
                  {{ getStopStatusLabel(stock.stopStatus) }}
                </span>
              </td>
              <td>
                <ArtDecoButton
                  variant="outline"
                  size="sm"
                  @click="emit('action', stock)"
                >
                  {{ stock.action }}
                </ArtDecoButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </ArtDecoCard>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.tab-panel {
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from {
    opacity: 0%;
    transform: translateY(calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)));
  }

  to {
    opacity: 100%;
    transform: translateY(0);
  }
}

.position-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-5);

  @media (width <= 62rem) {
    grid-template-columns: 1fr;
  }
}

.card-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
  padding-bottom: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.card-title-custom {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-gold-light);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  .title-bar {
    width: calc(var(--artdeco-spacing-px) * 4);
    height: calc(var(--artdeco-spacing-4) + (var(--artdeco-spacing-px) * 2));
    background: var(--artdeco-gold-primary);
    border-radius: var(--artdeco-radius-sm);
  }
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.sector-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
}

.sector-name {
  width: var(--artdeco-spacing-20);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.sector-bar {
  flex: 1;
  height: var(--artdeco-spacing-2);
  background: var(--artdeco-bg-base);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  overflow: hidden;
}

.sector-fill {
  height: 100%;
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  transition: width 0.5s ease;
}

.sector-percent {
  width: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
  text-align: right;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
}

.empty-copy {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: 1.6;
}

.observation-note {
  margin: 0 0 var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: 1.6;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.progress-value {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
}

.progress-bar-bg {
  height: var(--artdeco-spacing-2);
  background: var(--artdeco-bg-base);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  transition: width 0.5s ease;

  &.gold {
    background: linear-gradient(90deg, var(--artdeco-bronze), var(--artdeco-gold-primary));
  }

  &.success {
    background: linear-gradient(90deg, var(--artdeco-down), var(--artdeco-info));
  }

  &.warning {
    background: linear-gradient(90deg, var(--artdeco-warning), var(--artdeco-gold-light));
  }
}

.risk-table-card {
  margin-top: var(--artdeco-spacing-5);
}

.table-container {
  overflow-x: auto;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: var(--artdeco-spacing-4);
    text-align: left;
    border-bottom: 1px solid var(--artdeco-gold-opacity-10);
  }

  th {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-gold-dim);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-spacing-px);
    font-weight: 600;
    background: var(--artdeco-gold-opacity-05);
  }

  tr:hover td {
    background: var(--artdeco-gold-opacity-08);
  }
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.stock-name {
  font-weight: 500;
  color: var(--artdeco-fg-primary);
}

.stock-code {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  border-radius: calc(var(--artdeco-spacing-px) * 3);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;

  &.high {
    background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
    color: var(--artdeco-rise);
    border: 1px solid color-mix(in srgb, var(--artdeco-rise) 30%, transparent);
  }

  &.medium {
    background: color-mix(in srgb, var(--artdeco-warning) 20%, transparent);
    color: var(--artdeco-warning);
    border: 1px solid color-mix(in srgb, var(--artdeco-warning) 30%, transparent);
  }

  &.low {
    background: color-mix(in srgb, var(--artdeco-down) 20%, transparent);
    color: var(--artdeco-down);
    border: 1px solid color-mix(in srgb, var(--artdeco-down) 30%, transparent);
  }
}

.stop-status {
  font-size: var(--artdeco-text-sm);

  &.triggered {
    color: var(--artdeco-rise);
  }

  &.approaching {
    color: var(--artdeco-warning);
  }

  &.normal {
    color: var(--artdeco-down);
  }
}
</style>
