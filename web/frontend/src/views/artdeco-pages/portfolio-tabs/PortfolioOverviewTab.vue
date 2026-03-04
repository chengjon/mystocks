<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';
import {
  extractTradePositionsPayload,
  toPortfolioOverviewData,
  type PortfolioOverviewData
} from './portfolioOverviewData';

const { loading, lastRequestId, exec } = useArtDecoApi();
const portfolio = ref<PortfolioOverviewData>(toPortfolioOverviewData(null));

const fetchPortfolio = async () => {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), {
    silent: true
  });

  portfolio.value = toPortfolioOverviewData(extractTradePositionsPayload(responseData));
};

onMounted(() => {
  fetchPortfolio();
});
</script>

<template>
  <div class="portfolio-overview-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">Portfolio Assets</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <!-- 资产大卡片 -->
    <div class="assets-hero artdeco-card" v-loading="loading">
      <div class="hero-content">
        <div class="asset-main">
          <label>Total Assets (CNY)</label>
          <div class="value">{{ portfolio?.total_assets?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</div>
        </div>
        <div class="asset-pnl">
          <label>Today's P&L</label>
          <div :class="['pnl-value', (portfolio?.today_pnl ?? 0) >= 0 ? 'rise' : 'down']">
            {{ (portfolio?.today_pnl ?? 0) >= 0 ? '+' : '' }}{{ portfolio?.today_pnl?.toLocaleString() }}
            <span class="pct">({{ portfolio?.today_pnl_pct }}%)</span>
          </div>
        </div>
      </div>
      <div class="hero-decoration"></div>
    </div>

    <!-- 持仓列表 -->
    <div class="position-list-section">
      <h3 class="subsection-title">Top Positions</h3>
      <div class="positions-grid">
        <div v-for="pos in portfolio?.positions" :key="pos.symbol" class="position-item artdeco-card">
          <div class="pos-header">
            <span class="name">{{ pos.name }}</span>
            <span class="symbol">{{ pos.symbol }}</span>
          </div>
          <div class="pos-data">
            <div class="data-group">
              <label>Market Value</label>
              <div class="val">{{ pos.market_value.toLocaleString() }}</div>
            </div>
            <div class="data-group">
              <label>P&L %</label>
              <div :class="['val', pos.pnl_pct >= 0 ? 'rise' : 'down']">{{ pos.pnl_pct }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.portfolio-overview-tab {
  padding: var(--artdeco-spacing-6);
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
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }
  .trace-info {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}

.assets-hero {
  position: relative;
  background: var(--artdeco-bg-elevated);
  margin-bottom: var(--artdeco-spacing-10);
  padding: var(--artdeco-spacing-8);

  @include artdeco-stepped-corners(20px);

  border: 1px solid var(--artdeco-gold-primary);

  .hero-content {
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 1;
    position: relative;
  }

  label {
    font-family: var(--artdeco-font-display);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    font-size: var(--artdeco-text-sm);
    letter-spacing: 0.1em;
    display: block;
    margin-bottom: 8px;
  }
  .value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-4xl);
    color: var(--artdeco-gold-primary);
    font-weight: bold;
  }
  .pnl-value {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-2xl);

    &.rise {
      color: var(--artdeco-rise);
    }

    &.down {
      color: var(--artdeco-down);
    }

    .pct {
      font-size: var(--artdeco-text-lg);
      margin-left: 10px;
    }
  }
}

.positions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--artdeco-spacing-6);
}

.position-item {
  padding: var(--artdeco-spacing-5);

  @include artdeco-geometric-corners;

  background: var(--artdeco-bg-card);

  .pos-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-4);
    .name {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-text-lg);
      color: var(--artdeco-gold-light);
    }
    .symbol {
      font-family: var(--artdeco-font-mono);
      color: var(--artdeco-fg-muted);
    }
  }

  .pos-data {
    display: flex;
    justify-content: space-between;
    .data-group {
      label {
        font-size: 10px;
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        margin-bottom: 4px;
        display: block;
      }
      .val {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-md);

        &.rise {
          color: var(--artdeco-rise);
        }

        &.down {
          color: var(--artdeco-down);
        }
      }
    }
  }
}

.subsection-title {
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-gold-primary);
  margin-bottom: var(--artdeco-spacing-6);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  border-left: 4px solid var(--artdeco-gold-primary);
  padding-left: 12px;
}
</style>
