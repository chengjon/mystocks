import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 31', () => {
  it('removes strategy management stub action logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/StrategyManagement.vue'), 'utf8')

    expect(source).not.toContain("console.log('View:', strategy)")
    expect(source).not.toContain("console.log('Start:', strategy)")
    expect(source).not.toContain("console.log('Stop:', strategy)")
  })
})
