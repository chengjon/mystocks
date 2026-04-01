import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('ExecutionHistory style normalization', () => {
  it('moves static fallback text color and log font styling into semantic classes', () => {
    const source = readSource('src/components/task/ExecutionHistory.vue')

    expect(source).toContain('class="execution-fallback-text"')
    expect(source).toContain('class="execution-log-input"')
    expect(source).toContain('.execution-fallback-text {')
    expect(source).toContain('.execution-log-input {')
    expect(source).toContain('var(--color-danger)')
    expect(source).toContain('var(--color-bg-secondary)')

    expect(source).not.toContain('style="color: #909399"')
    expect(source).not.toContain("style=\"font-family: 'Courier New', monospace\"")
    expect(source).not.toContain('color: #f56c6c;')
    expect(source).not.toContain('background: #f5f7fa;')
  })
})
