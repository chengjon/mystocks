import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('system style sources', () => {
  it('keeps Architecture and DatabaseMonitor on ArtDeco bridge variables', () => {
    const files = [
      'src/views/system/styles/Architecture.scss',
      'src/views/system/styles/DatabaseMonitor.scss',
    ]

    for (const file of files) {
      const source = readSource(file)
      expect(source).toContain("@use '../../../styles/artdeco-tokens.scss' as *;")
      expect(source).toContain('--gold-primary: var(--artdeco-gold-primary);')
      expect(source).toContain('--bg-primary: var(--artdeco-bg-global);')
      expect(source).toContain('--text-primary: var(--artdeco-fg-primary);')
    }
  })

  it('keeps PerformanceMonitor layout metrics on ArtDeco token expressions', () => {
    const source = readSource('src/views/system/styles/PerformanceMonitor.css')
    expect(source).toContain('calc((var(--artdeco-spacing-20) * 3) + var(--artdeco-spacing-16))')
    expect(source).toContain('color-mix(in srgb, var(--artdeco-down) 10%, var(--artdeco-bg-card))')
    expect(source).toContain('@media (width <= 64rem)')
    expect(source).toContain('@media (width <= 48rem)')
    expect(source).not.toContain('rgb(0 230 118 / 10%)')
    expect(source).not.toContain('rgb(255 193 7 / 10%)')
    expect(source).not.toContain('rgb(255 82 82 / 10%)')
  })
})
