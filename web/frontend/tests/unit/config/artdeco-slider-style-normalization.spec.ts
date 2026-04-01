import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoSlider style normalization', () => {
  it('moves static marker positions into semantic classes', () => {
    const source = readSource('src/components/artdeco/business/ArtDecoSlider.vue')

    expect(source).toContain('class="artdeco-slider-marker marker-0"')
    expect(source).toContain('class="artdeco-slider-marker marker-5"')
    expect(source).toContain('.marker-0 {')
    expect(source).toContain('.marker-5 {')
    expect(source).toContain('left: 0%')
    expect(source).toContain('left: 100%')

    expect(source).not.toContain(":style=\"{ left: '0%' }\"")
    expect(source).not.toContain(":style=\"{ left: '20%' }\"")
    expect(source).not.toContain(":style=\"{ left: '40%' }\"")
    expect(source).not.toContain(":style=\"{ left: '60%' }\"")
    expect(source).not.toContain(":style=\"{ left: '80%' }\"")
    expect(source).not.toContain(":style=\"{ left: '100%' }\"")
    expect(source).not.toContain('artde-slider-marker')
  })
})
