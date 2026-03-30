import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 11', () => {
  it('removes SSE connection and domain event console logs while keeping helper shims explicit', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useSSE.js'), 'utf8')
    const helpers = readFileSync(resolve(process.cwd(), 'src/composables/useSSE.helpers.js'), 'utf8')

    expect(source).not.toContain("console.log('[SSE] Connecting to SSE endpoint:'")
    expect(source).not.toContain("console.log('[SSE] Connection opened')")
    expect(source).not.toContain('console.log(`[SSE] Reconnecting in ${currentReconnectDelay}ms')
    expect(source).not.toContain("console.log('[SSE] Disconnecting...')")

    expect(source).not.toContain("console.log('[Training] Progress update:'")
    expect(source).not.toContain("console.log('[Backtest] Progress update:'")
    expect(source).not.toContain("console.log('[Alerts] New risk alert:'")
    expect(source).not.toContain("console.log('[Dashboard] Metrics update:'")

    expect(helpers).toContain('export const createChannelConnectedLogger = (_channelLabel, _channelName) => (_data) => {}')
    expect(helpers).toContain('export const createKeepaliveLogger = (_channelLabel) => (_data) => {}')
  })
})
