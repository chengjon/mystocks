<script setup lang="ts">
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import {
  formatRiskCurrencyNumber,
  type RiskMetrics
} from './riskManagementHelpers'

defineProps<{
  riskData: RiskMetrics
}>()

function hasMetricValue(value: number | null): value is number {
  return typeof value === 'number'
}
</script>

<template>
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">总资产</div>
      <div class="stat-value gold">¥{{ formatRiskCurrencyNumber(riskData.totalAssets) }}</div>
      <template v-if="hasMetricValue(riskData.totalAssetsChange)">
        <div class="stat-change" :class="riskData.totalAssetsChange >= 0 ? 'positive' : 'negative'">
          <ArtDecoIcon :name="riskData.totalAssetsChange >= 0 ? 'trending-up' : 'trending-down'" size="xs" />
          {{ riskData.totalAssetsChange >= 0 ? '+' : '' }}{{ riskData.totalAssetsChange }}%
        </div>
      </template>
      <template v-else>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">今日收益</div>
      <div class="stat-value" :class="riskData.todayProfit >= 0 ? 'success' : 'danger'">
        {{ riskData.todayProfit >= 0 ? '+' : '' }}¥{{ formatRiskCurrencyNumber(riskData.todayProfit) }}
      </div>
      <template v-if="hasMetricValue(riskData.todayProfitChange)">
        <div class="stat-change" :class="riskData.todayProfitChange >= 0 ? 'positive' : 'negative'">
          {{ riskData.todayProfitChange >= 0 ? '+' : '' }}{{ riskData.todayProfitChange }}%
        </div>
      </template>
      <template v-else>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card warning">
      <div class="stat-label">最大回撤</div>
      <template v-if="hasMetricValue(riskData.maxDrawdown)">
        <div class="stat-value danger">-{{ riskData.maxDrawdown }}%</div>
        <div class="stat-change negative">当前周期</div>
      </template>
      <template v-else>
        <div class="stat-value pending">未校验</div>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">夏普比率</div>
      <template v-if="hasMetricValue(riskData.sharpeRatio)">
        <div class="stat-value">{{ riskData.sharpeRatio }}</div>
        <div class="stat-change positive">超额收益</div>
      </template>
      <template v-else>
        <div class="stat-value pending">未校验</div>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">年化波动率</div>
      <template v-if="hasMetricValue(riskData.volatility)">
        <div class="stat-value">{{ riskData.volatility }}%</div>
      </template>
      <template v-else>
        <div class="stat-value pending">未校验</div>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">贝塔值</div>
      <template v-if="hasMetricValue(riskData.beta)">
        <div class="stat-value">{{ riskData.beta }}</div>
        <div class="stat-change negative">vs 沪深300</div>
      </template>
      <template v-else>
        <div class="stat-value pending">未校验</div>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">索提诺比率</div>
      <template v-if="hasMetricValue(riskData.sortinoRatio)">
        <div class="stat-value">{{ riskData.sortinoRatio }}</div>
      </template>
      <template v-else>
        <div class="stat-value pending">未校验</div>
        <div class="stat-change pending">待接入</div>
      </template>
    </div>
    <div class="stat-card">
      <div class="stat-label">持仓市值</div>
      <div class="stat-value">¥{{ formatRiskCurrencyNumber(riskData.positionValue) }}</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);

  @media (width <= 75rem) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (width <= 48rem) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-opacity-10);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  padding: var(--artdeco-spacing-5);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: calc(var(--artdeco-spacing-px) * 3);
    background: linear-gradient(90deg, var(--artdeco-gold-primary), transparent);
  }

  &.warning::before {
    background: linear-gradient(90deg, var(--artdeco-warning), transparent);
  }

  &:hover {
    border-color: var(--artdeco-gold-opacity-20);
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
  }
}

.stat-label {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-spacing-px);
  margin-bottom: var(--artdeco-spacing-2);
}

.stat-value {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-fg-primary);
  margin-bottom: var(--artdeco-spacing-1);

  &.gold {
    color: var(--artdeco-gold-primary);
  }

  &.danger {
    color: var(--artdeco-down);
  }

  &.success {
    color: var(--artdeco-rise);
  }

  &.pending {
    color: var(--artdeco-warning);
  }
}

.stat-change {
  font-size: var(--artdeco-text-sm);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);

  &.positive {
    color: var(--artdeco-rise);
  }

  &.negative {
    color: var(--artdeco-down);
  }

  &.pending {
    color: var(--artdeco-fg-muted);
  }
}
</style>
