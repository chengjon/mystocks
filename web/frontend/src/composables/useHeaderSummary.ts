import { ref, type Ref } from 'vue'

const marketStatus = ref('')
const activeStrategiesCount: Ref<number | null> = ref(null)
const todayPnLValue = ref('¥0.00')
const currentTime = ref('')
const refreshing = ref(false)
const canRefresh = ref(false)
let _refreshFn: (() => Promise<void>) | null = null

function resetSummaryState() {
  marketStatus.value = ''
  activeStrategiesCount.value = null
  todayPnLValue.value = '¥0.00'
  currentTime.value = ''
  refreshing.value = false
  _refreshFn = null
  canRefresh.value = false
}

export function useHeaderSummary() {
  function update(data: {
    marketStatus?: string
    activeStrategiesCount?: number | null
    todayPnLValue?: string
    currentTime?: string
    refreshing?: boolean
  }) {
    if (data.marketStatus !== undefined) marketStatus.value = data.marketStatus
    if (data.activeStrategiesCount !== undefined) activeStrategiesCount.value = data.activeStrategiesCount
    if (data.todayPnLValue !== undefined) todayPnLValue.value = data.todayPnLValue
    if (data.currentTime !== undefined) currentTime.value = data.currentTime
    if (data.refreshing !== undefined) refreshing.value = data.refreshing
  }

  function setRefreshFn(fn: () => Promise<void>) {
    _refreshFn = fn
    canRefresh.value = true
  }

  async function refresh() {
    await _refreshFn?.()
  }

  function reset() {
    resetSummaryState()
  }

  return {
    marketStatus,
    activeStrategiesCount,
    todayPnLValue,
    currentTime,
    refreshing,
    canRefresh,
    update,
    setRefreshFn,
    refresh,
    reset,
  }
}
