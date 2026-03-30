import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 27', () => {
  it('removes capital flow event handler logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/market/CapitalFlow.vue'), 'utf8')

    expect(source).not.toContain("console.log('Fund flow data loaded:', data)")
    expect(source).not.toContain("console.log('Fund flow refresh requested')")
  })
})
