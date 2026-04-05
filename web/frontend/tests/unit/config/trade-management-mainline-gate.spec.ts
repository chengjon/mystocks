import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Trade-management mainline gate', () => {
  it('keeps trade-management views under root directory coverage without child fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/views/trade-management --changed-from-git')
    expect(pkg).not.toContain('--target-dir src/views/trade-management/components --changed-from-git')
  })
})
