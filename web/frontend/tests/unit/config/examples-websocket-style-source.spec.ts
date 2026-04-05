import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Examples WebSocket style source', () => {
  it('keeps WebSocketConfigExample.vue on ArtDeco tokens without inline style literals', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/views/examples/WebSocketConfigExample.vue'),
      'utf8',
    )

    expect(source).toContain('var(--artdeco-gold-primary)')
    expect(source).toContain('var(--artdeco-fg-primary)')
    expect(source).toContain('var(--artdeco-fg-muted)')
    expect(source).toContain('route-option-label')
    expect(source).toContain('route-option-meta')

    expect(source).not.toContain('style="width: 100%"')
    expect(source).not.toContain('style="float: left"')
    expect(source).not.toContain('style="float: right; color: #8492a6; font-size: 13px"')
    expect(source).not.toContain('style="margin-left: 10px"')
    expect(source).not.toContain('padding: 20px')
    expect(source).not.toContain('#303133')
    expect(source).not.toContain('#909399')
  })
})
