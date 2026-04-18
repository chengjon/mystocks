<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import {
  extractPositionsPayload,
  toTradingPositionRows,
} from '@/views/artdeco-pages/trading-tabs/tradingDataTransform'

export interface Position {
  symbol: string
  name: string
  shares: number
  avgCost: number
  currentPrice: number
  marketValue: number
  pnl: number
  pnlPercent: number
  positionPercent: number
}

const props = defineProps<{
  positions?: Position[]
}>()

const internalPositions = ref<Position[]>([])
const instance = getCurrentInstance()
const { exec, loading, lastRequestId, lastProcessTime } = useArtDecoApi()

const isEmbedded = computed(() => {
  const rawProps = instance?.vnode.props
  return Boolean(rawProps && 'positions' in rawProps)
})

const displayPositions = computed(() => {
  if (Array.isArray(props.positions) && props.positions.length > 0) {
    return props.positions
  }
  return internalPositions.value
})

const totalMarketValue = computed(() =>
  `¥${displayPositions.value.reduce((sum, position) => sum + Number(position.marketValue || 0), 0).toFixed(0)}`,
)
const totalPnl = computed(() =>
  displayPositions.value.reduce((sum, position) => sum + Number(position.pnl || 0), 0),
)
const positiveCount = computed(() =>
  displayPositions.value.filter((position) => position.pnl >= 0).length,
)
const highestWeight = computed(() => {
  if (displayPositions.value.length === 0) return '--'
  const value = Math.max(...displayPositions.value.map((position) => Number(position.positionPercent || 0)))
  return `${value.toFixed(2)}%`
})
const displayRequestId = computed(() => lastRequestId.value || 'N/A')
const displayProcessTime = computed(() => {
  if (!lastProcessTime.value) {
    return 'N/A'
  }
  const value = Number.parseFloat(lastProcessTime.value)
  if (Number.isNaN(value)) {
    return lastProcessTime.value
  }
  return `${value.toFixed(2)}ms`
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return displayPositions.value.length > 0 ? '持仓在线' : '暂无持仓'
})
const pageStatusType = computed(() => {
  if (totalPnl.value > 0) return 'success'
  if (totalPnl.value < 0) return 'warning'
  return 'info'
})

const loadPositions = async () => {
  const responseData = await exec(() => apiClient.get('/v1/trade/positions'), { silent: true })
  internalPositions.value = toTradingPositionRows(extractPositionsPayload(responseData))
}

onMounted(() => {
  if (!Array.isArray(props.positions) || props.positions.length === 0) {
    void loadPositions()
  }
})
</script>

<template>
  <div class="artdeco-trading-positions" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">position ledger desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>TIME: {{ displayProcessTime }}</span>
            <span>ROWS: {{ displayPositions.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="持仓工作台"
        subtitle="统一查看持仓结构、盈亏表现和仓位分布，形成交易域的头寸入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton
            variant="solid"
            priority="primary"
            motion="data"
            size="sm"
            :loading="loading"
            @click="loadPositions"
          >
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新持仓
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="持仓标的" :value="displayPositions.length" variant="gold" />
      <ArtDecoStatCard label="盈利标的" :value="positiveCount" variant="rise" />
      <ArtDecoStatCard label="组合市值" :value="totalMarketValue" variant="gold" />
      <ArtDecoStatCard label="最高仓位" :value="highestWeight" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">position allocation route</span>
          <h3 class="content-shell-title">持仓结构与仓位面板</h3>
          <p class="content-shell-subtitle">从持股数、成本、市值到盈亏与仓位占比，形成完整的持仓监控工作流。</p>
        </div>
        <div class="content-shell-meta">
          <span>MARKET_VALUE: {{ totalMarketValue }}</span>
          <span>TOTAL_PNL: ¥{{ totalPnl.toFixed(0) }}</span>
        </div>
      </div>

      <ArtDecoCard title="持仓明细" hoverable>
        <div class="artdeco-trading-positions__table">
          <div class="artdeco-trading-positions__header">
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol">股票</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares">持股数</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost">平均成本</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price">当前价</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value">市值</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl">盈亏</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent">盈亏%</div>
            <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position">仓位%</div>
          </div>
          <div v-if="displayPositions.length === 0" class="artdeco-trading-positions__empty">
            暂无持仓数据
          </div>
          <div v-else class="artdeco-trading-positions__body">
            <div v-for="position in displayPositions" :key="position.symbol" class="artdeco-trading-positions__row">
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--symbol">
                <div class="artdeco-trading-positions__symbol-name">{{ position.name }}</div>
                <div class="artdeco-trading-positions__symbol-code">{{ position.symbol }}</div>
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--shares">
                {{ position.shares }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--avg-cost">
                ¥{{ position.avgCost }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--current-price">
                ¥{{ position.currentPrice }}
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--market-value">
                ¥{{ position.marketValue }}
              </div>
              <div
                class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl"
                :class="
                  position.pnl >= 0
                    ? 'artdeco-trading-positions__pnl--rise'
                    : 'artdeco-trading-positions__pnl--fall'
                "
              >
                ¥{{ position.pnl }}
              </div>
              <div
                class="artdeco-trading-positions__col artdeco-trading-positions__col--pnl-percent"
                :class="
                  position.pnlPercent >= 0
                    ? 'artdeco-trading-positions__pnl--rise'
                    : 'artdeco-trading-positions__pnl--fall'
                "
              >
                {{ position.pnlPercent >= 0 ? '+' : '' }}{{ position.pnlPercent }}%
              </div>
              <div class="artdeco-trading-positions__col artdeco-trading-positions__col--position">
                <div class="artdeco-trading-positions__position-bar">
                  <div
                    class="artdeco-trading-positions__position-fill"
                    :style="{ width: position.positionPercent + '%' }"
                  ></div>
                  <span class="artdeco-trading-positions__position-text">
                    {{ position.positionPercent }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-patterns.scss' as *;

.artdeco-trading-positions {
  --artdeco-trading-positions-col-symbol: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));
  --artdeco-trading-positions-col-shares: var(--artdeco-spacing-20);
  --artdeco-trading-positions-col-price: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5) / 2);
  --artdeco-trading-positions-col-market-value: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-5));
  --artdeco-trading-positions-table-width: calc(
    var(--artdeco-spacing-32) * 5 + var(--artdeco-spacing-20) + var(--artdeco-spacing-5)
  );
  --artdeco-trading-positions-body-height: calc(var(--artdeco-spacing-20) * 5);
  --artdeco-trading-positions-corner-size: var(--artdeco-spacing-4);
  --artdeco-trading-positions-border-width: calc(var(--artdeco-spacing-1) / 2);
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);

  @include artdeco-stepped-corners(var(--artdeco-spacing-2));
  @include artdeco-geometric-corners(
    $color: var(--artdeco-gold-primary),
    $size: var(--artdeco-trading-positions-corner-size),
    $border-width: var(--artdeco-trading-positions-border-width)
  );
  @include artdeco-hover-lift-glow;
}

