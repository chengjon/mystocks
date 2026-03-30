import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('console log cleanup batch 48', () => {
  it('removes enhanced risk monitor tab and websocket logs', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/views/EnhancedRiskMonitor.vue'), 'utf8')

    expect(source).not.toContain("console.log('Tab changed to:', tab.props.name)")
    expect(source).not.toContain("console.log('WebSocket connected for real-time risk updates')")
    expect(source).not.toContain("console.log('WebSocket disconnected')")
  })
})
