<template>
  <div class="watchlist-manager">
    <div class="overview-grid">
      <ArtDecoStatCard label="组合数量" :value="watchlistsCountLabel" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="当前股票数" :value="stocksCountLabel" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="上涨家数" :value="upCountLabel" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="下跌家数" :value="downCountLabel" :show-change="false" variant="fall" />
    </div>

    <div class="watchlist-header">
      <div class="watchlist-tabs">
        <button
          v-for="list in displayWatchlists"
          :key="list.id"
          type="button"
          class="watchlist-tab"
          :class="{ active: displayActiveWatchlistId === list.id }"
          :aria-pressed="displayActiveWatchlistId === list.id ? 'true' : 'false'"
          @click="handleSelectList(list.id)"
        >
          {{ list.name }}
          <span class="count">{{ list.stocks.length }}</span>
        </button>
        <button type="button" class="add-list-btn" :disabled="loading" @click="handleAddList">+</button>
      </div>
      <div class="actions">
        <ArtDecoButton variant="outline" size="sm" :disabled="loading || !displayActiveWatchlistId" @click="handleAddStock">添加股票</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" :disabled="loading || !displayActiveWatchlistId" @click="handleDeleteActiveWatchlist">删除组合</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" :disabled="loading" @click="handleImport">导入</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" :disabled="loading" @click="handleExport">导出</ArtDecoButton>
      </div>
    </div>

    <div v-if="showLoadingState" class="state-panel artdeco-card" role="status" aria-live="polite">
      <p>自选列表同步中</p>
      <span>正在刷新清单和持仓明细。</span>
    </div>

    <div v-else-if="showStaleState" class="state-panel artdeco-card" role="alert">
      <p>自选列表刷新异常</p>
      <span>{{ staleMessage }}</span>
      <ArtDecoButton variant="outline" size="sm" @click="syncWatchlistState">重试刷新</ArtDecoButton>
    </div>

    <div v-else-if="showErrorState" class="state-panel artdeco-card" role="alert">
      <p>自选列表加载失败</p>
      <span>{{ error }}</span>
      <ArtDecoButton variant="outline" size="sm" @click="syncWatchlistState">重试刷新</ArtDecoButton>
    </div>

    <div v-else-if="showEmptyState" class="state-panel artdeco-card" role="status" aria-live="polite">
      <p>暂无自选组合</p>
      <span>当前还没有可展示的自选清单，可新建组合或导入文件。</span>
    </div>

    <ArtDecoCard title="组合持仓明细" hoverable>
      <ArtDecoTable :columns="columns" :data="displayCurrentStocks">
        <template #actions="{ row }">
          <ArtDecoButton variant="outline" size="sm" :disabled="loading" @click="handleRemoveStock(row)">删除</ArtDecoButton>
        </template>
      </ArtDecoTable>
    </ArtDecoCard>
    <input ref="importInput" type="file" accept="application/json" class="hidden-import" @change="handleImportFile" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'
import { createMonitoringWatchlistActions, useWatchlistsStore, useWatchlistStocksStore } from '@/stores/apiStores'
import { buildWatchlistExportDocument, parseWatchlistImportDocument } from './stockManagementRouteActions'

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
const emit = defineEmits(['select-list', 'add-list', 'delete-list', 'add-stock', 'import', 'export', 'remove-stock'])
const watchlistsStore = useWatchlistsStore()
const watchlistStocksStore = useWatchlistStocksStore()
const watchlistActions = createMonitoringWatchlistActions()
const importedWatchlists = ref<WatchlistItem[] | null>(null)
const internalActiveWatchlistId = ref('')
const importedCurrentStocks = ref<StockRow[] | null>(null)
const verifiedStocksSnapshots = ref<Record<string, StockRow[]>>({})
const importInput = ref<HTMLInputElement | null>(null)
const hasLoaded = ref(false)
const actionError = ref('')
const actionPending = ref(false)

