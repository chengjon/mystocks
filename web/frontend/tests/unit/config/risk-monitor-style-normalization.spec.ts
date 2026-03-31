import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('RiskMonitor style normalization', () => {
  it('moves repeated section spacing, table width, and alert spacing into classes', () => {
    const source = readSource('src/views/RiskMonitor.vue')

    expect(source).toContain('class="section-gap-large"')
    expect(source).toContain('class="full-width-table"')
    expect(source).toContain('class="risk-alert-item"')
    expect(source).toContain('class="chart-placeholder"')

    expect(source).toContain('.section-gap-large {')
    expect(source).toContain('.full-width-table {')
    expect(source).toContain('.risk-alert-item {')
    expect(source).toContain('.chart-placeholder {')

    expect(source).not.toContain('style="margin-top: 30px;"')
    expect(source).not.toContain('style="width: 100%"')
    expect(source).not.toContain('style="margin-bottom: 10px;"')
    expect(source).not.toContain('style="text-align: center; padding: 40px; color: #666;"')
  })
})
