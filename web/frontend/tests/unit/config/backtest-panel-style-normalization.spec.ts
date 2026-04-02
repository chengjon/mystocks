import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('BacktestPanel style normalization', () => {
  it('uses theme variables for result card neutral palette', () => {
    const source = readSource('src/components/BacktestPanel.vue')

    expect(source).toContain('background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);')
    expect(source).toContain('border: 1px solid var(--color-border-light);')
    expect(source).toContain('color: var(--color-text-tertiary);')
    expect(source).toContain('color: var(--color-text-primary);')
    expect(source).toContain('border-top: 1px solid var(--color-border-light);')

    expect(source).not.toContain('.metric-card {\n  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);')
    expect(source).not.toContain('.metric-card {\n  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);\n  border-radius: 8px;\n  padding: 16px;\n  text-align: center;\n  border: 1px solid #e5e7eb;')
    expect(source).not.toContain('.metric-card .label {\n  display: block;\n  font-size: 12px;\n  color: #737373;')
    expect(source).not.toContain('.metric-card .value {\n  display: block;\n  font-size: 20px;\n  font-weight: 700;\n  color: #262626;')
    expect(source).not.toContain('.modal-footer {\n  display: flex;\n  justify-content: flex-end;\n  gap: 12px;\n  padding: 16px 24px;\n  border-top: 1px solid #e5e7eb;')
  })
})
