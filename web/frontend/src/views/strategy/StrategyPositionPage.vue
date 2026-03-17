<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { strategyPositionService, type StrategyPositionSnapshot } from '@/api/services/strategyPositionService'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import PortfolioMonitor from '@/views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue'

const { loading, error, lastProcessTime, lastRequestId, exec } = useArtDecoApi()

const snapshot = ref<StrategyPositionSnapshot>({
  summary: {
    totalMarketValue: 0,
    totalProfitLoss: 0,
    totalProfitLossPercent: 0,
    positionsCount: 0,
    maxPositionPercent: 0
  },
  positions: []
})

function displayProcessTime(): string {
  return lastProcessTime.value || 'N/A'
}

async function fetchPositions(): Promise<void> {
  const data = await exec(() => strategyPositionService.getPositionExposure(), {
    silent: true,
    errorMsg: '仓位数据加载失败'
  })

  snapshot.value = data ?? {
    summary: {
      totalMarketValue: 0,
      totalProfitLoss: 0,
      totalProfitLossPercent: 0,
      positionsCount: 0,
      maxPositionPercent: 0
    },
    positions: []
  }
}

onMounted(() => {
  void fetchPositions()
})
</script>

<template>
  <div class="strategy-position-page page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Strategy Position Board</h2>
      <div class="header-meta">
        <span>DATA: REAL</span>
        <span>REQ: {{ lastRequestId || 'N/A' }}</span>
        <span>TIME: {{ displayProcessTime() }}</span>
      </div>
    </div>

    <div v-if="snapshot.positions.length === 0" class="position-empty artdeco-card" v-loading="loading">
      <p v-if="error" class="empty-error">{{ error }}</p>
      <p class="empty-title">暂无仓位数据</p>
      <p class="empty-hint">当前页面只展示真实生产链路返回的数据，不再使用本地 mock / fallback 伪成功。</p>
    </div>

    <PortfolioMonitor
      v-else
      :summary="snapshot.summary"
      :positions="snapshot.positions"
    />
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.strategy-position-page {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
}

.header-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.position-empty {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
}

.empty-error {
  margin: 0;
  color: var(--artdeco-down);
  font-family: var(--artdeco-font-mono);
}

.empty-title {
  margin: 0;
  color: var(--artdeco-gold-light);
  font-size: var(--artdeco-text-lg);
}

.empty-hint {
  margin: 0;
  color: var(--artdeco-fg-muted);
}
</style>
