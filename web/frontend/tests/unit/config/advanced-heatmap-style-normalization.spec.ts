import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('AdvancedHeatmap style normalization', () => {
  it('moves static color scheme selector width into a semantic class', () => {
    const viewSource = readSource('src/components/Charts/AdvancedHeatmap.vue')
    const styleSource = readSource('src/components/Charts/styles/AdvancedHeatmap.scss')

    expect(viewSource).toContain('class="heatmap-color-select"')
    expect(viewSource).not.toContain('style="width: 120px"')

    expect(styleSource).toContain('.heatmap-color-select')
    expect(styleSource).toContain('width:')
  })
})
