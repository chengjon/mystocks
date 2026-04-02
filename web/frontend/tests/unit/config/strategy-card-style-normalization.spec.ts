import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StrategyCard style normalization', () => {
  it('moves strategy card neutral palette onto theme variables', () => {
    const source = readSource('src/components/StrategyCard.vue')

    expect(source).toContain('linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-elevated) 100%)')
    expect(source).toContain('border: 1px solid var(--color-border-light);')
    expect(source).toContain('background: var(--color-bg-primary);')
    expect(source).toContain('color: var(--color-text-primary);')
    expect(source).toContain('color: var(--color-text-tertiary);')
    expect(source).toContain('background-color: var(--color-bg-secondary);')

    expect(source).not.toContain('linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%)')
    expect(source).not.toContain('.strategy-card {\n  border: 1px solid #e8e8e8;')
    expect(source).not.toContain('.strategy-card {\n  border: 1px solid var(--color-border-light);\n  border-radius: 8px;\n  padding: 16px;\n  background: white;')
    expect(source).not.toContain('.strategy-name {\n  margin: 0;\n  font-size: 18px;\n  font-weight: 600;\n  color: #262626;')
    expect(source).not.toContain('.description {\n  color: #737373;')
    expect(source).not.toContain('.meta {\n  display: flex;\n  gap: 8px;\n  margin-bottom: 12px;\n  font-size: 12px;\n  color: #737373;')
    expect(source).not.toContain('.type-badge {\n  padding: 2px 8px;\n  background-color: #f0f0f0;')
    expect(source).not.toContain('.metric .label {\n  font-size: 11px;\n  color: #737373;')
    expect(source).not.toContain('.metric .value {\n  font-size: 16px;\n  font-weight: 600;\n  color: #262626;')
  })
})
