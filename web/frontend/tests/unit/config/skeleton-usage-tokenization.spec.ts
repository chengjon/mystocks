import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('SkeletonUsage tokenization', () => {
  it('keeps skeleton demo sizing on design-token expressions', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/SkeletonUsage.vue'), 'utf8')

    expect(source).toContain("@use '@/styles/artdeco-tokens.scss' as *;")
    expect(source).toContain(":width=\"'var(--artdeco-spacing-16)'\"")
    expect(source).toContain(":height=\"'var(--artdeco-spacing-16)'\"")
    expect(source).toContain("profile-name-skeleton")

    expect(source).not.toContain('width="64px"')
    expect(source).not.toContain('height: 24px; margin-bottom: 8px;')
    expect(source).not.toContain('height="300px"')
  })
})
