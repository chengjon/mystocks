import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Technical mainline gate', () => {
  it('keeps technical components under changed-scope directory coverage without file-level fallback', () => {
    const pkg = readFileSync(resolve(process.cwd(), 'package.json'), 'utf8')

    expect(pkg).toContain('--target-dir src/components/technical --changed-from-git')
    expect(pkg).not.toContain('--target-file src/components/technical/IndicatorPanel.vue --changed-from-git')
  })
})
