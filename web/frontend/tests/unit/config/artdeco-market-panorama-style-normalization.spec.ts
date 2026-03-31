import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoMarketPanorama style normalization', () => {
  it('moves the static activity fill width into a semantic class', () => {
    const source = readSource('src/components/artdeco/advanced/ArtDecoMarketPanorama.vue')

    expect(source).toContain('class="fill activity-fill-default"')
    expect(source).toContain('.activity-fill-default {')
    expect(source).not.toContain('style="width: 85%"')
  })
})
