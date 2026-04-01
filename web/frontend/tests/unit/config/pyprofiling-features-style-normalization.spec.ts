import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Pyprofiling Features style normalization', () => {
  it('moves static section spacing into semantic classes', () => {
    const source = readSource('src/views/demo/pyprofiling/components/Features.vue')

    expect(source).toContain('class="info-grid features-grid-offset"')
    expect(source).toContain('class="features-section-heading"')
    expect(source).toContain('class="table features-table-offset"')
    expect(source).toContain('.features-grid-offset')
    expect(source).toContain('.features-section-heading')
    expect(source).toContain('.features-table-offset')

    expect(source).not.toContain('style="margin-top: 15px"')
    expect(source).not.toContain('style="margin-top: 30px"')
  })
})
