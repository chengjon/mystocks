import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoSidebar style normalization', () => {
  it('moves staggered animation delays into semantic classes', () => {
    const viewSource = readSource('src/components/artdeco/trading/ArtDecoSidebar.vue')
    const styleSource = readSource('src/components/artdeco/trading/styles/ArtDecoSidebar.scss')

    expect(viewSource).toContain('artdeco-nav-section-delay-1')
    expect(viewSource).toContain('artdeco-nav-section-delay-2')
    expect(viewSource).toContain('artdeco-nav-section-delay-3')
    expect(viewSource).toContain('artdeco-nav-section-delay-4')

    expect(viewSource).not.toContain('style="animation-delay: 0.1s"')
    expect(viewSource).not.toContain('style="animation-delay: 0.2s"')
    expect(viewSource).not.toContain('style="animation-delay: 0.3s"')
    expect(viewSource).not.toContain('style="animation-delay: 0.4s"')

    expect(styleSource).toContain('.artdeco-nav-section-delay-1')
    expect(styleSource).toContain('.artdeco-nav-section-delay-4')
  })
})
