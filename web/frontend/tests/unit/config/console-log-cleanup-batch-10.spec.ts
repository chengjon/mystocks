import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 10', () => {
  it('removes runtime websocket debug console.log calls', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useWebSocketEnhanced.ts'), 'utf8')

    expect(source).not.toContain("console.log('[WebSocket] Already connected')")
    expect(source).not.toContain("console.log('[WebSocket] Connected to', url)")
    expect(source).not.toContain("console.log('[WebSocket] Disconnected')")
    expect(source).not.toContain('console.log(`[WebSocket] Scheduling reconnect in ${delay}ms')
    expect(source).not.toContain('console.log(`[WebSocket] Subscribed to channel: ${channel}`)')
    expect(source).not.toContain('console.log(`[WebSocket] Unsubscribed from channel: ${channel}`)')
  })
})
