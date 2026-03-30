import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 13', () => {
  it('removes remaining SSE event console.log calls', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useSSE.js'), 'utf8')

    expect(source).not.toContain("console.log('[Training] Progress update:'")
    expect(source).not.toContain("console.log('[Backtest] Progress update:'")
    expect(source).not.toContain("console.log('[Alerts] New risk alert:'")
    expect(source).not.toContain("console.log('[Dashboard] Metrics update:'")
  })
})
