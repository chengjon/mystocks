import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('HealthRadarChart style normalization', () => {
  it('keeps fixed chart width in CSS instead of inline bindings', () => {
    const viewSource = readSource('src/components/chart/HealthRadarChart.vue')
    const styleSource = readSource('src/components/chart/styles/HealthRadarChart.css')

    expect(viewSource).toContain('class="chart-canvas" :style="{ height: chartHeight }"')
    expect(viewSource).not.toContain("width: '100%'")

    expect(styleSource).toContain('.chart-canvas')
    expect(styleSource).toContain('width: 100%')
  })
})