.artdeco-trading-positions.is-embedded {
  gap: var(--artdeco-spacing-4);
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
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
  align-items: flex-start;
  justify-content: space-between;
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
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wider);
  color: var(--artdeco-gold-dim);
}

.hero-meta,
.content-shell-meta {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
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

.artdeco-trading-positions__table {
  width: 100%;
  overflow-x: auto;
}

.artdeco-trading-positions__header {
  display: grid;
  grid-template-columns:
    var(--artdeco-trading-positions-col-symbol)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-price)
    var(--artdeco-trading-positions-col-price)
    var(--artdeco-trading-positions-col-market-value)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-market-value);
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);
  border-bottom: 1px solid var(--artdeco-border-default);
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
  min-width: var(--artdeco-trading-positions-table-width);
}

.artdeco-trading-positions__body {
  max-height: var(--artdeco-trading-positions-body-height);
  overflow-y: auto;
}

.artdeco-trading-positions__empty {
  padding: var(--artdeco-spacing-6);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  text-align: center;
}

.artdeco-trading-positions__row {
  display: grid;
  grid-template-columns:
    var(--artdeco-trading-positions-col-symbol)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-price)
    var(--artdeco-trading-positions-col-price)
    var(--artdeco-trading-positions-col-market-value)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-shares)
    var(--artdeco-trading-positions-col-market-value);
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);
  align-items: center;
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  min-width: var(--artdeco-trading-positions-table-width);
  transition: all var(--artdeco-transition-base);

  &:hover {
    background: var(--artdeco-bg-elevated);
  }
}

.artdeco-trading-positions__symbol-name {
  font-weight: 600;
  color: var(--artdeco-fg-primary);
}

.artdeco-trading-positions__symbol-code {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.artdeco-trading-positions__pnl--rise {
  color: var(--artdeco-up);
}

.artdeco-trading-positions__pnl--fall {
  color: var(--artdeco-down);
}

.artdeco-trading-positions__position-bar {
  position: relative;
  width: 100%;
  height: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-elevated);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;
}

.artdeco-trading-positions__position-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-up));
  transition: width var(--artdeco-transition-base);
}

.artdeco-trading-positions__position-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
  color: var(--artdeco-fg-primary);
}

.artdeco-trading-positions__corner {
  position: absolute;
  width: var(--artdeco-trading-positions-corner-size);
  height: var(--artdeco-trading-positions-corner-size);
  border-color: var(--artdeco-gold-primary);
  border-style: solid;
  opacity: 40%;
  transition: opacity var(--artdeco-transition-base);
  z-index: 1;
}

.artdeco-trading-positions__corner--tl {
  top: calc(var(--artdeco-spacing-px) * -1);
  left: calc(var(--artdeco-spacing-px) * -1);
  border-width: var(--artdeco-trading-positions-border-width) 0 0 var(--artdeco-trading-positions-border-width);
}

.artdeco-trading-positions__corner--br {
  bottom: calc(var(--artdeco-spacing-px) * -1);
  right: calc(var(--artdeco-spacing-px) * -1);
  border-width: 0 var(--artdeco-trading-positions-border-width) var(--artdeco-trading-positions-border-width) 0;
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
}
</style>
