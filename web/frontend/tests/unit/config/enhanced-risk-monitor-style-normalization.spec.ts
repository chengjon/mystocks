import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('EnhancedRiskMonitor style normalization', () => {
  it('moves static control button spacing and gpu icon colors into classes', () => {
    const source = readSource('src/views/EnhancedRiskMonitor.vue')

    expect(source).toContain('class="control-action-button"')
    expect(source).toContain('gpu-status-icon--available')
    expect(source).toContain('gpu-status-icon--unavailable')

    expect(source).toContain('.control-action-button {')
    expect(source).toContain('.gpu-status-icon--available {')
    expect(source).toContain('.gpu-status-icon--unavailable {')

    expect(source).not.toContain('style="margin-top: 10px;"')
    expect(source).not.toContain('style="color: #67C23A;"')
    expect(source).not.toContain('style="color: #F56C6C;"')
  })
})
