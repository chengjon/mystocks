import { describe, expect, it } from 'vitest'
import {
  extractBacktestTaskId,
  normalizeBacktestTaskStatus,
  isBacktestTerminalStatus,
  toBacktestStatusMessage
} from '@/views/artdeco-pages/strategy-tabs/backtestQuickRun'

describe('backtestQuickRun helpers', () => {
  it('extracts task id from common API fields', () => {
    expect(extractBacktestTaskId({ task_id: 't-1' })).toBe('t-1')
    expect(extractBacktestTaskId({ taskId: 't-2' })).toBe('t-2')
    expect(extractBacktestTaskId({ id: 't-3' })).toBe('t-3')
    expect(extractBacktestTaskId({ data: { task_id: 't-4' } })).toBe('t-4')
    expect(extractBacktestTaskId({})).toBeNull()
  })

  it('normalizes backend status values to cross-tab status model', () => {
    expect(normalizeBacktestTaskStatus('pending')).toBe('queued')
    expect(normalizeBacktestTaskStatus('initializing')).toBe('queued')
    expect(normalizeBacktestTaskStatus('running')).toBe('running')
    expect(normalizeBacktestTaskStatus('success')).toBe('completed')
    expect(normalizeBacktestTaskStatus('done')).toBe('completed')
    expect(normalizeBacktestTaskStatus('failed')).toBe('failed')
    expect(normalizeBacktestTaskStatus('cancelled')).toBe('failed')
    expect(normalizeBacktestTaskStatus('unknown')).toBeNull()
  })

  it('detects terminal status and formats status messages', () => {
    expect(isBacktestTerminalStatus('completed')).toBe(true)
    expect(isBacktestTerminalStatus('failed')).toBe(true)
    expect(isBacktestTerminalStatus('queued')).toBe(false)
    expect(isBacktestTerminalStatus('running')).toBe(false)

    expect(toBacktestStatusMessage('queued')).toContain('排队')
    expect(toBacktestStatusMessage('running')).toContain('执行')
    expect(toBacktestStatusMessage('completed')).toContain('完成')
    expect(toBacktestStatusMessage('failed')).toContain('失败')
  })
})
