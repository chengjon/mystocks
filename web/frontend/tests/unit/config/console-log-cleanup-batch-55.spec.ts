import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 55', () => {
  it('removes artdeco settings placeholder logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useArtDecoSettings.ts'), 'utf8')

    expect(source).not.toContain("console.log('Saving settings:', settings.value)")
    expect(source).not.toContain("console.log('Resetting to defaults')")
  })
})
