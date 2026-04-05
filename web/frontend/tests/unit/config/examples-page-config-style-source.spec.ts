import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Examples PageConfig style source', () => {
  it('keeps PageConfigExample.vue on ArtDeco tokens without hardcoded icon colors', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/examples/PageConfigExample.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')

    expect(source).not.toContain('color="#67C23A"')
    expect(source).not.toContain('color="#909399"')
    expect(source).not.toContain('#303133')
    expect(source).not.toContain('#f5f7fa')
    expect(source).not.toContain('#e83e8c')
    expect(source).not.toContain('padding: 20px')
  })
})
