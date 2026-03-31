import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('style cleanup batch 77', () => {
  it('removes static width inline styles from watchlist and trading dashboard tables', () => {
    const files = [
      'src/views/stocks/Watchlist.vue',
      'src/views/TradingDashboard.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('style="width: 100%"')
    }
  })
})
