import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoMarketData style normalization', () => {
  it('moves repeated card top spacing into a semantic class', () => {
    const source = readSource('src/views/artdeco-pages/ArtDecoMarketData.vue')

    expect(source).toContain('class="tab-card-offset"')
    expect(source).toContain('.tab-card-offset {')
    expect(source).toContain('margin-top: var(--artdeco-spacing-6);')

    expect(source).not.toContain('style="margin-top: 24px;"')
  })
})
