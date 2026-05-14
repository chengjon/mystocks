import { afterEach, describe, expect, it, vi } from 'vitest'

interface CapturedRequest {
  url?: string
  method?: string
  headers: Record<string, string>
  data?: unknown
}

interface CapturedResponse {
  data: {
    success: boolean
    code: number
    data: {
      url?: string
      headers: Record<string, string>
    }
    message: string
    timestamp: string
    request_id?: string
    errors: null
  }
  headers: Record<string, string>
  status: number
  statusText: string
  config: CapturedRequest
}

type RequestFulfilled = (config: CapturedRequest) => CapturedRequest | Promise<CapturedRequest>
type ResponseFulfilled = (response: CapturedResponse) => CapturedResponse

interface RequestConfig {
  headers?: Record<string, string>
  data?: unknown
}

function createAxiosHarness(): {
  axios: {
    create: ReturnType<typeof vi.fn>
    get: ReturnType<typeof vi.fn>
  }
  capturedRequests: CapturedRequest[]
} {
  const requestHandlers: Array<{ fulfilled?: RequestFulfilled }> = []
  const responseHandlers: Array<{ fulfilled?: ResponseFulfilled }> = []
  const capturedRequests: CapturedRequest[] = []

  const instance = {
    defaults: {
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    },
    interceptors: {
      request: {
        handlers: requestHandlers,
        use(fulfilled?: RequestFulfilled): number {
          requestHandlers.push({ fulfilled })
          return requestHandlers.length - 1
        },
      },
      response: {
        handlers: responseHandlers,
        use(fulfilled?: ResponseFulfilled): number {
          responseHandlers.push({ fulfilled })
          return responseHandlers.length - 1
        },
      },
    },
    async get(url: string, config: RequestConfig = {}): Promise<CapturedResponse> {
      let request: CapturedRequest = {
        ...config,
        url,
        method: 'get',
        headers: { ...(config.headers ?? {}) },
      }

      for (const handler of requestHandlers) {
        if (handler.fulfilled) {
          request = await handler.fulfilled(request)
        }
      }

      capturedRequests.push(request)

      let response: CapturedResponse = {
        data: {
          success: true,
          code: 0,
          data: {
            url: request.url,
            headers: request.headers,
          },
          message: 'ok',
          timestamp: '2026-05-15T00:00:00.000Z',
          errors: null,
        },
        headers: {},
        status: 200,
        statusText: 'OK',
        config: request,
      }

      for (const handler of responseHandlers) {
        if (handler.fulfilled) {
          response = handler.fulfilled(response)
        }
      }

      return response
    },
  }

  const axios = {
    create: vi.fn(() => instance),
    get: vi.fn(),
  }

  return { axios, capturedRequests }
}

async function importApiClientWithAxiosHarness(): Promise<{
  apiClient: typeof import('../apiClient')['apiClient']
  capturedRequests: CapturedRequest[]
}> {
  vi.resetModules()
  const harness = createAxiosHarness()
  vi.doMock('axios', () => ({
    default: harness.axios,
  }))

  const module = await import('../apiClient')
  return {
    apiClient: module.apiClient,
    capturedRequests: harness.capturedRequests,
  }
}

afterEach(() => {
  vi.doUnmock('axios')
  vi.resetModules()
  vi.clearAllMocks()
})

describe('apiClient version negotiation integration', () => {
  it('adapts a target-version request through the public apiClient path', async () => {
    const { apiClient, capturedRequests } = await importApiClientWithAxiosHarness()

    const response = await apiClient.get<{
      success: boolean
      data: {
        url?: string
        headers: Record<string, string>
      }
    }>('/v1/market/quotes', {
      headers: {
        'X-API-Version': '2.0.0',
      },
    })

    expect(capturedRequests).toHaveLength(1)
    expect(capturedRequests[0].url).toBe('/market/v2/quotes')
    expect(capturedRequests[0].headers).toMatchObject({
      'X-API-Version': '2.0.0',
      'X-API-Version-From': '1.0.0',
      'X-API-Migration-Path': '1.0.0->2.0.0',
    })
    expect(response.data.url).toBe('/market/v2/quotes')
  })

  it('keeps unversioned requests on the original endpoint', async () => {
    const { apiClient, capturedRequests } = await importApiClientWithAxiosHarness()

    await apiClient.get('/v1/market/quotes')

    expect(capturedRequests).toHaveLength(1)
    expect(capturedRequests[0].url).toBe('/v1/market/quotes')
    expect(capturedRequests[0].headers['X-API-Version-From']).toBeUndefined()
    expect(capturedRequests[0].headers['X-API-Migration-Path']).toBeUndefined()
  })
})
