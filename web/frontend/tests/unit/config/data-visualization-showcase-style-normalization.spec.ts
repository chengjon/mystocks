import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('DataVisualizationShowcase style normalization', () => {
  it('moves traditional chart container heights into semantic classes', () => {
    const viewSource = readSource('src/views/DataVisualizationShowcase.vue')
    const styleSource = readSource('src/views/styles/DataVisualizationShowcase.scss')

    expect(viewSource).toContain('class="traditional-chart-canvas"')
    expect(viewSource).not.toContain('style="height: 300px"')

    expect(styleSource).toContain('.traditional-chart-canvas')
    expect(styleSource).toContain('height:')
  })
})
