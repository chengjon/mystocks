import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('data adapter source hygiene', () => {
  it('does not keep stale placeholder type comments or unused compatibility aliases', () => {
    const source = readSource('src/utils/adapters.ts')

    expect(source).not.toContain('Temporary: Use any for missing generated types')
    expect(source).not.toContain('TODO: Fix type generation to include these types')
    expect(source).not.toContain('type _IndexData = Record<string, unknown>')
    expect(source).not.toContain('type _SectorData = Record<string, unknown>')
    expect(source).not.toContain('type _KLinePoint = Record<string, unknown>')
  })
})
