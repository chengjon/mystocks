import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'

function readBacktestGpuStyleSource() {
  const entryPath = resolve(process.cwd(), 'src/views/strategy/styles/BacktestGPU.scss')
  const entrySource = readFileSync(entryPath, 'utf8')
  const partialSources = Array.from(entrySource.matchAll(/^@import ['"](.+)['"];$/gm)).map(([, importPath]) =>
    readFileSync(resolve(dirname(entryPath), `${importPath}.scss`), 'utf8'),
  )

  return {
    entrySource,
    source: [entrySource, ...partialSources].join('\n'),
  }
}

describe('BacktestGPU style source', () => {
  it('keeps BacktestGPU styles on ArtDeco tokens', () => {
    const { entrySource, source } = readBacktestGpuStyleSource()

    expect(entrySource).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
    expect(entrySource).toContain("@import './BacktestGPU.shell';")
    expect(entrySource).toContain("@import './BacktestGPU.status';")
    expect(entrySource).toContain("@import './BacktestGPU.performance-controls';")
    expect(entrySource).toContain("@import './BacktestGPU.logs-metrics';")
    expect(entrySource).toContain("@import './BacktestGPU.element-plus';")
    expect(entrySource).toContain("@import './BacktestGPU.responsive';")
    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-bg-card)')
    expect(source).toContain('var(--artdeco-fg-primary)')

    expect(source).not.toContain('var(--color-')
    expect(source).not.toContain('var(--spacing-')
    expect(source).not.toContain('var(--font-size-')
    expect(source).not.toContain('var(--border-radius-')
  })
})
