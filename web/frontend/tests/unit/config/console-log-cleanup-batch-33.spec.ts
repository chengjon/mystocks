import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 33', () => {
  it('removes smart recommendation action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/SmartRecommendation.vue'), 'utf8')

    expect(source).not.toContain("console.log('Selected stock:', stock)")
    expect(source).not.toContain("console.log('Applied strategy:', strategy)")
  })
})
