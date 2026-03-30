import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 18', () => {
  it('removes intelligent data source adapter debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/services/intelligentDataSourceAdapter.js'), 'utf8')

    expect(source).not.toContain('console.log(')
    expect(source).not.toContain('console.debug(')
  })
})
