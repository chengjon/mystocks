import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 60', () => {
  it('removes artdeco date range dayjs import log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/artdeco/business/ArtDecoDateRange.vue'), 'utf8')

    expect(source).not.toContain("console.log('dayjs imported in ArtDecoDateRange')")
  })
})
