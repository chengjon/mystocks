<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { dataApi } from '@/api/index'

interface ScannerRow {
  symbol: string
  name: string
  rsi: string
  macd_signal: 'BULL' | 'BEAR'
  trend_score: string
  [key: string]: unknown
}

const { loading, lastRequestId, exec } = useArtDecoApi()
const scannerResults = ref<ScannerRow[]>([])

const bullCount = computed(() => scannerResults.value.filter((row) => row.macd_signal === 'BULL').length)
const overboughtCount = computed(() => scannerResults.value.filter((row) => Number.parseFloat(row.rsi) > 70).length)
const avgTrendScore = computed(() => {
  if (scannerResults.value.length === 0) return '0.0'
  const total = scannerResults.value.reduce((sum, row) => sum + Number.parseFloat(row.trend_score), 0)
  return (total / scannerResults.value.length).toFixed(1)
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return bullCount.value >= Math.max(1, scannerResults.value.length - bullCount.value) ? '多头占优' : '空头占优'
})
const pageStatusType = computed(() => (bullCount.value >= Math.max(1, scannerResults.value.length - bullCount.value) ? 'success' : 'warning'))

const fetchScannerData = async () => {
  // 获取基础股票列表作为扫描展示（实际生产中会调用专门的筛选接口）
  const response = await exec(() => dataApi.getStocksBasic({ limit: 20 }), {
    silent: true
  })

  const items = (response as Record<string, unknown>)?.data as unknown[] | undefined;
  if (response && items) {
    // 模拟添加一些技术指标评分数据
    scannerResults.value = items.map((stock: unknown, index) => {
      const row = stock as Record<string, unknown>
      return {
      ...row,
      symbol: String(row.symbol ?? `UNKNOWN-${index + 1}`),
      name: String(row.name ?? 'UNKNOWN'),
      rsi: (Math.random() * 40 + 30).toFixed(2),
      macd_signal: Math.random() > 0.5 ? 'BULL' : 'BEAR',
      trend_score: (Math.random() * 10).toFixed(1)
      }
    })
  }
}

onMounted(() => {
  void fetchScannerData()
})
</script>

<template>
  <div class="technical-scanner-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">technical scanner desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">ID: {{ lastRequestId }}</span>
            <span>BULL: {{ bullCount }}</span>
            <span>TREND: {{ avgTrendScore }}/10</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="技术扫描工作台"
        subtitle="统一观察 RSI、MACD 和趋势分值，形成技术筛选的快速入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchScannerData">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新扫描
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="扫描样本" :value="scannerResults.length" variant="gold" />
      <ArtDecoStatCard label="多头信号" :value="bullCount" variant="rise" />
      <ArtDecoStatCard label="超买信号" :value="overboughtCount" variant="fall" />
      <ArtDecoStatCard label="平均趋势" :value="`${avgTrendScore}/10`" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">indicator scan route</span>
          <h3 class="content-shell-title">指标筛选与趋势面板</h3>
          <p class="content-shell-subtitle">通过 RSI、MACD 与趋势分值，快速定位当前技术面更强或更弱的标的。</p>
        </div>
        <div class="content-shell-meta">
          <span>OVERBOUGHT: {{ overboughtCount }}</span>
          <span>TOTAL: {{ scannerResults.length }}</span>
        </div>
      </div>

      <div class="scanner-grid" v-loading="loading">
        <div v-for="stock in scannerResults" :key="stock.symbol" class="artdeco-card stock-scan-card">
          <div class="stock-header">
            <span class="symbol">{{ stock.symbol }}</span>
            <span class="name">{{ stock.name }}</span>
          </div>
          
          <div class="indicators">
            <div class="indicator">
              <span class="label">RSI(14)</span>
              <span :class="['value', parseFloat(stock.rsi) > 70 ? 'overbought' : (parseFloat(stock.rsi) < 30 ? 'oversold' : '')]">
                {{ stock.rsi }}
              </span>
            </div>
            <div class="indicator">
              <span class="label">MACD</span>
              <span :class="['value', stock.macd_signal === 'BULL' ? 'rise' : 'down']">
                {{ stock.macd_signal }}
              </span>
            </div>
          </div>

          <div class="trend-gauge">
            <div class="gauge-label">Trend Strength</div>
            <div class="gauge-bar">
              <div class="gauge-fill" :style="{ width: `${Number(stock.trend_score) * 10}%`, background: stock.macd_signal === 'BULL' ? 'var(--artdeco-rise)' : 'var(--artdeco-down)' }"></div>
            </div>
            <div class="gauge-value">{{ stock.trend_score }}/10</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.technical-scanner-tab {
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

.scanner-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(var(--artdeco-spacing-20) * 3), 1fr));
  gap: var(--artdeco-spacing-6);
}

.stock-scan-card {
  padding: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);

  @include artdeco-hover-lift-glow;

  .stock-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-4);
    border-bottom: 1px solid var(--artdeco-gold-opacity-20);
    padding-bottom: var(--artdeco-spacing-2);

    .symbol {
      font-family: var(--artdeco-font-mono);
      font-weight: bold;
      color: var(--artdeco-gold-primary);
    }
    .name {
      font-size: var(--artdeco-text-sm);
    }
  }
}

.indicators {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-4);

  .indicator {
    display: flex;
    justify-content: space-between;
    font-size: var(--artdeco-text-xs);
    
    .label {
      color: var(--artdeco-fg-muted);
    }
    .value {
      font-family: var(--artdeco-font-mono);
      &.overbought { color: var(--artdeco-rise); }
      &.oversold { color: var(--artdeco-down); }
      &.rise { color: var(--artdeco-rise); }
      &.down { color: var(--artdeco-down); }
    }
  }
}

.trend-gauge {
  .gauge-label {
    font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) - var(--artdeco-spacing-px));
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    margin-bottom: var(--artdeco-spacing-1);
  }
  .gauge-bar {
    height: var(--artdeco-spacing-1);
    background: var(--artdeco-bg-elevated);
    margin-bottom: var(--artdeco-spacing-1);
    .gauge-fill {
      height: 100%;
      transition: width 0.5s ease;
    }
  }
  .gauge-value {
    font-family: var(--artdeco-font-mono);
    font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px) - var(--artdeco-spacing-px));
    text-align: right;
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

  .hero-meta,
  .content-shell-meta,
  .stock-header {
    width: 100%;
  }

  .stock-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-2);
  }
}
</style>
