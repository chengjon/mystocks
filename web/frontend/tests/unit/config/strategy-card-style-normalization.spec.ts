import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('StrategyCard style normalization', () => {
  it('moves performance panel gradient onto theme variables', () => {
    const source = readSource('src/components/StrategyCard.vue')

    expect(source).toContain('linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-elevated) 100%)')
    expect(source).not.toContain('linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%)')
  })
})
