export interface StreamCoalescer<T> {
  push: (value: T) => void
  flush: () => void
  cancel: () => void
}

export function createLatestOnlyCoalescer<T>(
  consumer: (value: T) => void,
  windowMs = 200
): StreamCoalescer<T> {
  let latestValue: T | null = null
  let timerId: number | null = null

  const flush = () => {
    if (timerId !== null) {
      window.clearTimeout(timerId)
      timerId = null
    }

    if (latestValue !== null) {
      const value = latestValue
      latestValue = null
      consumer(value)
    }
  }

  const push = (value: T) => {
    latestValue = value

    if (windowMs <= 0) {
      flush()
      return
    }

    if (timerId !== null) {
      return
    }

    timerId = window.setTimeout(() => {
      flush()
    }, windowMs)
  }

  const cancel = () => {
    if (timerId !== null) {
      window.clearTimeout(timerId)
      timerId = null
    }
    latestValue = null
  }

  return {
    push,
    flush,
    cancel,
  }
}
