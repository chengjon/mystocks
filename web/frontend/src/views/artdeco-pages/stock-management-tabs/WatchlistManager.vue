<template>
  <div class="watchlist-manager-page">
    <div class="page-header">
      <h2 class="section-title">组合管理</h2>
      <div class="trace-info" v-if="lastRequestId">REQ: {{ lastRequestId }}</div>
    </div>

    <div class="watchlist-manager">
      <div class="overview-grid">
        <ArtDecoStatCard label="组合数量" :value="displayWatchlists.length" variant="gold" />
        <ArtDecoStatCard label="当前股票数" :value="stocksCount" variant="gold" />
        <ArtDecoStatCard label="上涨家数" :value="upCount" variant="rise" />
        <ArtDecoStatCard label="下跌家数" :value="downCount" variant="fall" />
      </div>

      <div v-if="showErrorState" class="empty-state empty-state--error">
        持仓组合加载失败：{{ error }}
      </div>

      <div v-else-if="showEmptyState" class="empty-state">
        暂无自选组合。
      </div>

      <template v-else>
        <div class="watchlist-header">
          <div class="watchlist-tabs">
            <button
              v-for="list in displayWatchlists"
              :key="list.id"
              class="watchlist-tab"
              :class="{ active: resolvedActiveWatchlistId === list.id }"
              @click="emit('select-list', list.id)"
            >
              {{ list.name }}
              <span class="count">{{ list.stocks.length }}</span>
            </button>
            <button class="add-list-btn" @click="emit('add-list')">+</button>
          </div>
          <div class="actions">
            <ArtDecoButton variant="outline" size="sm" @click="emit('import')">导入</ArtDecoButton>
            <ArtDecoButton variant="outline" size="sm" @click="emit('export')">导出</ArtDecoButton>
          </div>
        </div>

        <ArtDecoCard title="组合持仓明细" hoverable>
          <ArtDecoTable :columns="columns" :data="currentStocks">
            <template #action="{ row }">
              <ArtDecoButton variant="outline" size="sm" @click="emit('remove-stock', row)">删除</ArtDecoButton>
            </template>
          </ArtDecoTable>
        </ArtDecoCard>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { apiClient } from '@/api/apiClient'

interface StockRow {
  [key: string]: unknown
  change?: number | string
}

interface WatchlistItem {
  id: string
  name: string
  stocks: unknown[]
}

interface Props {
  watchlists: WatchlistItem[]
  activeWatchlistId: string
  currentStocks: StockRow[]
}

const props = withDefaults(defineProps<Props>(), {
  watchlists: () => [],
  activeWatchlistId: '',
  currentStocks: () => []
})

const emit = defineEmits(['select-list', 'add-list', 'import', 'export', 'remove-stock'])
const internalWatchlists = ref<WatchlistItem[]>([])
const { error, lastRequestId, exec } = useArtDecoApi()

const displayWatchlists = computed(() => props.watchlists.length > 0 ? props.watchlists : internalWatchlists.value)
const resolvedActiveWatchlistId = computed(() => props.activeWatchlistId || displayWatchlists.value[0]?.id || '')

const numericChanges = computed(() => props.currentStocks.map((row) => {
  const value = row.change
  if (typeof value === 'number') return value
  if (typeof value === 'string') return Number(value.replace('%', ''))
  return 0
}))

const stocksCount = computed(() => props.currentStocks.length)
const upCount = computed(() => numericChanges.value.filter((value) => value > 0).length)
const downCount = computed(() => numericChanges.value.filter((value) => value < 0).length)
const showErrorState = computed(() => Boolean(error.value) && displayWatchlists.value.length === 0)
const showEmptyState = computed(() => !error.value && displayWatchlists.value.length === 0)

const columns = [
  { key: 'symbol', label: '代码', width: '100px' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'action', label: '操作', width: '90px' }
]

async function loadWatchlists() {
  if (props.watchlists.length > 0) {
    return
  }

  const response = await exec(() => apiClient.get('/watchlist'), {
    silent: true,
    errorMsg: '自选组合加载失败'
  })

  const rows = Array.isArray((response as { data?: unknown[] } | null)?.data)
    ? (response as { data: Array<Record<string, unknown>> }).data
    : Array.isArray(response)
      ? (response as Array<Record<string, unknown>>)
      : []

  internalWatchlists.value = rows.map((row, index) => ({
    id: String(row.id ?? row.watchlist_id ?? `watchlist-${index + 1}`),
    name: String(row.name ?? row.watchlist_name ?? `组合 ${index + 1}`),
    stocks: Array.isArray(row.stocks) ? row.stocks : []
  }))
}

onMounted(() => {
  void loadWatchlists()
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.watchlist-manager-page {
  display: grid;
  gap: var(--artdeco-spacing-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-size: var(--artdeco-text-2xl);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.trace-info {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
}

.watchlist-manager {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.empty-state {
  padding: var(--artdeco-spacing-5);
  border: thin solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
  color: var(--artdeco-fg-primary);

  &--error {
    color: var(--artdeco-rise);
  }
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.watchlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.watchlist-tabs {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.watchlist-tab {
  background: var(--artdeco-bg-card);
  border: thin solid var(--artdeco-border-default);
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-10);
  }

  .count {
    margin-left: var(--artdeco-spacing-2);
    font-size: var(--artdeco-text-xs);
    opacity: 60%;
  }
}

.add-list-btn {
  @extend .watchlist-tab;
  width: 2.5rem;
  padding: var(--artdeco-spacing-2) 0;
}

.actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}
</style>
