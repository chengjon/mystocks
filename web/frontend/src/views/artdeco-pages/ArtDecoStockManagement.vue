<template>
  <div class="artdeco-stock-management">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">adaptive stock command desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ requestTraceId }}</span>
            <span>SYNC: {{ syncLabel }}</span>
            <span>FOCUS: {{ activeTabMeta.label }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="智能选股管理"
        subtitle="动态自选池 · 实时持仓监控 · 行业深度归因"
        :show-status="true"
        :status-text="syncLabel"
      >
        <template #actions>
          <ArtDecoButton variant="solid" size="sm" @click="handleAddStock">
            <template #icon><ArtDecoIcon name="plus" /></template>
            添加股票
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="组合数量" :value="watchlists.length" variant="gold" />
      <ArtDecoStatCard label="当前股票数" :value="currentWatchlistStocks.length" variant="gold" />
      <ArtDecoStatCard label="持仓数量" :value="positions.length" variant="gold" />
      <ArtDecoStatCard label="当前焦点" :value="activeTabMeta.label" variant="gold" />
    </section>

    <section class="tabs-shell artdeco-card-shell">
      <div class="tabs-shell-header">
        <div class="tabs-shell-copy">
          <span class="tabs-shell-eyebrow">portfolio route</span>
          <h2 class="tabs-shell-title">自选与持仓工作流</h2>
          <p class="tabs-shell-subtitle">{{ activeTabMeta.description }}</p>
        </div>
        <div class="tabs-shell-trace">
          <span>TABS: {{ tabs.length }}</span>
          <span>WATCHLISTS: {{ watchlists.length }}</span>
        </div>
      </div>

      <nav class="main-tabs">
        <button
          v-for="(tab, _idx) in tabs"
          :key="tab.key"
          class="main-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <ArtDecoIcon :name="tab.icon" size="sm" class="tab-icon" />
          <span>{{ tab.label }}</span>
        </button>
      </nav>
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">{{ activeTabMeta.eyebrow }}</span>
          <h3 class="content-shell-title">{{ activeTabMeta.label }}</h3>
        </div>
        <div class="content-shell-meta">
          <span>MODE: {{ syncLabel }}</span>
          <span>STOCKS: {{ currentWatchlistStocks.length }}</span>
        </div>
      </div>

      <div class="tab-content">
        <transition name="fade" mode="out-in">
          <div :key="activeTab" class="tab-panel">
            <WatchlistManager
              v-if="activeTab === 'watchlist'"
              :watchlists="watchlists"
              :active-watchlist-id="activeWatchlistId"
              :current-stocks="currentWatchlistStocks"
              @select-list="activeWatchlistId = $event"
            />
            <PortfolioMonitor
              v-else-if="activeTab === 'portfolio'"
              :positions="positions"
            />
            <ArtDecoCard v-else title="行业归因" class="attribution-placeholder" hoverable>
              <div class="placeholder-body">
                <p class="placeholder-title">行业归因能力整理中</p>
                <p class="placeholder-text">
                  当前已完成自选管理与持仓监控工作流，行业归因将在同一工作台里补齐板块暴露、行业权重和收益来源分析。
                </p>
                <ul class="placeholder-list">
                  <li>组合行业权重与集中度透视</li>
                  <li>行业收益贡献与拖累拆分</li>
                  <li>与风险管理页的一致性联动</li>
                </ul>
              </div>
            </ArtDecoCard>
          </div>
        </transition>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArtDecoHeader, ArtDecoButton, ArtDecoIcon, ArtDecoCard, ArtDecoStatCard } from '@/components/artdeco'
import WatchlistManager from './stock-management-tabs/WatchlistManager.vue'
import PortfolioMonitor from './stock-management-tabs/PortfolioMonitor.vue'
import apiClient from '@/api/apiClient'

