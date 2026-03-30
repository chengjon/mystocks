import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 53', () => {
  it('removes layout enhanced toggle logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/layouts/ArtDecoLayoutEnhanced.vue'), 'utf8')

    expect(source).not.toContain("console.log('Toggle notifications')")
    expect(source).not.toContain("console.log('Toggle user menu')")
  })
})
