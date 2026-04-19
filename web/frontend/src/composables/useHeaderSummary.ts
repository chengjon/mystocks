import { ref, type Ref } from 'vue'

const marketStatus = ref('')
const activeStrategiesCount: Ref<number | null> = ref(null)
const todayPnLValue = ref('¥0.00')
const currentTime = ref('')
const refreshing = ref(false)
let _refreshFn: (() => Promise<void>) | null = null

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
  }

  async function refresh() {
    await _refreshFn?.()
  }

  return {
    marketStatus,
    activeStrategiesCount,
    todayPnLValue,
    currentTime,
    refreshing,
    update,
    setRefreshFn,
    refresh,
  }
}
