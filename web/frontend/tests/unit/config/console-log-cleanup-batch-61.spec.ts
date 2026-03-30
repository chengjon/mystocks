import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 61', () => {
  it('removes base layout command palette interaction logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/layouts/BaseLayout.vue'), 'utf8')

    expect(source).not.toContain("console.log('Command Palette opened')")
    expect(source).not.toContain("console.log('Command Palette closed')")
    expect(source).not.toContain("console.log('Navigated to:', path)")
  })
})
