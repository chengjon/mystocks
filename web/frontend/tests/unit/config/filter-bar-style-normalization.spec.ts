import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('FilterBar style normalization', () => {
  it('moves default filter widths into semantic classes while preserving overrides', () => {
    const source = readSource('src/components/shared/ui/FilterBar.vue')

    expect(source).toContain('getFilterControlClass(filter.type)')
    expect(source).toContain('filter.width ? { width: filter.width } : undefined')
    expect(source).toContain('filter-control--input')
    expect(source).toContain('filter-control--select')
    expect(source).toContain('filter-control--date')
    expect(source).toContain('filter-control--date-range')

    expect(source).not.toContain(":style=\"{ width: filter.width || '150px' }\"")
    expect(source).not.toContain(":style=\"{ width: filter.width || '120px' }\"")
    expect(source).not.toContain(":style=\"{ width: filter.width || '260px' }\"")
  })
})
