import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 66', () => {
  it('removes performance monitor network logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/performance/part-1.ts'), 'utf8')

    expect(source).not.toContain("console.log('Navigation Performance:', {")
    expect(source).not.toContain("console.log('Resource Performance:', {")
  })
})
