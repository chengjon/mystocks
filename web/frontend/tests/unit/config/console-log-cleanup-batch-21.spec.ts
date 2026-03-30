import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 21', () => {
  it('removes strategy service endpoint selection logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/services/strategyService.ts'), 'utf8')

    expect(source).not.toContain("console.log('[Strategy API] Using Mock endpoint:'")
    expect(source).not.toContain("console.log('[Strategy API] Using Real endpoint:'")
  })
})
