import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useHeaderSummary } from '@/composables/useHeaderSummary'

describe('useHeaderSummary', () => {
  beforeEach(() => {
    const headerSummary = useHeaderSummary()
    headerSummary.update({
      marketStatus: '',
      activeStrategiesCount: null,
      todayPnLValue: '¥0.00',
      currentTime: '',
      refreshing: false,
    })
    headerSummary.setRefreshFn(async () => {})
  })

  it('shares a singleton summary state across consumers', () => {
    const firstConsumer = useHeaderSummary()
    const secondConsumer = useHeaderSummary()

    firstConsumer.update({
      marketStatus: '市场震荡',
      activeStrategiesCount: 3,
      todayPnLValue: '¥12.34',
      currentTime: '2026/04/19 09:30:00',
      refreshing: true,
    })

    expect(secondConsumer.marketStatus.value).toBe('市场震荡')
    expect(secondConsumer.activeStrategiesCount.value).toBe(3)
    expect(secondConsumer.todayPnLValue.value).toBe('¥12.34')
    expect(secondConsumer.currentTime.value).toBe('2026/04/19 09:30:00')
    expect(secondConsumer.refreshing.value).toBe(true)
  })

  it('delegates refresh to the latest registered refresh function', async () => {
    const headerSummary = useHeaderSummary()
    const refreshSpy = vi.fn().mockResolvedValue(undefined)

    headerSummary.setRefreshFn(refreshSpy)
    await headerSummary.refresh()

    expect(refreshSpy).toHaveBeenCalledTimes(1)
  })

  it('tracks whether a refresh action is currently available', async () => {
    const headerSummary = useHeaderSummary()

    headerSummary.reset()
    expect(headerSummary.canRefresh.value).toBe(false)

    headerSummary.setRefreshFn(async () => {})
    expect(headerSummary.canRefresh.value).toBe(true)
  })
})
