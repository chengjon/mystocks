import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ArtDecoLayoutEnhanced accessibility contract', () => {
  it('keeps the active shell skip-link target wired to the main landmark', () => {
    const source = readSource('src/layouts/ArtDecoLayoutEnhanced.vue')

    expect(source).toContain('<ArtDecoSkipLink />')
    expect(source).toContain("import ArtDecoSkipLink from '@/components/artdeco/base/ArtDecoSkipLink.vue'")
    expect(source).toMatch(/<main[\s\S]*id="main-content"[\s\S]*tabindex="-1"[\s\S]*>/)
  })
})
