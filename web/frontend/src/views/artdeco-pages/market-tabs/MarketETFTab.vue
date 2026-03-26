<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'

interface EtfRow {
  symbol: string
  name: string
  price: number
  change_pct: number
  volume: string
}

const { loading, lastRequestId, exec } = useArtDecoApi()
const etfList = ref<EtfRow[]>([])

const risingCount = computed(() => etfList.value.filter((etf) => etf.change_pct >= 0).length)
const totalVolume = computed(() => {
  const total = etfList.value.reduce((sum, etf) => sum + Number.parseFloat(String(etf.volume).replace(/[^\d.-]/g, '')), 0)
  return `${total.toFixed(1)}B`
})
const topSymbol = computed(() => etfList.value[0]?.symbol || 'N/A')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return risingCount.value >= Math.max(1, etfList.value.length - risingCount.value) ? 'ETF偏强' : 'ETF承压'
})
const pageStatusType = computed(() => (risingCount.value >= Math.max(1, etfList.value.length - risingCount.value) ? 'success' : 'warning'))

const fetchETFs = async () => {
  // 获取 ETF 实时数据 (调用 v1 标准接口)
  const data = await exec(() => apiClient.get('/v1/market/etf', { params: { limit: 15 } }), {
    silent: true
  })
  
  if (data && (data as Record<string, unknown>).items) {
    etfList.value = (data as Record<string, unknown>).items as EtfRow[]
  } else {
    // 降级模拟数据 (仅用于演示，实际生产需后端支持该接口)
    etfList.value = [
      { symbol: '510300', name: '沪深300ETF', price: 3.842, change_pct: 1.25, volume: '4.2B' },
      { symbol: '159915', name: '创业板ETF', price: 2.156, change_pct: -0.85, volume: '2.1B' },
      { symbol: '510050', name: '上证50ETF', price: 2.678, change_pct: 0.42, volume: '1.5B' }
    ]
  }
}

onMounted(() => {
  void fetchETFs()
})
</script>

<template>
  <div class="market-etf-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">etf market pulse</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">ID: {{ lastRequestId }}</span>
            <span>RISING: {{ risingCount }}</span>
            <span>FOCUS: {{ topSymbol }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="ETF 市场工作台"
        subtitle="统一观察 ETF 强弱、成交规模和头部产品，形成被动资金入口面板"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchETFs">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新ETF
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="ETF 样本" :value="etfList.length" variant="gold" />
      <ArtDecoStatCard label="上涨 ETF" :value="risingCount" variant="rise" />
      <ArtDecoStatCard label="总成交量" :value="totalVolume" variant="gold" />
      <ArtDecoStatCard label="头部产品" :value="topSymbol" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">passive flow route</span>
          <h3 class="content-shell-title">ETF 价格与成交面板</h3>
          <p class="content-shell-subtitle">从头部 ETF 的价格、涨跌和成交量结构，观察被动资金与指数偏好的变化。</p>
        </div>
        <div class="content-shell-meta">
          <span>RISING: {{ risingCount }}</span>
          <span>TOTAL: {{ etfList.length }}</span>
        </div>
      </div>

      <div class="etf-grid" v-loading="loading">
        <div v-for="etf in etfList" :key="etf.symbol" class="artdeco-card etf-card">
          <div class="card-inner">
            <div class="etf-info">
              <span class="symbol">{{ etf.symbol }}</span>
              <span class="name">{{ etf.name }}</span>
            </div>
            <div class="etf-price-row">
              <span class="price">{{ etf.price?.toFixed(3) }}</span>
              <span :class="['change', etf.change_pct >= 0 ? 'rise' : 'down']">
                {{ etf.change_pct >= 0 ? '+' : '' }}{{ etf.change_pct }}%
              </span>
            </div>
            <div class="etf-volume">
              <label>VOL:</label>
              <span>{{ etf.volume }}</span>
            </div>
          </div>
          <div class="corner-accents"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-etf-tab {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.hero-shell,
.stats-strip,
.content-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.hero-meta,
.content-shell-meta {
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

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.etf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-20) * 3 - var(--artdeco-spacing-10) + var(--artdeco-spacing-2)), 1fr));
  gap: var(--artdeco-spacing-6);
}

.etf-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  position: relative;

  @include artdeco-hover-lift-glow;

  .card-inner {
    padding: var(--artdeco-spacing-4);
    z-index: 1;
    position: relative;
  }

  .etf-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-4);
    .symbol {
      font-family: var(--artdeco-font-mono);
      color: var(--artdeco-gold-primary);
      font-weight: bold;
    }

    .name {
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-primary);
    }
  }

  .etf-price-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: var(--artdeco-spacing-3);
    .price {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-xl);
    }

    .change {
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

  .etf-volume {
    font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) - var(--artdeco-spacing-px));
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
    label { margin-right: var(--artdeco-spacing-1); }
  }

  @include artdeco-geometric-corners(var(--artdeco-gold-dim), var(--artdeco-spacing-3), var(--artdeco-spacing-px));
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

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }

  .etf-info,
  .etf-price-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-2);
  }
}
</style>
