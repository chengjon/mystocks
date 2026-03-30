import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 15', () => {
  it('removes menu service websocket debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/services/menuService.ts'), 'utf8')

    expect(source).not.toContain("console.log('[WebSocket] Connected')")
    expect(source).not.toContain("console.log('[WebSocket] Disconnected')")
  })
})
