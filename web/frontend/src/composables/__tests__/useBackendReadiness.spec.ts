import { afterEach, describe, expect, it, vi } from 'vitest'

import { requestBackendReadiness, resolveReadinessEndpoint } from '@/composables/useBackendReadiness'

describe('useBackendReadiness', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('keeps the readiness probe alive long enough for a slightly slow ready response', async () => {
    vi.useFakeTimers()

    const fetchImpl = vi.fn((_: RequestInfo | URL, init?: RequestInit) => {
      const signal = init?.signal

      return new Promise<Response>((resolve, reject) => {
        const timer = setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({
              success: true,
              message: '系统就绪检查完成',
              request_id: 'req-ready',
              data: {
                status: 'ready'
              }
            })
          } as Response)
        }, 5200)

        signal?.addEventListener(
          'abort',
          () => {
            clearTimeout(timer)
            reject(new Error('signal is aborted without reason'))
          },
          { once: true }
        )
      })
    })

    const resultPromise = requestBackendReadiness(fetchImpl as typeof fetch, '/api', false)

    await vi.advanceTimersByTimeAsync(5200)
    const result = await resultPromise

    expect(resolveReadinessEndpoint('/api')).toBe('/api/health/ready')
    expect(result).toMatchObject({
      ready: true,
      backendReady: true,
      usingMockFallback: false,
      requestId: 'req-ready'
    })
  })

  it('retries once when the first readiness probe aborts but the next one succeeds', async () => {
    const fetchImpl = vi
      .fn<typeof fetch>()
      .mockRejectedValueOnce(new Error('signal is aborted without reason'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: '系统就绪检查完成',
          request_id: 'req-retry',
          data: {
            status: 'ready'
          }
        })
      } as Response)

    const result = await requestBackendReadiness(fetchImpl, '/api', false)

    expect(fetchImpl).toHaveBeenCalledTimes(2)
    expect(result).toMatchObject({
      ready: true,
      backendReady: true,
      usingMockFallback: false,
      requestId: 'req-retry'
    })
  })
})
