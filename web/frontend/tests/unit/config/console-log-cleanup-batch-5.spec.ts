import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 5', () => {
  it('removes dev-only console.log calls from low-risk composables', () => {
    const files = [
      'src/composables/useToastManager.ts',
      'src/composables/usePageTitle.ts',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
