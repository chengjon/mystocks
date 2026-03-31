import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 75', () => {
  it('removes console log examples from websocket and page config docs', () => {
    const files = [
      'src/composables/useWebSocketEnhanced.ts',
      'src/composables/useWebSocketWithConfig.ts',
      'src/config/pageConfigExtended.example.ts',
      'src/services/api/marketService.ts',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
