import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TaskForm style normalization', () => {
  it('moves static field widths and scheduling hint styling into semantic classes', () => {
    const source = readSource('src/components/task/TaskForm.vue')

    expect(source).toContain('class="task-form-control"')
    expect(source).toContain('class="task-form-hint"')

    expect(source).toContain('.task-form-control {')
    expect(source).toContain('.task-form-hint {')

    expect(source).not.toContain('style="width: 100%"')
    expect(source).not.toContain('style="margin-top: 8px; color: #909399; font-size: 12px"')
  })
})
