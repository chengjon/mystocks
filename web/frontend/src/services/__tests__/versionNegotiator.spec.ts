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
})
