import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('PageConfigExample style normalization', () => {
  it('moves page type icon colors into semantic classes', () => {
    const source = readSource('src/views/examples/PageConfigExample.vue')

    expect(source).toContain('page-type-icon page-type-icon--standard')
    expect(source).toContain('page-type-icon page-type-icon--component')
    expect(source).toContain('.page-type-icon--standard')
    expect(source).toContain('.page-type-icon--component')
    expect(source).toContain('var(--color-text-primary)')
    expect(source).toContain('var(--color-bg-secondary)')
    expect(source).toContain('var(--color-text-tertiary)')
    expect(source).toContain('var(--color-accent)')

    expect(source).not.toContain('color="#67C23A"')
    expect(source).not.toContain('color="#909399"')
    expect(source).not.toContain('#303133')
    expect(source).not.toContain('#f5f7fa')
    expect(source).not.toContain('#e83e8c')
  })
})
