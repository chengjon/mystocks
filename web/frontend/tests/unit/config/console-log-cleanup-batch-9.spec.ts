import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 9', () => {
  it('removes pure logger helpers from useSSE helpers module', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/composables/useSSE.helpers.js'), 'utf8')
    expect(source).not.toContain('console.log(')
  })
})
