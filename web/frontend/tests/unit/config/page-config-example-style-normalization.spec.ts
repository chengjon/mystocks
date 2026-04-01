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

    expect(source).not.toContain('color="#67C23A"')
    expect(source).not.toContain('color="#909399"')
  })
})
