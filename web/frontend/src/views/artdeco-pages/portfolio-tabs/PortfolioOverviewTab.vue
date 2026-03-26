<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import {
  extractTradePositionsPayload,
  toPortfolioOverviewData,
  type PortfolioOverviewData
} from './portfolioOverviewData'

const { loading, lastRequestId, exec } = useArtDecoApi()
const portfolio = ref<PortfolioOverviewData>(toPortfolioOverviewData(null))
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return (portfolio.value?.today_pnl ?? 0) >= 0 ? '组合偏强' : '组合承压'
})
const pageStatusType = computed(() => ((portfolio.value?.today_pnl ?? 0) >= 0 ? 'success' : 'warning'))

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
    .slice(0, 8)
})

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
    .slice(0, 6)
})

const positionCount = computed(() => portfolio.value?.positions?.length || 0)
const totalAssetsLabel = computed(() =>
  portfolio.value?.total_assets?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) || '0.00'
)
const todayPnlLabel = computed(() =>
  `${(portfolio.value?.today_pnl ?? 0) >= 0 ? '+' : ''}${portfolio.value?.today_pnl?.toLocaleString() || 0}`
)

const fetchPortfolio = async () => {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), {
    silent: true
  })

  portfolio.value = toPortfolioOverviewData(extractTradePositionsPayload(responseData))
}

onMounted(() => {
  void fetchPortfolio()
})
</script>

<template>
  <div class="portfolio-overview-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">portfolio assets desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ: {{ lastRequestId }}</span>
            <span>POSITIONS: {{ positionCount }}</span>
            <span>REBALANCE: {{ autoRebalanceSuggestions.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="组合资产工作台"
        subtitle="统一查看资产规模、持仓分布、绩效归因和再平衡建议"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchPortfolio">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新资产
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="总资产" :value="totalAssetsLabel" variant="gold" />
      <ArtDecoStatCard label="今日盈亏" :value="todayPnlLabel" :variant="(portfolio?.today_pnl ?? 0) >= 0 ? 'rise' : 'fall'" />
      <ArtDecoStatCard label="持仓数量" :value="positionCount" variant="gold" />
      <ArtDecoStatCard label="再平衡建议" :value="autoRebalanceSuggestions.length" variant="gold" />
    </section>

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
@use '@/styles/artdeco-tokens.scss' as *;

.portfolio-overview-tab {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.hero-shell,
.stats-strip {
  width: 100%;
}

.hero-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.hero-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.assets-hero {
  position: relative;
  background: var(--artdeco-bg-elevated);
  margin-bottom: var(--artdeco-spacing-10);
  padding: var(--artdeco-spacing-8);

  @include artdeco-stepped-corners(var(--artdeco-spacing-5));

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
    margin-bottom: var(--artdeco-spacing-2);
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
      margin-left: calc(var(--artdeco-spacing-5) / 2);
    }
  }
}

.positions-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fit,
    minmax(calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-6)), 1fr)
  );
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
        font-size: calc(var(--artdeco-spacing-5) / 2);
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        margin-bottom: var(--artdeco-spacing-1);
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
  border-left: var(--artdeco-spacing-1) solid var(--artdeco-gold-primary);
  padding-left: var(--artdeco-spacing-3);
}

.attribution-section,
.rebalance-section {
  margin-top: var(--artdeco-spacing-8);
}

.attribution-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fit,
    minmax(calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-12) + var(--artdeco-spacing-3)), 1fr)
  );
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
    gap: calc(var(--artdeco-spacing-1) / 2);

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

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta {
    width: 100%;
  }
}
</style>
