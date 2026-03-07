<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';
import {
  extractTradePositionsPayload,
  toPortfolioOverviewData,
  type PortfolioOverviewData
} from './portfolioOverviewData';

const { loading, lastRequestId, exec } = useArtDecoApi();
const portfolio = ref<PortfolioOverviewData>(toPortfolioOverviewData(null));

const performanceAttribution = computed(() => {
  const positions = portfolio.value?.positions ?? [];
  const total = Math.max(
    1,
    positions.reduce((sum, item) => sum + item.market_value, 0)
  );

  return positions
    .map((item) => {
      const weight = item.market_value / total;
      const pnlContribution = (weight * item.pnl_pct);
      return {
        symbol: item.symbol,
        name: item.name,
        weight: Number((weight * 100).toFixed(2)),
        pnlContribution: Number(pnlContribution.toFixed(2))
      };
    })
    .sort((a, b) => Math.abs(b.pnlContribution) - Math.abs(a.pnlContribution))
    .slice(0, 8);
});

const autoRebalanceSuggestions = computed(() => {
  const positions = portfolio.value?.positions ?? [];
  if (positions.length === 0) {
    return [];
  }

  const total = Math.max(
    1,
    positions.reduce((sum, item) => sum + item.market_value, 0)
  );

  const targetWeight = Math.min(25, Number((100 / positions.length).toFixed(2)));

  return positions
    .map((item) => {
      const currentWeight = Number(((item.market_value / total) * 100).toFixed(2));
      const gap = Number((currentWeight - targetWeight).toFixed(2));
      const amount = Number(((Math.abs(gap) / 100) * total).toFixed(2));
      return {
        symbol: item.symbol,
        name: item.name,
        currentWeight,
        targetWeight,
        gap,
        amount,
        action: gap > 0 ? '减仓' : '加仓'
      };
    })
    .filter((item) => Math.abs(item.gap) >= 3)
    .sort((a, b) => Math.abs(b.gap) - Math.abs(a.gap))
    .slice(0, 6);
});

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

    <div class="attribution-section">
      <h3 class="subsection-title">绩效归因</h3>
      <div class="attribution-grid">
        <div
          v-for="item in performanceAttribution"
          :key="`attr-${item.symbol}`"
          class="attribution-item artdeco-card"
        >
          <div class="item-head">
            <span class="name">{{ item.name }}</span>
            <span class="symbol">{{ item.symbol }}</span>
          </div>
          <div class="item-row">
            <span>权重</span>
            <strong>{{ item.weight }}%</strong>
          </div>
          <div class="item-row">
            <span>收益贡献</span>
            <strong :class="item.pnlContribution >= 0 ? 'rise' : 'down'">
              {{ item.pnlContribution >= 0 ? '+' : '' }}{{ item.pnlContribution }}%
            </strong>
          </div>
        </div>
      </div>
    </div>

    <div class="rebalance-section">
      <h3 class="subsection-title">自动再平衡建议</h3>
      <div class="rebalance-list artdeco-card">
        <div v-if="autoRebalanceSuggestions.length === 0" class="rebalance-empty">
          当前持仓权重偏离较小，暂无自动再平衡建议。
        </div>
        <div v-else>
          <div
            v-for="item in autoRebalanceSuggestions"
            :key="`rebalance-${item.symbol}`"
            class="rebalance-row"
          >
            <div class="rebalance-main">
              <span class="name">{{ item.name }}</span>
              <span class="symbol">{{ item.symbol }}</span>
            </div>
            <div class="rebalance-detail">
              当前 {{ item.currentWeight }}% → 目标 {{ item.targetWeight }}%
            </div>
            <div class="rebalance-action" :class="item.gap > 0 ? 'down' : 'rise'">
              建议{{ item.action }}约 ¥{{ item.amount.toLocaleString('zh-CN') }}
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

.attribution-section,
.rebalance-section {
  margin-top: var(--artdeco-spacing-8);
}

.attribution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--artdeco-spacing-4);
}

.attribution-item {
  padding: var(--artdeco-spacing-4);

  .item-head {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-3);
  }

  .name {
    color: var(--artdeco-gold-light);
    font-family: var(--artdeco-font-display);
  }

  .symbol {
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
  }

  .item-row {
    display: flex;
    justify-content: space-between;
    margin-top: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-sm);

    .rise {
      color: var(--artdeco-rise);
    }

    .down {
      color: var(--artdeco-down);
    }
  }
}

.rebalance-list {
  padding: var(--artdeco-spacing-4);
}

.rebalance-empty {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

.rebalance-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: var(--artdeco-spacing-3);
  align-items: center;
  padding: var(--artdeco-spacing-3) 0;
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);

  &:last-child {
    border-bottom: none;
  }

  .rebalance-main {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .name {
      color: var(--artdeco-gold-light);
      font-family: var(--artdeco-font-display);
    }

    .symbol {
      color: var(--artdeco-fg-muted);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-xs);
    }
  }

  .rebalance-detail {
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }

  .rebalance-action {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-sm);
    font-weight: 600;

    &.rise {
      color: var(--artdeco-rise);
    }

    &.down {
      color: var(--artdeco-down);
    }
  }
}
</style>
