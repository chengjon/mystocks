import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoChart accessibility contract', () => {
  it('supports an accessible chart description wired through aria-describedby', () => {
    const source = readSource('src/components/artdeco/charts/ArtDecoChart.vue')

    expect(source).toContain('accessibleDescription')
    expect(source).toContain(':aria-describedby="chartAriaDescribedBy"')
    expect(source).toContain('resolvedAccessibleDescription')
    expect(source).toContain('getOptionDescription(props.option)')
    expect(source).toContain('chart-sr-description')
    expect(source).toContain('resolvedAccessibleDescription.value ? descriptionId : undefined')
  })
})
