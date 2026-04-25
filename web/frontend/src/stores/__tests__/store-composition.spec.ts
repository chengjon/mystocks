import { computed, ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useStoreComposition } from '@/stores/storeComposition'

describe('useStoreComposition', () => {
  it('aggregates loading, errors, and latest fetch metadata across stores', () => {
    const marketLoading = ref(true)
    const watchlistError = ref<string | null>('watchlist unavailable')
    const strategyLastFetch = computed(() => 1714032000000)

    const composition = useStoreComposition({
      market: {
        loading: marketLoading,
        error: null,
        lastFetch: 1714031000000
      },
      watchlist: {
        loading: false,
        error: watchlistError,
        lastFetch: null
      },
      strategy: {
        loading: false,
        error: '',
        lastFetch: strategyLastFetch
      }
    })

    expect(composition.isLoading.value).toBe(true)
    expect(composition.hasErrors.value).toBe(true)
    expect(composition.errors.value).toEqual([{ id: 'watchlist', message: 'watchlist unavailable' }])
    expect(composition.latestFetch.value).toBe(1714032000000)

    marketLoading.value = false
    watchlistError.value = null

    expect(composition.isLoading.value).toBe(false)
    expect(composition.hasErrors.value).toBe(false)
    expect(composition.errors.value).toEqual([])
  })

  it('refreshes each store via refresh or fetch and returns settled statuses', async () => {
    const refreshMarket = vi.fn().mockResolvedValue({ ok: true })
    const fetchStrategy = vi.fn().mockRejectedValue(new Error('strategy failed'))

    const composition = useStoreComposition({
      market: { refresh: refreshMarket },
      strategy: { fetch: fetchStrategy },
      passive: {}
    })

    const result = await composition.refreshAll()

    expect(refreshMarket).toHaveBeenCalledTimes(1)
    expect(fetchStrategy).toHaveBeenCalledTimes(1)
    expect(result).toEqual([
      { id: 'market', status: 'fulfilled' },
      { id: 'strategy', status: 'rejected', reason: expect.any(Error) },
      { id: 'passive', status: 'fulfilled' }
    ])
    expect((result[1] as { reason: Error }).reason.message).toBe('strategy failed')
  })
})
