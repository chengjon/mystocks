import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('MonitoringDashboard style normalization', () => {
  it('moves static stat gradients and colors into semantic classes', () => {
    const viewSource = readSource('src/views/monitoring/MonitoringDashboard.vue')
    const styleSource = readSource('src/views/monitoring/styles/MonitoringDashboard.scss')

    expect(viewSource).toContain('stat-icon-market')
    expect(viewSource).toContain('stat-icon-rise')
    expect(viewSource).toContain('stat-icon-fall')
    expect(viewSource).toContain('stat-icon-warning')
    expect(viewSource).toContain('stat-value-rise')
    expect(viewSource).toContain('stat-value-fall')
    expect(viewSource).toContain('stat-value-warning')

    expect(viewSource).not.toContain('style="background: linear-gradient(45deg, var(--gold-primary), #E5C158);"')
    expect(viewSource).not.toContain('style="background: linear-gradient(45deg, var(--rise), #FF8A80);"')
    expect(viewSource).not.toContain('style="background: linear-gradient(45deg, var(--fall), #69F0AE);"')
    expect(viewSource).not.toContain('style="background: linear-gradient(45deg, var(--warning), #FFD54F);"')
    expect(viewSource).not.toContain('style="color: var(--rise);"')
    expect(viewSource).not.toContain('style="color: var(--fall);"')
    expect(viewSource).not.toContain('style="color: var(--warning);"')

    expect(styleSource).toContain('.stat-icon-market')
    expect(styleSource).toContain('.stat-value-warning')
  })
})
