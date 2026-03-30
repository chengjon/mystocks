import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 43', () => {
  it('removes trading decision center unknown action log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/TradingDecisionCenter.vue'), 'utf8')

    expect(source).not.toContain("console.log('Unknown action:', action)")
  })
})
