import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 71', () => {
  it('removes websocket helper connection chatter logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/websocket-manager.ts'), 'utf8')

    expect(source).not.toContain("console.log('✅ WebSocket connected')")
    expect(source).not.toContain("console.log('❌ WebSocket disconnected:', event.code, event.reason)")
    expect(source).not.toContain('console.log(')
    expect(source).not.toContain('`🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}, delay: ${delay}ms)`')
  })
})
