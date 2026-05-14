import { beforeEach, describe, expect, it, vi } from 'vitest'

const getMock = vi.fn()

vi.mock('element-plus', () => ({
  ElNotification: vi.fn(),
}))

vi.mock('@/api/apiClient.ts', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('versionNegotiator', () => {
  beforeEach(() => {
    vi.resetModules()
    getMock.mockReset()
    getMock.mockImplementation(async (url: string) => {
      if (url === '/health') {
        return {
          success: true,
          data: { version: '1.0.0' },
        }
      }

      return {
        success: false,
        data: null,
      }
    })
  })

  it('does not probe contract active versions during module startup', async () => {
    await import('../versionNegotiator')

    expect(getMock).toHaveBeenCalledWith('/health')
    expect(getMock).not.toHaveBeenCalledWith('/contracts/versions/technical/active')
    expect(getMock).not.toHaveBeenCalledWith('/contracts/versions/market/v2/active')
  })

  it('builds the canonical active contract path', async () => {
    const module = await import('../versionNegotiator')

    expect(module.resolveContractVersionPath('/api/v1/technical')).toBe('/contracts/versions/technical/active')
    expect(module.resolveContractVersionPath('/api/market/v2')).toBe('/contracts/versions/market/v2/active')
  })

  it('falls back to configured versions when contract probing returns success=false', async () => {
    const module = await import('../versionNegotiator')
    await module.refreshApiVersions()

    expect(module.getEndpointVersion('/api/v1/technical/overview')).toBe('1.0.0')
    expect(module.getEndpointVersion('/api/market/v2/quotes')).toBe('2.0.0')
    expect(getMock).toHaveBeenCalledWith('/contracts/versions/technical/active')
    expect(getMock).toHaveBeenCalledWith('/contracts/versions/market/v2/active')
  })

  it('uses the endpoint configured version as the default compatibility requirement', async () => {
    const module = await import('../versionNegotiator')
    await module.refreshApiVersions()

    expect(module.checkApiCompatibility('/api/v1/technical').isCompatible).toBe(true)
    expect(module.checkApiCompatibility('/api/market/v2').isCompatible).toBe(true)
    expect(module.checkApiCompatibility('/api/market/v2').requiredVersion).toBe('2.0.0')
  })

  it('calculates a breaking migration path between incompatible major versions', async () => {
    const module = await import('../versionNegotiator')
    await module.refreshApiVersions()

    const migrationPath = module.calculateApiMigrationPath('/api/v1/market/quotes', '2.0.0')

    expect(migrationPath.isBreaking).toBe(true)
    expect(migrationPath.currentVersion).toBe('1.0.0')
    expect(migrationPath.targetVersion).toBe('2.0.0')
    expect(migrationPath.steps).toEqual([
      {
        fromVersion: '1.0.0',
        toVersion: '2.0.0',
        type: 'breaking',
        changes: ['API版本1.0.0与所需版本2.0.0不兼容'],
      },
    ])
  })

  it('adapts request endpoint and version headers when a target version prefix exists', async () => {
    const module = await import('../versionNegotiator')
    await module.refreshApiVersions()

    const adapted = module.adaptApiRequestForVersion('/api/v1/market/quotes', { symbol: '000001' }, '2.0.0')

    expect(adapted.endpoint).toBe('/api/market/v2/quotes')
    expect(adapted.payload).toEqual({ symbol: '000001' })
    expect(adapted.headers).toEqual({
      'X-API-Version': '2.0.0',
      'X-API-Version-From': '1.0.0',
      'X-API-Migration-Path': '1.0.0->2.0.0',
    })
    expect(adapted.migrationPath.isBreaking).toBe(true)
  })
})
