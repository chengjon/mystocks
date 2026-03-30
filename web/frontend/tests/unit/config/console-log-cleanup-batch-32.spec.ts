import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 32', () => {
  it('removes concepts view concept stocks log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/market/Concepts.vue'), 'utf8')

    expect(source).not.toContain("console.log('View concept stocks:', selectedConcept.value?.name)")
  })
})
