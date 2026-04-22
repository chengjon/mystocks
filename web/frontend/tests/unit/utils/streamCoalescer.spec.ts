import { describe, expect, it, vi } from 'vitest'
import { createLatestOnlyCoalescer } from '@/utils/streamCoalescer'

describe('createLatestOnlyCoalescer', () => {
  it('emits only the latest value within the window', async () => {
    vi.useFakeTimers()
    const consumer = vi.fn()
    const coalescer = createLatestOnlyCoalescer<number>(consumer, 200)

    coalescer.push(1)
    coalescer.push(2)
    coalescer.push(3)

    await vi.advanceTimersByTimeAsync(200)

    expect(consumer).toHaveBeenCalledTimes(1)
    expect(consumer).toHaveBeenCalledWith(3)
    vi.useRealTimers()
  })

  it('flushes pending values immediately', () => {
    vi.useFakeTimers()
    const consumer = vi.fn()
    const coalescer = createLatestOnlyCoalescer<string>(consumer, 200)

    coalescer.push('latest')
    coalescer.flush()

    expect(consumer).toHaveBeenCalledWith('latest')
    vi.useRealTimers()
  })
})