const displayWatchlists = computed(() => {
  if (props.watchlists.length > 0) {
    return props.watchlists
  }
  if (importedWatchlists.value) {
    return importedWatchlists.value
  }
  return (watchlistsStore.data as WatchlistItem[] | null) ?? []
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
  if (importedCurrentStocks.value) {
    return importedCurrentStocks.value
  }

  const activeWatchlistId = displayActiveWatchlistId.value
  if (!activeWatchlistId) {
    return []
  }

  return verifiedStocksSnapshots.value[activeWatchlistId] ?? []
})

const loading = computed(() => watchlistsStore.loading || watchlistStocksStore.loading || actionPending.value)
const error = computed(() => actionError.value || watchlistsStore.error || watchlistStocksStore.error || '')

const numericChanges = computed(() => displayCurrentStocks.value.map((row) => {
  const value = row.change
  if (typeof value === 'number') return value
  if (typeof value === 'string') return Number(value.replace('%', ''))
  return 0
}))

const stocksCount = computed(() => displayCurrentStocks.value.length)
const upCount = computed(() => numericChanges.value.filter((v) => v > 0).length)
const downCount = computed(() => numericChanges.value.filter((v) => v < 0).length)
const hasVerifiedCurrentStocksSnapshot = computed(() => {
  if (props.currentStocks.length > 0 || importedCurrentStocks.value) {
    return true
  }

  const activeWatchlistId = displayActiveWatchlistId.value
  if (!activeWatchlistId) {
    return hasLoaded.value && !watchlistsStore.loading && !watchlistsStore.error && displayWatchlists.value.length === 0
  }

  return Object.prototype.hasOwnProperty.call(verifiedStocksSnapshots.value, activeWatchlistId)
})

const showLoadingState = computed(() =>
  loading.value && (!hasLoaded.value || (hasVerifiedWatchlistsSnapshot.value && !hasVerifiedCurrentStocksSnapshot.value))
)
const hasVerifiedCombinedSnapshot = computed(() => hasVerifiedWatchlistsSnapshot.value && hasVerifiedStocksSnapshot.value)
const showStaleState = computed(() => !loading.value && hasLoaded.value && Boolean(error.value) && hasVerifiedCombinedSnapshot.value)
const showErrorState = computed(() => !loading.value && hasLoaded.value && Boolean(error.value) && !showStaleState.value)
const showEmptyState = computed(() => !loading.value && hasLoaded.value && !error.value && displayWatchlists.value.length === 0)
const staleMessage = computed(() => `${error.value}，当前仍显示上次成功同步的自选组合快照。`)

const hasVerifiedWatchlistsSnapshot = computed(() => {
  if (props.watchlists.length > 0 || importedWatchlists.value || displayWatchlists.value.length > 0) {
    return true
  }

  return hasLoaded.value && !watchlistsStore.loading && !watchlistsStore.error
})

const hasVerifiedStocksSnapshot = computed(() => hasVerifiedCurrentStocksSnapshot.value)

const watchlistsCountLabel = computed(() => (hasVerifiedWatchlistsSnapshot.value ? `${displayWatchlists.value.length}` : '--'))
const stocksCountLabel = computed(() => (hasVerifiedStocksSnapshot.value ? `${stocksCount.value}` : '--'))
const upCountLabel = computed(() => (hasVerifiedStocksSnapshot.value ? `${upCount.value}` : '--'))
const downCountLabel = computed(() => (hasVerifiedStocksSnapshot.value ? `${downCount.value}` : '--'))

async function loadWatchlists() {
  await watchlistsStore.refresh()
  const rows = (watchlistsStore.data as WatchlistItem[] | null) ?? []
  if (!internalActiveWatchlistId.value && rows.length > 0) {
    internalActiveWatchlistId.value = rows[0].id
  }
}

async function loadCurrentStocks(
  watchlistIdOverride = displayActiveWatchlistId.value,
  rollbackWatchlistId = '',
) {
  if (props.currentStocks.length > 0) {
    return
  }
  const watchlistId = watchlistIdOverride
  if (!watchlistId) {
    watchlistStocksStore.clear()
    return
  }

  try {
    await watchlistStocksStore.refresh({ watchlistId })
    verifiedStocksSnapshots.value = {
      ...verifiedStocksSnapshots.value,
      [watchlistId]: [...(((watchlistStocksStore.data as StockRow[] | null) ?? []))],
    }
  } catch (err) {
    if (!props.activeWatchlistId && rollbackWatchlistId) {
      internalActiveWatchlistId.value = rollbackWatchlistId
    }
    throw err
  }
}