const activeTab = ref('watchlist')
const tabs = [
  {
    key: 'watchlist',
    label: '自选管理',
    icon: 'Bookmark',
    eyebrow: 'watchlist matrix',
    description: '维护动态自选池、组合分组和关注股票的结构化清单。'
  },
  {
    key: 'portfolio',
    label: '持仓监控',
    icon: 'Positions',
    eyebrow: 'portfolio lens',
    description: '监控当前持仓的仓位、成本、现价和盈亏表现。'
  },
  {
    key: 'attribution',
    label: '行业归因',
    icon: 'FactorAnalysis',
    eyebrow: 'sector attribution',
    description: '汇总行业暴露、收益来源和板块层面的贡献分析。'
  }
]

interface WatchlistItem {
  id: string
  name: string
  stocks: StockRow[]
}

interface StockRow {
  symbol: string
  name: string
  [key: string]: unknown
}

interface PositionRow {
  symbol?: string
  name?: string
  quantity?: number
  cost?: number
  price?: number
  pnl?: number
  marketValue?: number
  positionPercent?: number
}

const activeWatchlistId = ref('')
const watchlists = ref<WatchlistItem[]>([])
const positions = ref<PositionRow[]>([])
const dataLoaded = ref(false)

const currentWatchlistStocks = computed(() => {
  return watchlists.value.find((l) => l.id === activeWatchlistId.value)?.stocks || []
})
const activeTabMeta = computed(() => tabs.find((tab) => tab.key === activeTab.value) || tabs[0])
const requestTraceId = computed(() => 'N/A')
const syncLabel = computed(() => dataLoaded.value ? '云同步完成' : '待同步')

function parseOptionalNumber(value: unknown): number | undefined {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : undefined
  }

  if (typeof value === 'string' && value.trim()) {
    const parsed = Number.parseFloat(value.replace(/,/g, ''))
    return Number.isFinite(parsed) ? parsed : undefined
  }

  return undefined
}

function parseOptionalString(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value : undefined
}

function normalizePercent(value: number | undefined): number | undefined {
  if (value === undefined) {
    return undefined
  }

  return Math.abs(value) <= 1 ? value * 100 : value
}

function normalizePositions(payload: unknown): PositionRow[] {
  if (!Array.isArray(payload)) {
    return []
  }

  return payload.map((item) => {
    const record = typeof item === 'object' && item !== null ? item as Record<string, unknown> : {}

    return {
      symbol: parseOptionalString(record.symbol),
      name: parseOptionalString(record.name ?? record.symbol_name),
      quantity: parseOptionalNumber(record.quantity),
      cost: parseOptionalNumber(record.average_cost ?? record.cost_price ?? record.cost),
      price: parseOptionalNumber(record.current_price ?? record.price),
      pnl: parseOptionalNumber(record.unrealized_pnl ?? record.profit_loss ?? record.pnl),
      marketValue: parseOptionalNumber(record.market_value ?? record.marketValue),
      positionPercent: normalizePercent(parseOptionalNumber(record.weight ?? record.position_percent ?? record.positionPercent))
    }
  })
}

const fetchData = async () => {
  try {
    const [wlRes, portRes] = await Promise.all([
      apiClient.get('/api/portfolio/v2/watchlist'),
      apiClient.get('/api/portfolio/v2/summary')
    ])

    if (wlRes.data?.success) {
      watchlists.value = wlRes.data.data as WatchlistItem[]
      if (watchlists.value.length > 0 && !activeWatchlistId.value) {
        activeWatchlistId.value = watchlists.value[0].id
      }
    }

    if (portRes.data?.success) {
      positions.value = normalizePositions(portRes.data?.data?.positions)
    }
  } catch (e) {
    console.error('Failed to fetch stock management data', e)
  } finally {
    dataLoaded.value = true
  }
}

const handleAddStock = () => {
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-stock-management {
  background: var(--artdeco-bg-global);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 18% 10%, color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent) 0%, transparent 34%),
      radial-gradient(circle at 84% 14%, color-mix(in srgb, var(--artdeco-bronze) 4%, transparent) 0%, transparent 28%);
    z-index: 0;
  }
}

