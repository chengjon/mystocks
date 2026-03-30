import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 11', () => {
  it('removes generic SSE connection debug logs while keeping domain event handlers intact', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useSSE.js'), 'utf8')

    expect(source).not.toContain("console.log('[SSE] Connecting to SSE endpoint:'")
    expect(source).not.toContain("console.log('[SSE] Connection opened')")
    expect(source).not.toContain('console.log(`[SSE] Reconnecting in ${currentReconnectDelay}ms')
    expect(source).not.toContain("console.log('[SSE] Disconnecting...')")

    expect(source).toContain("console.log('[Training] Progress update:'")
    expect(source).toContain("console.log('[Backtest] Progress update:'")
    expect(source).toContain("console.log('[Alerts] New risk alert:'")
    expect(source).toContain("console.log('[Dashboard] Metrics update:'")
  })
})
