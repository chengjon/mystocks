import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 54', () => {
  it('removes command palette theme toggle log', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/components/menu/CommandPalette.vue'), 'utf8')

    expect(source).not.toContain("console.log('Toggle theme')")
  })
})
