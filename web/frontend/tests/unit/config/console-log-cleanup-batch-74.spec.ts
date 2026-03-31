import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 74', () => {
  it('removes type validator success path logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/types/tools/validators/TypeValidator.ts'), 'utf8')

    expect(source).not.toContain("console.log('🔍 Running TypeScript type validation...\\n');")
    expect(source).not.toContain("console.log('✅ Type validation passed!');")
    expect(source).not.toContain('console.log(`📊 Stats: ${result.stats.totalTypes} total types (${result.stats.coverage.toFixed(1)}% coverage)`);')
  })
})
