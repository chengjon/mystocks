import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 3', () => {
  it('removes debug console.log calls from kline composables', () => {
    const files = [
      'src/composables/useKLineData.ts',
      'src/composables/useKLineControls.ts',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
