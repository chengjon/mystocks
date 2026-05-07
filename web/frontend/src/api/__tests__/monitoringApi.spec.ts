import { beforeEach, describe, expect, it, vi } from 'vitest'

const { apiGetMock, apiPutMock, apiPostMock, apiDeleteMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
  apiPutMock: vi.fn(),
  apiPostMock: vi.fn(),
  apiDeleteMock: vi.fn()
}))

vi.mock('../apiClient', () => ({
  apiClient: {
    get: apiGetMock,
    put: apiPutMock,
    post: apiPostMock,
    delete: apiDeleteMock
  }
}))

import { monitoringApi } from '../index'

describe('monitoringApi data source config endpoints', () => {
  beforeEach(() => {
    apiGetMock.mockReset().mockResolvedValue({})
    apiPutMock.mockReset().mockResolvedValue({})
    apiPostMock.mockReset().mockResolvedValue({})
    apiDeleteMock.mockReset().mockResolvedValue({})
  })

  it('uses trailing slash for getDataSourceConfig to avoid /{endpoint_name} route collision', async () => {
    await monitoringApi.getDataSourceConfig()

    expect(apiGetMock).toHaveBeenCalledWith('/v1/data-sources/config/')
  })

  it('uses the dedicated v1 system resources contract for the resource usage workbench', async () => {
    await monitoringApi.getSystemResources({ window_minutes: 60, include_processes: true })

    expect(apiGetMock).toHaveBeenCalledWith('/v1/system/resources', {
      params: { window_minutes: 60, include_processes: true },
    })
  })
})
