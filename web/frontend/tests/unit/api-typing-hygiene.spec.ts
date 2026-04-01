import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('frontend api typing hygiene', () => {
  it('uses explicit monitoring response types instead of temporary placeholder comments', () => {
    const source = readSource('src/api/monitoring.ts')

    expect(source).toContain("from '@/utils/monitoring-adapters.types.ts'")
    expect(source).not.toContain('Temporary: Use any for missing generated types')
    expect(source).not.toContain('TODO: Fix type generation to include these types')
    expect(source).toContain('as unknown as SystemStatusResponse')
    expect(source).toContain('as unknown as MonitoringAlertResponse[]')
    expect(source).toContain('as unknown as LogEntryResponse[]')
    expect(source).toContain('as unknown as DataQualityResponse')
  })

  it('awaits strategy request results before applying array and config assertions', () => {
    const source = readSource('src/api/strategy.ts')

    expect(source).toContain("return (await request.get(`${this.baseUrl}/templates`)) as unknown[]")
    expect(source).toContain("return (await request.get(`${this.baseUrl}/${id}/logs`, { params })) as unknown[]")
    expect(source).toContain("}) as StrategyConfigResponse")
  })
})