.hero-shell,
.stats-strip,
.tabs-shell,
.content-shell {
  position: relative;
  z-index: 1;
}

.artdeco-card-shell {
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(
    145deg,
    var(--artdeco-gold-opacity-05),
    color-mix(in srgb, var(--artdeco-bg-global) 92%, transparent)
  );
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, var(--artdeco-fg-primary) 3%, transparent),
    0 var(--artdeco-spacing-2) var(--artdeco-spacing-6) color-mix(in srgb, var(--artdeco-bg-global) 82%, transparent);
}

.hero-shell {
  padding: var(--artdeco-spacing-5);

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-10));
    height: calc(var(--artdeco-spacing-1) / 2);
    background: linear-gradient(
      90deg,
      transparent,
      var(--artdeco-gold-primary),
      var(--artdeco-bronze),
      var(--artdeco-gold-primary),
      transparent
    );
    box-shadow: 0 0 var(--artdeco-spacing-5) color-mix(in srgb, var(--artdeco-gold-primary) 45%, transparent);
  }
}

.hero-rail,
.tabs-shell-header,
.content-shell-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.tabs-shell-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.tabs-shell-eyebrow,
.content-shell-kicker {
  font-size: var(--artdeco-text-xs);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
}

.hero-meta,
.tabs-shell-trace,
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
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
}

.tabs-shell {
  padding: var(--artdeco-spacing-4);
}

.tabs-shell-title,
.content-shell-title {
  margin: 0;
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.tabs-shell-title {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-2xl);
}

.tabs-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  max-width: calc(var(--artdeco-spacing-32) * 3 + var(--artdeco-spacing-20));
  line-height: var(--artdeco-leading-relaxed);
}

.main-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
  margin-top: var(--artdeco-spacing-4);
  border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-opacity-10);
  padding-bottom: var(--artdeco-spacing-2);
  flex-wrap: wrap;
}

.main-tab {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  text-transform: uppercase;
  font-family: var(--artdeco-font-body);
  letter-spacing: var(--artdeco-tracking-wide);
  transition:
    border-color var(--artdeco-transition-base),
    background-color var(--artdeco-transition-base),
    color var(--artdeco-transition-base),
    box-shadow var(--artdeco-transition-base),
    transform var(--artdeco-transition-base);

  &:hover {
    color: var(--artdeco-accent-gold);
    border-color: var(--artdeco-accent-gold);
    background: var(--artdeco-gold-opacity-05);
    transform: translateY(calc(var(--artdeco-spacing-1) / -2));
  }

  &.active {
    color: var(--artdeco-accent-gold);
    border-color: var(--artdeco-accent-gold);
    background: var(--artdeco-gold-opacity-08);
    box-shadow: var(--artdeco-glow-subtle);
  }
}

.tab-icon {
  flex-shrink: 0;
}

.content-shell {
  padding: var(--artdeco-spacing-5);
}

.content-shell-title {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
}

.tab-content {
  margin-top: var(--artdeco-spacing-4);
}

.attribution-placeholder {
  background: transparent;
}

.placeholder-body {
  padding: var(--artdeco-spacing-6);
  border: 1px dashed var(--artdeco-border-accent);
  background: var(--artdeco-gold-opacity-05);
}

.placeholder-title {
  margin: 0 0 var(--artdeco-spacing-2);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-gold-primary);
}

.placeholder-text {
  margin: 0 0 var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  line-height: var(--artdeco-leading-relaxed);
}

.placeholder-list {
  margin: 0;
  padding-left: var(--artdeco-spacing-5);
  color: var(--artdeco-fg-primary);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.fade-enter-active, .fade-leave-active { transition: opacity var(--artdeco-transition-base); }
.fade-enter-from, .fade-leave-to { opacity: 0%; }

@media (width <= var(--artdeco-breakpoint-lg)) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= var(--artdeco-breakpoint-md)) {
  .stats-strip {
    grid-template-columns: minmax(0, 1fr);
  }

  .main-tab {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
