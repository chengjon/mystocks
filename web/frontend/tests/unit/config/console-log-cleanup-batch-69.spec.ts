import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 69', () => {
  it('removes websocket manager state and reconnect logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/webSocketManager.ts'), 'utf8')

    expect(source).not.toContain('console.log(`WebSocket state changed: ${oldState} -> ${newState}`)')
    expect(source).not.toContain('console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.reconnectAttempts})...`)')
  })
})
