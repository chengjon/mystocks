import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('HeatmapCard legend style normalization', () => {
  it('moves static legend backgrounds into semantic classes', () => {
    const viewSource = readSource('src/components/artdeco/charts/HeatmapCard.vue')
    const styleSource = readSource('src/components/artdeco/charts/styles/HeatmapCard.scss')

    expect(viewSource).toContain('hybrid-heatmap-card__legend-color--limit-down')
    expect(viewSource).toContain('hybrid-heatmap-card__legend-color--down-range')
    expect(viewSource).toContain('hybrid-heatmap-card__legend-color--flat')
    expect(viewSource).toContain('hybrid-heatmap-card__legend-color--up-range')
    expect(viewSource).toContain('hybrid-heatmap-card__legend-color--limit-up')

    expect(viewSource).not.toContain('style="background-color: var(--artdeco-down)"')
    expect(viewSource).not.toContain('style="background: linear-gradient(to right, var(--artdeco-down), var(--artdeco-flat))"')
    expect(viewSource).not.toContain('style="background-color: var(--artdeco-flat)"')
    expect(viewSource).not.toContain('style="background: linear-gradient(to right, var(--artdeco-flat), var(--artdeco-up))"')
    expect(viewSource).not.toContain('style="background-color: var(--artdeco-up)"')

    expect(styleSource).toContain('.hybrid-heatmap-card__legend-color--limit-down')
    expect(styleSource).toContain('.hybrid-heatmap-card__legend-color--limit-up')
  })
})
