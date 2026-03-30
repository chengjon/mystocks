import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 16', () => {
  it('removes smart data debug logs from service and indicator component', () => {
    const files = [
      'src/services/smartDataService.js',
      'src/components/common/SmartDataIndicator.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
      expect(source).not.toContain('console.debug(')
    }
  })
})
