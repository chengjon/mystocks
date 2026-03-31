import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PageTitleDemo style normalization', () => {
  it('moves static width and spacing styles into semantic classes', () => {
    const source = readSource('src/views/PageTitleDemo.vue')

    expect(source).toContain('class="demo-input-300"')
    expect(source).toContain('class="demo-input-400"')
    expect(source).toContain('demo-input-with-gap')
    expect(source).toContain('class="demo-result-spacer"')
    expect(source).toContain('class="demo-stock-input"')
    expect(source).toContain('.demo-input-with-gap {')

    expect(source).not.toContain('style="width: 300px"')
    expect(source).not.toContain('style="width: 400px"')
    expect(source).not.toContain('style="width: 400px; margin-bottom: 10px"')
    expect(source).not.toContain('style="width: 200px; margin-right: 10px"')
    expect(source).not.toContain('style="margin-top: 10px"')
    expect(source).not.toContain('style="width: 300px; margin-bottom: 10px"')
  })
})
