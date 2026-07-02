<template>
  <div class="lhb-analysis" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">dragon tiger desk</span>
          <div class="hero-meta">
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
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" @click="fetchDragonTigerRows">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新榜单
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="榜单条目" :value="displayRows.length" variant="gold" />
      <ArtDecoStatCard label="当前日期" :value="currentDateLabel" variant="gold" />
      <ArtDecoStatCard label="当前榜单" :value="currentFilterLabel" variant="gold" />
      <ArtDecoStatCard label="最高换手" :value="topTurnover" variant="rise" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">anomaly leaderboard route</span>
          <h3 class="content-shell-title">上榜记录与筛选面板</h3>
          <p class="content-shell-subtitle">{{ activeFilterDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>FILTER: {{ currentFilterLabel }}</span>
          <span>DATE: {{ currentDateLabel }}</span>
        </div>
      </div>

      <ArtDecoCard title="龙虎榜数据" hoverable class="lhb-card">
        <div class="lhb-controls">
          <ArtDecoSelect
            :model-value="currentDate"
            :options="dateOptions"
            placeholder="选择日期"
            @update:model-value="handleDateChange"
          />
          <div class="lhb-filters">
            <button
              v-for="(f, _idx) in filters"
              :key="f.key"
              class="filter-btn"
              :class="{ active: currentFilter === f.key }"
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
import { apiClient } from '@/api/apiClient'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoSelect, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { extractDragonTigerRows, type DragonTigerRow } from './dragonTigerData'

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
const instance = getCurrentInstance()
const internalRows = ref<DragonTigerRow[]>([])
const currentDate = ref(props.lhbDate)
const currentFilter = ref(props.activeFilter)

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
const displayRows = computed(() => {
  if (hasExternalRows.value) {
    return extractDragonTigerRows(props.lhbData, currentFilter.value, currentDate.value)
  }
  return internalRows.value
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
const topTurnover = computed(() => displayRows.value[0]?.turnoverRate ?? '--')
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
  if (displayRows.value.length === 0) return '暂无上榜'
  return `${currentFilterLabel.value}在线`
})
const pageStatusType = computed(() => {
  if (currentFilter.value === 'sell') return 'warning'
  return 'success'
})

const columns = [
  { key: 'rank', label: '排名', width: '60px' },
  { key: 'tradeDate', label: '交易日', width: '120px' },
  { key: 'stockInfo', label: '股票信息' },
  { key: 'reason', label: '上榜原因' },
  { key: 'buyAmount', label: '买入金额', align: 'right' },
  { key: 'sellAmount', label: '卖出金额', align: 'right' },
  { key: 'netBuy', label: '净买入', variant: 'color', align: 'right' },
  { key: 'turnoverRate', label: '换手率', align: 'right' }
]

const fetchDragonTigerRows = async () => {
  let data: unknown
  try {
    data = await apiClient.get('/v1/market/lhb', { params: { limit: 100 } })
  } catch (err) {
    console.error('[LHB] fetch failed', err)
    internalRows.value = []
    return
  }

  const payload: unknown =
    Array.isArray(data) ? data :
    (data && typeof data === 'object' && 'data' in (data as Record<string, unknown>)) ?
      ((data as { data?: unknown }).data ?? []) : data
  internalRows.value = extractDragonTigerRows(
    payload,
    currentFilter.value,
    currentDate.value,
  )
}

function handleDateChange(value: string) {
  currentDate.value = value
  emit('date-change', value)
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  }
}

function handleFilterChange(value: string) {
  currentFilter.value = value
  emit('filter-change', value)
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
  }
}

onMounted(() => {
  if (!hasExternalRows.value) {
    void fetchDragonTigerRows()
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
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
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

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.lhb-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
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
  cursor: pointer;
  transition: all var(--artdeco-duration-base);

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
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
}
</style>
