import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('chart style sources', () => {
  it('keeps chart style files on ArtDeco token variables', () => {
    const files = [
      'src/components/Charts/styles/AdvancedHeatmap.scss',
      'src/components/Charts/styles/ProKLineChart.css',
      'src/components/Charts/styles/RelationChart.scss',
      'src/components/chart/styles/HealthRadarChart.css',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain('artdeco')
      expect(source).not.toContain('#333')
      expect(source).not.toContain('#e0e0e0')
      expect(source).not.toContain('rgb(255 255 255 / 80%)')
    }
  })
})
