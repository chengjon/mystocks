import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '../apiClient'
import { authApi } from '../index'

vi.mock('../apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('authApi client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it('submits login credentials to the canonical v1 form endpoint without CSRF bootstrap', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      success: true,
      code: 200,
      data: { token: 'jwt-token', token_type: 'bearer' },
    } as never)

    await authApi.login('trader', 'secret')

    expect(apiClient.post).toHaveBeenCalledTimes(1)
    const [url, body, config] = vi.mocked(apiClient.post).mock.calls[0]

    expect(url).toBe('/v1/auth/login')
    expect(body).toBeInstanceOf(URLSearchParams)
    expect((body as URLSearchParams).get('username')).toBe('trader')
    expect((body as URLSearchParams).get('password')).toBe('secret')
    expect(config).toEqual({
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      skipCSRF: true,
    })
  })
})
