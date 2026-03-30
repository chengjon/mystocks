import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 57', () => {
  it('removes ui store realtime update stub logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/stores/ui.ts'), 'utf8')

    expect(source).not.toContain("console.log('Setting up realtime updates:', updates)")
    expect(source).not.toContain("console.log('Started realtime updates')")
    expect(source).not.toContain("console.log('Stopped realtime updates')")
  })
})
