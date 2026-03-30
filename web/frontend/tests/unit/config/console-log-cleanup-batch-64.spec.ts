import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 64', () => {
  it('removes mock api client request debug log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/mockApiClient.ts'), 'utf8')

    expect(source).not.toContain('console.log(`[Mock API] GET ${url}`, config);')
  })
})
