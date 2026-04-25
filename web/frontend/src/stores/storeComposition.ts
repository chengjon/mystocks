import { computed, unref } from 'vue'
import type { ComputedRef, Ref } from 'vue'

type MaybeRef<T> = T | Ref<T> | ComputedRef<T>

export interface ComposableStoreLike {
  loading?: MaybeRef<boolean>
  error?: MaybeRef<string | null>
  lastFetch?: MaybeRef<number | null>
  refresh?: () => Promise<unknown>
  fetch?: () => Promise<unknown>
}

export interface StoreCompositionResult {
  isLoading: ComputedRef<boolean>
  hasErrors: ComputedRef<boolean>
  errors: ComputedRef<Array<{ id: string; message: string }>>
  latestFetch: ComputedRef<number | null>
  refreshAll: () => Promise<Array<{ id: string; status: 'fulfilled' | 'rejected'; reason?: unknown }>>
}

function resolveValue<T>(value: MaybeRef<T> | undefined): T | undefined {
  return value === undefined ? undefined : unref(value)
}

export function useStoreComposition(stores: Record<string, ComposableStoreLike>): StoreCompositionResult {
  const entries = computed(() => Object.entries(stores))

  const isLoading = computed(() =>
    entries.value.some(([, store]) => resolveValue(store.loading) === true)
  )

  const errors = computed(() =>
    entries.value.flatMap(([id, store]) => {
      const message = resolveValue(store.error)
      return typeof message === 'string' && message.length > 0
        ? [{ id, message }]
        : []
    })
  )

  const hasErrors = computed(() => errors.value.length > 0)

  const latestFetch = computed(() => {
    const timestamps = entries.value
      .map(([, store]) => resolveValue(store.lastFetch))
      .filter((value): value is number => typeof value === 'number')

    return timestamps.length > 0 ? Math.max(...timestamps) : null
  })

  const refreshAll = async () => {
    const settled = await Promise.allSettled(
      entries.value.map(async ([, store]) => {
        if (typeof store.refresh === 'function') {
          return store.refresh()
        }
        if (typeof store.fetch === 'function') {
          return store.fetch()
        }
        return undefined
      })
    )

    return settled.map((result, index) => {
      const id = entries.value[index]?.[0] || `store-${index}`
      if (result.status === 'fulfilled') {
        return { id, status: 'fulfilled' as const }
      }
      return { id, status: 'rejected' as const, reason: result.reason }
    })
  }

  return {
    isLoading,
    hasErrors,
    errors,
    latestFetch,
    refreshAll
  }
}
