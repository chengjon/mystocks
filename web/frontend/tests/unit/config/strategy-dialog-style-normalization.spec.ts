import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StrategyDialog style normalization', () => {
  it('uses theme variables for modal shell neutral colors', () => {
    const source = readSource('src/components/StrategyDialog.vue')

    expect(source).toContain('background: var(--color-bg-primary);')
    expect(source).toContain('border-bottom: 1px solid var(--color-border-light);')
    expect(source).toContain('color: var(--color-text-primary);')
    expect(source).toContain('color: var(--color-text-tertiary);')
    expect(source).toContain('background-color: var(--color-bg-secondary);')

    expect(source).not.toContain('background: white;')
    expect(source).not.toContain('border-bottom: 1px solid #e5e7eb;')
    expect(source).not.toContain('color: #262626;')
    expect(source).not.toContain('color: #737373;')
    expect(source).not.toContain('.btn-close:hover {\n  background-color: #f3f4f6;\n}')
  })
})
