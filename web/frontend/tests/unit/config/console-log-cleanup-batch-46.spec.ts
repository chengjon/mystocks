import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 46', () => {
  it('removes wencai panel simple request debug logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/market/WencaiPanelSimple.vue'), 'utf8')

    expect(source).not.toContain("console.log('API endpoint:', API_ENDPOINTS.wencai.queries)")
    expect(source).not.toContain("console.log('Response status:', response.status)")
    expect(source).not.toContain("console.log('Response data:', data)")
  })
})
