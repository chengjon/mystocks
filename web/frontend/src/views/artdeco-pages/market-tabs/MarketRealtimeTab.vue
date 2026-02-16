<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { dataApi } from '@/api/index';
import type { MarketOverview } from '@/api/types/common';

// 使用 ArtDeco API 组合函数
const { loading, lastRequestId, exec } = useArtDecoApi();

// 市场概览数据
const overview = ref<MarketOverview | null>(null);

// 获取数据
const fetchOverview = async () => {
  const data = await exec(() => dataApi.getMarketOverview(), {
    silent: true // 初始加载保持静默，不弹出消息
  });
  if (data) {
    overview.value = data;
  }
};

onMounted(() => {
  fetchOverview();
});
</script>

<template>
  <div class="market-realtime-tab page-enter">
    <!-- 装饰性标题栏 -->
    <div class="artdeco-header-bar">
      <h2 class="section-title">Market Realtime Overview</h2>
      <div class="request-trace" v-if="lastRequestId">
        TRACE_ID: {{ lastRequestId }}
      </div>
    </div>

    <!-- 核心指标网格 -->
    <div class="stats-grid" v-loading="loading">
      <div v-for="index in overview?.indices" :key="index.symbol" class="artdeco-card stat-card">
        <div class="card-inner">
          <div class="index-name">{{ index.name }}</div>
          <div class="index-value">{{ index.current_price?.toFixed(2) }}</div>
          <div :class="['index-change', (index.change_percent ?? 0) >= 0 ? 'rise' : 'down']">
            {{ (index.change_percent ?? 0) >= 0 ? '+' : '' }}{{ index.change_percent?.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 涨跌分布 -->
    <div class="distribution-section artdeco-card">
      <h3 class="subsection-title">Market Distribution</h3>
      <div class="distribution-bar">
        <div class="bar-segment rise-segment" :style="{ width: `${(overview?.up_count || 0) / 50}%` }">
          涨: {{ overview?.up_count }}
        </div>
        <div class="bar-segment flat-segment" :style="{ width: `${(overview?.flat_count || 0) / 50}%` }">
          平: {{ overview?.flat_count }}
        </div>
        <div class="bar-segment down-segment" :style="{ width: `${(overview?.down_count || 0) / 50}%` }">
          跌: {{ overview?.down_count }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.market-realtime-tab {
  padding: var(--artdeco-spacing-6);
  background: var(--artdeco-bg-base);
  min-height: 400px;
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-shadow: var(--artdeco-glow-subtle);
  }

  .request-trace {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--artdeco-spacing-6);
  margin-bottom: var(--artdeco-spacing-8);
}

.stat-card {
  @include artdeco-stepped-corners(12px);
  @include artdeco-hover-lift-glow;
  padding: 1px; // 为边框发光留出空间
  background: linear-gradient(135deg, var(--artdeco-gold-primary), transparent);

  .card-inner {
    background: var(--artdeco-bg-card);
    padding: var(--artdeco-spacing-5);
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .index-name {
    font-family: var(--font-display);
    font-size: var(--artdeco-text-lg);
    margin-bottom: var(--artdeco-spacing-2);
  }

  .index-value {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-3xl);
    font-weight: var(--artdeco-font-bold);
    margin-bottom: var(--artdeco-spacing-1);
  }

  .index-change {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xl);

    &.rise { color: var(--artdeco-rise); }
    &.down { color: var(--artdeco-down); }
  }
}

.distribution-section {
  padding: var(--artdeco-spacing-6);
  @include artdeco-geometric-corners;

  .subsection-title {
    font-family: var(--font-display);
    color: var(--artdeco-gold-primary);
    margin-bottom: var(--artdeco-spacing-4);
  }
}

.distribution-bar {
  display: flex;
  height: 32px;
  background: var(--artdeco-bg-elevated);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;
  border: 1px solid var(--artdeco-border-default);

  .bar-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-sm);
    transition: width 1s ease-in-out;
  }

  .rise-segment { background: var(--artdeco-rise); }
  .flat-segment { background: var(--artdeco-flat); }
  .down-segment { background: var(--artdeco-down); }
}
</style>
