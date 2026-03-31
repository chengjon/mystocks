import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('LynchModel style normalization', () => {
  it('moves static marker positions into CSS classes', () => {
    const source = readSource('src/views/artdeco-pages/components/LynchModel.vue')

    expect(source).not.toContain('style="left: 25%"')
    expect(source).not.toContain('style="left: 50%"')
    expect(source).not.toContain('style="left: 75%"')

    expect(source).toContain('.marker.undervaluated')
    expect(source).toContain('.marker.fair')
    expect(source).toContain('.marker.overvaluated')
  })
})
