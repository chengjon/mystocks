import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('RelationChart style normalization', () => {
  it('moves default legend color into a semantic class while keeping explicit overrides dynamic', () => {
    const viewSource = readSource('src/components/Charts/RelationChart.vue')
    const styleSource = readSource('src/components/Charts/styles/RelationChart.scss')

    expect(viewSource).toContain("'legend-color--default'")
    expect(viewSource).toContain("category.itemStyle?.color ? { backgroundColor: category.itemStyle.color } : undefined")
    expect(viewSource).not.toContain(":style=\"{ backgroundColor: category.itemStyle?.color || '#5470c6' }\"")

    expect(styleSource).toContain('&--default')
    expect(styleSource).toContain('background: var(--artdeco-info)')
  })
})
