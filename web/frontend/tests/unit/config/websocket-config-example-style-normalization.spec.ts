import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('WebSocketConfigExample style normalization', () => {
  it('moves static route selector layout styles into semantic classes', () => {
    const source = readSource('src/views/examples/WebSocketConfigExample.vue')

    expect(source).toContain('class="route-select"')
    expect(source).toContain('class="route-name"')
    expect(source).toContain('class="route-meta"')
    expect(source).toContain('class="route-description"')
    expect(source).toContain('var(--color-text-secondary)')
    expect(source).toContain('var(--color-text-tertiary)')

    expect(source).not.toContain('style="width: 100%"')
    expect(source).not.toContain('style="float: left"')
    expect(source).not.toContain('style="float: right; color: #8492a6; font-size: 13px"')
    expect(source).not.toContain('style="margin-left: 10px"')
    expect(source).not.toContain('color: #8492a6')
    expect(source).not.toContain('color: #909399')
  })
})
