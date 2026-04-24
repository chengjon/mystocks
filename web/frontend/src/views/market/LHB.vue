<template>
  <div class="lhb-analysis" :class="{ 'is-embedded': isEmbedded, [pageToneClass]: true }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">dragon tiger desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ: {{ lastRequestId }}</span>
            <span>DATE: {{ currentDateLabel }}</span>
            <span>FILTER: {{ currentFilterLabel }}</span>
            <span>ROWS: {{ displayRows.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="龙虎榜工作台"
        subtitle="统一审查上榜原因、净买入和换手率，形成异常活跃标的的复盘入口"
        :show-status="true"
        :status-text="pageStatusText"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" :disabled="loading" @click="fetchDragonTigerRows">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新榜单
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="榜单条目" :value="displayRows.length" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="当前日期" :value="currentDateLabel" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="当前榜单" :value="currentFilterLabel" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="最高换手" :value="topTurnover" :show-change="false" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">anomaly leaderboard route</span>
          <h2 class="content-shell-title">上榜记录与筛选面板</h2>
          <p class="content-shell-subtitle">{{ activeFilterDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>FILTER: {{ currentFilterLabel }}</span>
          <span>DATE: {{ currentDateLabel }}</span>
        </div>
      </div>

      <div v-if="error" class="state-banner state-banner--error" role="alert">
        <span>龙虎榜加载失败，已保留上一份有效榜单。</span>
        <ArtDecoButton variant="outline" size="sm" @click="fetchDragonTigerRows">重试</ArtDecoButton>
      </div>

      <div v-else-if="showEmptyState" class="state-banner state-banner--empty" role="status" aria-live="polite">
        <span>{{ selectedDateUnavailable ? `${currentDateLabel}暂无可用交易日数据。` : '当前筛选条件下暂无龙虎榜记录。' }}</span>
      </div>

      <ArtDecoCard title="龙虎榜数据" hoverable class="lhb-card">
        <div class="lhb-controls">
          <ArtDecoSelect
            :model-value="currentDate"
            :options="dateOptions"
            label="交易日筛选"
            placeholder="选择日期"
            @update:model-value="handleDateChange"
          />
          <div class="lhb-filters">
            <button
              v-for="(f, _idx) in filters"
              :key="f.key"
              class="filter-btn"
              :class="{ active: currentFilter === f.key }"
              type="button"
              :aria-pressed="currentFilter === f.key"
              @click="handleFilterChange(f.key)"
            >
              {{ f.label }}
            </button>
          </div>
        </div>

        <ArtDecoTable :columns="columns" :data="displayRows" />
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref, watch } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { extractDragonTigerRows } from './dragonTigerData'

interface Props {
  lhbData: unknown[]
  lhbDate: string
  activeFilter: string
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  lhbData: () => [],
  lhbDate: 'today',
  activeFilter: 'buy',
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})
const emit = defineEmits(['date-change', 'filter-change'])
const { loading, error, lastRequestId, exec } = useArtDecoApi()
const instance = getCurrentInstance()
const internalPayload = ref<unknown[]>([])
const currentDate = ref(props.lhbDate)
const currentFilter = ref(props.activeFilter)
const hasLoaded = ref(false)

watch(() => props.lhbDate, (value) => {
  currentDate.value = value
})

watch(() => props.activeFilter, (value) => {
  currentFilter.value = value
})

const hasExternalRows = computed(() => Array.isArray(props.lhbData) && props.lhbData.length > 0)
const isEmbedded = computed(() => {
  const rawProps = instance?.vnode.props
  return Boolean(props.functionKey) || Boolean(rawProps && ('lhbData' in rawProps || 'onDateChange' in rawProps || 'onFilterChange' in rawProps))
})
const sourceRows = computed(() => (hasExternalRows.value ? props.lhbData : internalPayload.value))
const selectedDateIndex = computed(() => {
  if (currentDate.value === 'yesterday') return 1
  if (currentDate.value === 'dayBefore') return 2
  return 0
})
const availableTradeDates = computed(() => {
  return [...new Set(sourceRows.value.map((row) => String((row as { trade_date?: unknown })?.trade_date ?? '')).filter(Boolean))].sort().reverse()
})
const selectedDateUnavailable = computed(() => sourceRows.value.length > 0 && !availableTradeDates.value[selectedDateIndex.value])
const displayRows = computed(() => {
  if (selectedDateUnavailable.value) {
    return []
  }
  return extractDragonTigerRows(sourceRows.value, currentFilter.value, currentDate.value)
})

const dateOptions = [
  { label: '今日', value: 'today' },
  { label: '昨日', value: 'yesterday' },
  { label: '前日', value: 'dayBefore' }
]

const filters = [
  { key: 'buy', label: '买入榜' },
  { key: 'sell', label: '卖出榜' },
  { key: 'institution', label: '机构榜' }
]

const currentDateLabel = computed(() => dateOptions.find((item) => item.value === currentDate.value)?.label ?? '今日')
const currentFilterLabel = computed(() => filters.find((item) => item.key === currentFilter.value)?.label ?? '买入榜')
const topTurnover = computed(() => {
  if (!displayRows.value.length) return '--'
  const maxTurnover = Math.max(...displayRows.value.map((row) => Number.parseFloat(row.turnoverRate) || 0))
  return `${maxTurnover.toFixed(2)}%`
})
const activeFilterDescription = computed(() => {
  if (currentFilter.value === 'sell') {
    return '聚焦净卖出占优的龙虎榜标的，识别资金撤离与情绪反转的信号。'
  }
  if (currentFilter.value === 'institution') {
    return '聚焦机构席位上榜记录，快速识别机构参与度较高的交易席位。'
  }
  return '聚焦净买入占优的龙虎榜标的，识别资金追涨与主导方向。'
})
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  if (error.value) return '榜单异常'
  if (displayRows.value.length === 0) return '暂无上榜'
  return `${currentFilterLabel.value}在线`
})
const pageToneClass = computed(() => {
  if (loading.value) return 'is-loading'
  if (error.value) return 'is-error'
  return currentFilter.value === 'sell' ? 'is-fall' : 'is-rise'
})
const showEmptyState = computed(() => hasLoaded.value && !loading.value && !error.value && displayRows.value.length === 0)

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'tradeDate', label: '交易日', width: '120px' },
  { key: 'stockInfo', label: '股票信息' },
  { key: 'reason', label: '上榜原因' },
  { key: 'buyAmount', label: '买入金额', align: 'right' },
  { key: 'sellAmount', label: '卖出金额', align: 'right' },
  {
    key: 'netBuy',
    label: '净买入',
    align: 'right',
    class: (row: unknown) => {
      const netBuy = Number.parseFloat(String((row as { netBuy?: string })?.netBuy ?? '0'))
      if (netBuy > 0) return 'net-buy--rise'
      if (netBuy < 0) return 'net-buy--fall'
      return 'net-buy--flat'
    }
  },
  { key: 'turnoverRate', label: '换手率', align: 'right' }
]

