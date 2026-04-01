import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('BacktestGPU color source', () => {
  it('keeps gpu progress colors on ArtDeco token variables', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/strategy/composables/useBacktestGPU.ts'),
      'utf8',
    )

    expect(source).toContain("return 'var(--artdeco-rise)'")
    expect(source).toContain("return 'var(--artdeco-warning)'")
    expect(source).toContain("return 'var(--artdeco-down)'")

    expect(source).not.toContain("return '#67C23A'")
    expect(source).not.toContain("return '#E6A23C'")
    expect(source).not.toContain("return '#F56C6C'")
  })
})
