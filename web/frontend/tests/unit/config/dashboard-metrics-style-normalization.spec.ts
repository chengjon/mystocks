import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('DashboardMetrics style normalization', () => {
  it('moves metric icon colors into semantic classes', () => {
    const viewSource = readSource('src/components/sse/DashboardMetrics.vue')
    const styleSource = readSource('src/components/sse/styles/DashboardMetrics.scss')

    expect(viewSource).toContain('dashboard-metrics-icon--info')
    expect(viewSource).toContain('dashboard-metrics-icon--success')
    expect(viewSource).toContain('dashboard-metrics-icon--danger')
    expect(viewSource).toContain('dashboard-metrics-icon--muted')
    expect(viewSource).toContain('getMetricStateClass(')

    expect(viewSource).not.toContain('color="#409eff"')
    expect(viewSource).not.toContain(':color="getMetricColor(key, value)"')
    expect(viewSource).not.toContain("return '#67c23a'")
    expect(viewSource).not.toContain("return '#f56c6c'")
    expect(viewSource).not.toContain("return '#909399'")

    expect(styleSource).toContain('.dashboard-metrics-icon--info')
    expect(styleSource).toContain('.dashboard-metrics-icon--success')
    expect(styleSource).toContain('.dashboard-metrics-icon--danger')
    expect(styleSource).toContain('.dashboard-metrics-icon--muted')
  })
})
