import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('RiskAlerts style normalization', () => {
  it('moves alert icon colors into semantic classes', () => {
    const source = readSource('src/components/sse/RiskAlerts.vue')

    expect(source).toContain('risk-alerts-icon--safe')
    expect(source).toContain('risk-alerts-icon--info')
    expect(source).toContain('risk-alerts-icon--muted')
    expect(source).toContain('risk-alerts-icon--warning')
    expect(source).toContain('risk-alerts-icon--alert')
    expect(source).toContain('getSeverityStateClass(')

    expect(source).not.toContain('emptyIconColor')
    expect(source).not.toContain('unreadDotColor')
    expect(source).not.toContain('getSeverityColor')
    expect(source).not.toContain(':color="getSeverityColor(alert.severity)"')
  })
})
