import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('realtime monitor type cleanup', () => {
  it('keeps the archived realtime monitor shell free of ts-nocheck', () => {
    const source = readFileSync(
      resolve(process.cwd(), '../../archive/web/frontend/src/views/root-legacy/real-time-monitor/RealTimeMonitor.vue'),
      'utf8',
    )
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
