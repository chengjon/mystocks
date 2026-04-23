import { describe, expect, it } from 'vitest'

import { resolveRuntimeApiBase } from '../runtime-endpoints'

const loopbackBrowser = {
  protocol: 'http:',
  host: '127.0.0.1:3020',
  hostname: '127.0.0.1',
  origin: 'http://127.0.0.1:3020',
} as const

describe('resolveRuntimeApiBase', () => {
  it('falls back to proxy base in dev when env points to a different local origin', () => {
    expect(resolveRuntimeApiBase('http://localhost:8020', loopbackBrowser, true)).toBe('/api')
  })

  it('keeps absolute backend host outside local dev proxy scenarios', () => {
    expect(resolveRuntimeApiBase('https://api.mystocks.test', loopbackBrowser, true)).toBe('https://api.mystocks.test')
    expect(resolveRuntimeApiBase('http://localhost:8020', undefined, false)).toBe('http://localhost:8020')
  })
})
