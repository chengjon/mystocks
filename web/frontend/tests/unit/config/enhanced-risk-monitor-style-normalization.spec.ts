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
    expect(source).toContain('var(--color-bg-primary)')
    expect(source).toContain('var(--color-info)')
    expect(source).toContain('var(--color-text-primary)')
    expect(source).toContain('var(--color-success)')
    expect(source).toContain('var(--color-danger)')
    expect(source).toContain('var(--color-text-tertiary)')

    expect(source).not.toContain('style="margin-top: 10px;"')
    expect(source).not.toContain('style="color: #67C23A;"')
    expect(source).not.toContain('style="color: #F56C6C;"')
    expect(source).not.toContain('.enhanced-risk-monitor {\n  padding: 20px;\n  background: #f5f7fa;')
    expect(source).not.toContain('.control-card .card-header {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  font-weight: 600;\n  color: #409EFF;')
    expect(source).not.toContain('.stat-number {\n  font-size: 28px;\n  font-weight: bold;\n  color: #303133;')
    expect(source).not.toContain('.gpu-status-icon--available {\n  color: #67C23A;')
    expect(source).not.toContain('.gpu-status-icon--unavailable {\n  color: #F56C6C;')
    expect(source).not.toContain('.stat-label {\n  font-size: 12px;\n  color: #909399;')
  })
})
