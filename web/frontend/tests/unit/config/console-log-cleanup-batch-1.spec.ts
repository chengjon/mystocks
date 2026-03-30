import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('console log cleanup batch 1', () => {
  it('removes production console.log calls from monitoring and market quote pages', () => {
    const files = [
      'src/views/monitoring/MonitoringDashboard.vue',
      'src/views/artdeco-pages/ArtDecoMarketQuotes.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).not.toContain('console.log(')
    }
  })
})
