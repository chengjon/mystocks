import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TaskTable style normalization', () => {
  it('moves the manual schedule fallback color into a semantic class', () => {
    const source = readSource('src/components/task/TaskTable.vue')

    expect(source).toContain('class="schedule-manual"')
    expect(source).toContain('.schedule-manual {')
    expect(source).toContain('var(--color-text-tertiary)')
    expect(source).not.toContain('style="color: #909399"')
  })
})
