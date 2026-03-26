<template>
  <div class="watchlist-manager">
    <div class="overview-grid">
      <ArtDecoStatCard label="组合数量" :value="displayWatchlists.length" variant="gold" />
      <ArtDecoStatCard label="当前股票数" :value="stocksCount" variant="gold" />
      <ArtDecoStatCard label="上涨家数" :value="upCount" variant="rise" />
      <ArtDecoStatCard label="下跌家数" :value="downCount" variant="fall" />
    </div>

    <div class="watchlist-header">
      <div class="watchlist-tabs">
        <button
          v-for="list in displayWatchlists"
          :key="list.id"
          class="watchlist-tab"
          :class="{ active: displayActiveWatchlistId === list.id }"
          @click="handleSelectList(list.id)"
        >
          {{ list.name }}
          <span class="count">{{ list.stocks.length }}</span>
        </button>
        <button class="add-list-btn" @click="handleAddList">+</button>
      </div>
      <div class="actions">
        <ArtDecoButton variant="outline" size="sm" @click="handleImport">导入</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" @click="handleExport">导出</ArtDecoButton>
      </div>
    </div>

    <ArtDecoCard title="组合持仓明细" hoverable>
      <ArtDecoTable :columns="columns" :data="displayCurrentStocks">
        <template #action="{ row }">
          <ArtDecoButton variant="outline" size="sm" @click="handleRemoveStock(row)">删除</ArtDecoButton>
        </template>
      </ArtDecoTable>
    </ArtDecoCard>
    <input ref="importInput" type="file" accept="application/json" class="hidden-import" @change="handleImportFile" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { apiClient } from '@/api/apiClient'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  extractMonitoringWatchlists,
  extractMonitoringWatchlistStocks,
} from './stockManagementRouteData'
import {
  buildWatchlistExportDocument,
  createStockManagementRouteActions,
  parseWatchlistImportDocument,
} from './stockManagementRouteActions'

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
const { exec } = useArtDecoApi()
const internalWatchlists = ref<WatchlistItem[]>([])
const internalActiveWatchlistId = ref('')
const internalCurrentStocks = ref<StockRow[]>([])
const importInput = ref<HTMLInputElement | null>(null)
const routeActions = createStockManagementRouteActions({
  post: (url, data) => apiClient.post(url, data),
  delete: (url) => apiClient.delete(url),
})

const displayWatchlists = computed(() => {
  if (props.watchlists.length > 0) {
    return props.watchlists
  }
  return internalWatchlists.value
})

const displayActiveWatchlistId = computed(() => {
  if (props.activeWatchlistId) {
    return props.activeWatchlistId
  }
  return internalActiveWatchlistId.value
})

const displayCurrentStocks = computed(() => {
  if (props.currentStocks.length > 0) {
    return props.currentStocks
  }
  return internalCurrentStocks.value
})

const numericChanges = computed(() => displayCurrentStocks.value.map((row) => {
  const value = row.change
  if (typeof value === 'number') return value
  if (typeof value === 'string') return Number(value.replace('%', ''))
  return 0
}))

const stocksCount = computed(() => displayCurrentStocks.value.length)
const upCount = computed(() => numericChanges.value.filter((v) => v > 0).length)
const downCount = computed(() => numericChanges.value.filter((v) => v < 0).length)

async function loadWatchlists() {
  const responseData = await exec(() => apiClient.get('/v1/monitoring/watchlists'), { silent: true })
  const rows = extractMonitoringWatchlists(responseData)
  internalWatchlists.value = rows as WatchlistItem[]
  if (!internalActiveWatchlistId.value && rows.length > 0) {
    internalActiveWatchlistId.value = rows[0].id
  }
}

async function loadCurrentStocks() {
  if (props.currentStocks.length > 0) {
    return
  }
  const watchlistId = displayActiveWatchlistId.value
  if (!watchlistId) {
    internalCurrentStocks.value = []
    return
  }

  const responseData = await exec(() => apiClient.get(`/v1/monitoring/watchlists/${watchlistId}/stocks`), { silent: true })
  internalCurrentStocks.value = extractMonitoringWatchlistStocks(responseData) as StockRow[]
}

function handleSelectList(watchlistId: string) {
  emit('select-list', watchlistId)
  if (!props.activeWatchlistId) {
    internalActiveWatchlistId.value = watchlistId
    void loadCurrentStocks()
  }
}

async function handleAddList() {
  emit('add-list')
  if (props.watchlists.length > 0) {
    return
  }

  const name = window.prompt('请输入清单名称')
  if (!name || !name.trim()) {
    return
  }

  await routeActions.createWatchlist(name.trim())
  await loadWatchlists()
}

async function handleRemoveStock(row: StockRow) {
  emit('remove-stock', row)
  if (props.currentStocks.length > 0) {
    return
  }

  const symbol = typeof row.symbol === 'string' ? row.symbol : ''
  const watchlistId = displayActiveWatchlistId.value
  if (!symbol || !watchlistId) {
    return
  }

  await routeActions.removeStock(watchlistId, symbol)
  await loadCurrentStocks()
  await loadWatchlists()
}

function handleExport() {
  emit('export')
  const payload = buildWatchlistExportDocument(displayWatchlists.value, displayActiveWatchlistId.value, displayCurrentStocks.value)
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'watchlists-export.json'
  anchor.click()
  URL.revokeObjectURL(url)
}

function handleImport() {
  emit('import')
  importInput.value?.click()
}

async function handleImportFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    return
  }

  const text = await file.text()
  const payload = parseWatchlistImportDocument(text)
  internalWatchlists.value = payload.watchlists as WatchlistItem[]
  internalActiveWatchlistId.value = payload.activeWatchlistId
  internalCurrentStocks.value = payload.currentStocks as StockRow[]
  input.value = ''
}

onMounted(async () => {
  if (props.watchlists.length === 0) {
    await loadWatchlists()
  }
  if (props.currentStocks.length === 0) {
    await loadCurrentStocks()
  }
})

const columns = [
  { key: 'symbol', label: '代码', width: '100px' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'change', label: '涨跌幅', variant: 'color', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'weight', label: '权重', align: 'right' },
  { key: 'action', label: '操作', width: '90px' }
]
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.watchlist-manager {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
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
  border: 1px solid var(--artdeco-border-default);
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

  width: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-2));
  padding: var(--artdeco-spacing-2) 0;
}

.actions {
  display: flex;
  gap: var(--artdeco-spacing-2);
}

.hidden-import {
  display: none;
}

@media (width <= 48rem) {
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .watchlist-header,
  .watchlist-tabs,
  .actions {
    width: 100%;
  }

  .watchlist-header,
  .watchlist-tabs,
  .actions {
    flex-wrap: wrap;
  }
}
</style>
