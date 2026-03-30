import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 7', () => {
  it('removes debug console.log calls from session and live-data helpers', () => {
    const files = [
      'src/composables/useLiveDataManager.ts',
      'src/utils/sessionRestore.js',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