const fetchDragonTigerRows = async () => {
  const data = await exec(() => apiClient.get('/v2/market/lhb', { params: { limit: 100 } }), {
    silent: true
  })

  if (data) {
    const nextPayload = data && typeof data === 'object' ? (data as { data?: unknown[] }).data ?? data : data
    internalPayload.value = Array.isArray(nextPayload) ? nextPayload : []
  }
  hasLoaded.value = true
}

function handleDateChange(value: string) {
  currentDate.value = value
  emit('date-change', value)
}

function handleFilterChange(value: string) {
  currentFilter.value = value
  emit('filter-change', value)
}

onMounted(() => {
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  } else {
    hasLoaded.value = true
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.lhb-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.artdeco-card-shell {
  position: relative;
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background:
    linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 68%),
    color-mix(in srgb, var(--artdeco-bg-card) 94%, transparent);
  box-shadow:
    inset 0 0 0 1px color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent),
    var(--artdeco-glow-subtle);
}

.artdeco-card-shell::after {
  content: '';
  position: absolute;
  inset: var(--artdeco-spacing-2);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 14%, transparent);
  pointer-events: none;
}

.lhb-analysis.is-embedded {
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
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-variant-numeric: tabular-nums;
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.lhb-analysis.is-rise :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-rise) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-rise) 10%, transparent);
}

.lhb-analysis.is-rise :deep(.status-dot) {
  background: var(--artdeco-rise);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-rise);
}

.lhb-analysis.is-fall :deep(.status-indicator),
.lhb-analysis.is-error :deep(.status-indicator) {
  border-color: color-mix(in srgb, var(--artdeco-down) 48%, var(--artdeco-border-default));
  background: color-mix(in srgb, var(--artdeco-down) 10%, transparent);
}

.lhb-analysis.is-fall :deep(.status-dot),
.lhb-analysis.is-error :deep(.status-dot) {
  background: var(--artdeco-down);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-down);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.state-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-border-default);
}

.state-banner--error {
  background: color-mix(in srgb, var(--artdeco-down) 8%, transparent);
  border-color: color-mix(in srgb, var(--artdeco-down) 32%, var(--artdeco-border-default));
}

.state-banner--empty {
  background: color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent);
}

.lhb-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
}

.lhb-controls :deep(.artdeco-select select) {
  min-height: 44px;
}

.lhb-controls :deep(.artdeco-select select:focus-visible),
.lhb-analysis :deep(.artdeco-button:focus-visible),
.filter-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 1px var(--artdeco-gold-primary), var(--artdeco-glow-subtle);
}

.lhb-filters {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.filter-btn {
  background: transparent;
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  min-height: 44px;
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }
}

.lhb-analysis :deep(.net-buy--rise) {
  color: var(--artdeco-rise);
}

.lhb-analysis :deep(.net-buy--fall) {
  color: var(--artdeco-down);
}

.lhb-analysis :deep(.net-buy--flat) {
  color: var(--artdeco-flat);
}

@media (width <= 75rem) {
  .lhb-analysis :deep(.artdeco-header) {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .lhb-analysis :deep(.header-right) {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .state-banner {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (width <= 48rem) {
  .lhb-analysis :deep(.header-status),
  .lhb-analysis :deep(.header-actions) {
    width: 100%;
  }

  .lhb-analysis :deep(.header-actions .artdeco-button) {
    width: 100%;
  }

  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta,
  .lhb-controls {
    width: 100%;
  }

  .lhb-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .lhb-filters {
    flex-wrap: wrap;
  }

  .artdeco-card-shell {
    padding: var(--artdeco-spacing-4);
  }
}
</style>
