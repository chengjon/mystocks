import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('OpenStockDemo style normalization', () => {
  it('moves the login alert button spacing into a semantic class', () => {
    const source = readSource('src/views/OpenStockDemo.vue')

    expect(source).toContain('class="login-alert-button"')
    expect(source).toContain('.login-alert-button {')
    expect(source).not.toContain('style="margin-top: 10px;"')
  })
})
