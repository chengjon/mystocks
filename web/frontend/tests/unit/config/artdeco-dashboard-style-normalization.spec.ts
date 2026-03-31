import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoDashboard style normalization', () => {
  it('moves static skeleton spacing and heatmap heights into semantic classes', () => {
    const viewSource = readSource('src/views/artdeco-pages/ArtDecoDashboard.vue')
    const styleSource = readSource('src/views/artdeco-pages/styles/ArtDecoDashboard.scss')

    expect(viewSource).toContain('class="dashboard-skeleton-offset"')
    expect(viewSource).toContain('class="heatmap-section dashboard-heatmap-panel"')
    expect(viewSource).toContain('class="skeleton-chart dashboard-skeleton-chart"')

    expect(viewSource).not.toContain('style="margin-top: 10px;"')
    expect(viewSource).not.toContain('style="height: 300px;"')
    expect(viewSource).not.toContain('style="height: 100%; display: flex; align-items: center; justify-content: center;"')

    expect(styleSource).toContain('.dashboard-skeleton-offset')
    expect(styleSource).toContain('.dashboard-heatmap-panel')
    expect(styleSource).toContain('.dashboard-skeleton-chart')
  })
})
