import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('chart component style normalization', () => {
  it('keeps chart component styles on the artdeco token namespace', () => {
    const files = [
      'src/components/charts/IndicatorSelector.vue',
      'src/components/charts/OscillatorChart.vue',
      'src/components/charts/SankeyChart.vue',
      'src/components/charts/TreeChart.vue',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain('artdeco')
      expect(source).not.toContain('var(--art-deco-')
    }
  })
})
