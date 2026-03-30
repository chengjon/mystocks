import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 47', () => {
  it('removes wencai panel v2 request debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/composables/useWencaiPanelV2.ts'), 'utf8')

    expect(source).not.toContain("console.log('executeQuery called with:', queryData)")
    expect(source).not.toContain("console.log('Calling API with query_name:', queryData.query_name)")
    expect(source).not.toContain("console.log('Response status:', response.status)")
    expect(source).not.toContain("console.log('Query response:', data)")
  })
})
