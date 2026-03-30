import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 14', () => {
  it('removes basic websocket connection debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useWebSocket.ts'), 'utf8')

    expect(source).not.toContain("console.log('WebSocket connected')")
    expect(source).not.toContain("console.log('WebSocket disconnected')")
  })
})
