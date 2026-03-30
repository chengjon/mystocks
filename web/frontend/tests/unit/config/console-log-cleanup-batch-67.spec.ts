import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 67', () => {
  it('removes performance part 2 debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/utils/performance/part-2.ts'), 'utf8')

    expect(source).not.toContain('console.log(`${name} took ${end - start}ms`)')
    expect(source).not.toContain("console.log('Performance Metrics:', metrics)")
  })
})
