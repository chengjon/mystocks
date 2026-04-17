import { describe, expect, it, vi } from 'vitest'

import {
  isAutomationBrowserSession,
  requestBackendReadiness,
  resolveReadinessEndpoint
} from '../useBackendReadiness'

describe('useBackendReadiness helpers', () => {
  it('resolves readiness endpoint for default api base path', () => {
    expect(resolveReadinessEndpoint('/api')).toBe('/api/health/ready')
  })

  it('resolves readiness endpoint for absolute backend base path', () => {
    expect(resolveReadinessEndpoint('http://localhost:8020')).toBe('http://localhost:8020/api/health/ready')
  })

  it('detects automation browser sessions via navigator.webdriver', () => {
    expect(isAutomationBrowserSession({ webdriver: true } as Navigator)).toBe(true)
    expect(isAutomationBrowserSession({ webdriver: false } as Navigator)).toBe(false)
  })
})

describe('requestBackendReadiness', () => {
  it('keeps blocking behavior for normal browsers when readiness returns 404', async () => {
    const fetchImpl = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: vi.fn().mockResolvedValue({
        success: false,
        message: 'Readiness probe failed with status 404'
      })
    })

    const result = await requestBackendReadiness(fetchImpl as typeof fetch, '/api', false, false)

    expect(result.ready).toBe(false)
    expect(result.backendReady).toBe(false)
    expect(result.usingMockFallback).toBe(false)
    expect(result.message).toContain('后端暂未就绪')
  })

  it('downgrades readiness 404 to non-blocking fallback for automation browsers', async () => {
    const fetchImpl = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: vi.fn().mockResolvedValue({
        success: false,
        message: 'Readiness probe failed with status 404',
        request_id: 'req-ready-404'
      })
    })

    const result = await requestBackendReadiness(fetchImpl as typeof fetch, '/api', false, true)

    expect(result.ready).toBe(true)
    expect(result.backendReady).toBe(false)
    expect(result.usingMockFallback).toBe(true)
    expect(result.requestId).toBe('req-ready-404')
    expect(result.message).toContain('自动化验收模式')
  })
})
