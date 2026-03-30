import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 70', () => {
  it('removes websocket manager subscription and reconnect chatter logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/websocket-manager.ts'), 'utf8')

    expect(source).not.toContain('console.log(`📝 Subscribed to "${messageType}" (total: ${subscribers.size})`)')
    expect(source).not.toContain('console.log(`🗑️  Cleaned up "${messageType}" (no more subscribers)`)')
    expect(source).not.toContain('console.log(`📝 Unsubscribed from "${messageType}" (remaining: ${handlers.size})`)')
    expect(source).not.toContain("console.log('🔌 Closing WebSocket connection...')")
    expect(source).not.toContain("console.log('🔄 Force reconnecting...')")
  })
})
