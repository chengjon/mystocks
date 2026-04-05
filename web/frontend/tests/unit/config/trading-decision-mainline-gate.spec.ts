import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Trading decision mainline gate', () => {
  it('keeps trading-decision views under changed-scope directory coverage', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/trading-decision --changed-from-git')
  })
})
