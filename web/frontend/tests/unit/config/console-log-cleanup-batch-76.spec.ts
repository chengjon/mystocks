import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 76', () => {
  it('removes live data manager commented debug line', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useLiveDataManager.ts'), 'utf8')

    expect(source).not.toContain('console.debug(`[LiveDataManager] Update for ${menu.path}:`, data)')
  })
})
