import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ApiVersionManager style normalization', () => {
  it('moves compatibility table width into a semantic class', () => {
    const source = readSource('src/components/common/ApiVersionManager.vue')

    expect(source).toContain('class="compatibility-table"')
    expect(source).toContain('.compatibility-table {')
    expect(source).not.toContain('style="width: 100%"')
  })
})
