import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('OpenStock Heatmap tooltip style normalization', () => {
  it('moves tooltip presentation styles into dedicated classes', () => {
    const source = readSource('src/views/demo/openstock/components/HeatmapChart.vue')

    expect(source).toContain('openstock-heatmap-tooltip__title')
    expect(source).toContain('openstock-heatmap-tooltip__change--up')
    expect(source).toContain('openstock-heatmap-tooltip__change--down')

    expect(source).not.toContain('<div style="font-weight: bold; margin-bottom: 5px;">')
    expect(source).not.toContain('style="color: ${data.value && data.value >= 0 ?')
  })
})