async function refreshWatchlistState() {
  actionError.value = ''
  importedWatchlists.value = null
  importedCurrentStocks.value = null
  try {
    await loadWatchlists()
    await loadCurrentStocks()
  } finally {
    hasLoaded.value = true
  }
}

async function syncWatchlistState() {
  try {
    await refreshWatchlistState()
  } catch {
    // Store-backed error state already drives the failure surface.
  }
}

async function handleSelectList(watchlistId: string) {
  emit('select-list', watchlistId)
  if (!props.activeWatchlistId) {
    const previousActiveWatchlistId = internalActiveWatchlistId.value
    actionError.value = ''
    internalActiveWatchlistId.value = watchlistId
    importedCurrentStocks.value = null
    try {
      await loadCurrentStocks(watchlistId, previousActiveWatchlistId)
    } catch (err) {
      actionError.value = err instanceof Error ? err.message : '自选组合持仓刷新失败'
    }
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

  actionPending.value = true
  actionError.value = ''
  try {
    await watchlistActions.createWatchlist(name.trim())
    await refreshWatchlistState()
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : '创建自选清单失败'
  } finally {
    actionPending.value = false
  }
}

async function handleDeleteActiveWatchlist() {
  const watchlistId = displayActiveWatchlistId.value
  if (!watchlistId) {
    return
  }

  emit('delete-list', watchlistId)
  if (props.watchlists.length > 0) {
    return
  }

  if (!window.confirm('确认删除当前自选组合？')) {
    return
  }

  actionPending.value = true
  actionError.value = ''
  try {
    await watchlistActions.deleteWatchlist(watchlistId)
    internalActiveWatchlistId.value = ''
    verifiedStocksSnapshots.value = {}
    await refreshWatchlistState()
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : '删除自选组合失败'
  } finally {
    actionPending.value = false
  }
}

async function handleAddStock() {
  const watchlistId = displayActiveWatchlistId.value
  if (!watchlistId) {
    return
  }

  const rawSymbol = window.prompt('请输入股票代码')
  const symbol = rawSymbol?.trim()
  if (!symbol) {
    return
  }

  emit('add-stock', { watchlistId, symbol })
  if (props.currentStocks.length > 0) {
    return
  }

  actionPending.value = true
  actionError.value = ''
  try {
    await watchlistActions.addStock(watchlistId, symbol)
    await refreshWatchlistState()
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : '添加自选股失败'
  } finally {
    actionPending.value = false
  }
}

async function handleRemoveStock(row: unknown) {
  if (!row || typeof row !== 'object') {
    return
  }

  const stockRow = row as StockRow
  emit('remove-stock', stockRow)
  if (props.currentStocks.length > 0) {
    return
  }

  const symbol = typeof stockRow.symbol === 'string' ? stockRow.symbol : ''
  const watchlistId = displayActiveWatchlistId.value
  if (!symbol || !watchlistId) {
    return
  }

  actionPending.value = true
  actionError.value = ''
  try {
    await watchlistActions.removeStock(watchlistId, symbol)
    await refreshWatchlistState()
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : '移除自选股失败'
  } finally {
    actionPending.value = false
  }
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
  importedWatchlists.value = payload.watchlists as WatchlistItem[]
  internalActiveWatchlistId.value = payload.activeWatchlistId
  importedCurrentStocks.value = payload.currentStocks as StockRow[]
  input.value = ''
  hasLoaded.value = true
}

onMounted(async () => {
  await syncWatchlistState()
})

const columns = [
  { key: 'symbol', label: '代码', width: '100px' },
  { key: 'name', label: '名称' },
  { key: 'price', label: '现价', align: 'right' },
  { key: 'change', label: '涨跌幅', align: 'right' },
  { key: 'volume', label: '成交量', align: 'right' },
  { key: 'weight', label: '权重', align: 'right' }
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

.state-panel {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(145deg, var(--artdeco-gold-opacity-05), transparent 65%);
}

.state-panel p {
  margin: 0;
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-display);
}

.state-panel span {
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

</style>
