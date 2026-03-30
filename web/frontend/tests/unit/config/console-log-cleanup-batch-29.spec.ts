import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 29', () => {
  it('removes analysis export placeholder logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/composables/useAnalysis.ts'), 'utf8')

    expect(source).not.toContain("console.log('Exporting to PDF...')")
    expect(source).not.toContain("console.log('Exporting to Excel...')")
    expect(source).not.toContain("console.log('Exporting to JSON...')")
  })
})
