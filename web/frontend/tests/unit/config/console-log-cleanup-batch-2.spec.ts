import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 2', () => {
  it('removes production console.log calls from shared stores and stocks page', () => {
    const files = [
      'src/stores/baseStore.ts',
      'src/stores/marketData.ts',
      'src/views/Stocks.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
