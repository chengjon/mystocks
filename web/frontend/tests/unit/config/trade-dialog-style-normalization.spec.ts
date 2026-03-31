import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TradeDialog style normalization', () => {
  it('relies on the existing input-number width rule instead of inline widths', () => {
    const viewSource = readSource('src/views/trade-management/components/TradeDialog.vue')

    expect(viewSource).not.toContain('style="width: 100%"')
    expect(viewSource).toContain(':deep(.el-input-number) {')
    expect(viewSource).toContain('width: 100%;')
  })
})
