import { beforeEach, describe, expect, it, vi } from 'vitest'

const { requestGetMock, requestPutMock, requestPostMock } = vi.hoisted(() => ({
  requestGetMock: vi.fn(),
  requestPutMock: vi.fn(),
  requestPostMock: vi.fn(),
}))

vi.mock('@/utils/request.ts', () => ({
  request: {
    get: requestGetMock,
    put: requestPutMock,
    post: requestPostMock,
  },
}))

import { userApi } from '../user.ts'

describe('userApi notification preference endpoints', () => {
  beforeEach(() => {
    requestGetMock.mockReset().mockResolvedValue({})
    requestPutMock.mockReset().mockResolvedValue({})
    requestPostMock.mockReset().mockResolvedValue({})
  })

  it('reads notification settings from the canonical preferences endpoint', async () => {
    await userApi.getNotificationSettings()

    expect(requestGetMock).toHaveBeenCalledWith('/api/notification/preferences')
  })

  it('writes notification settings to the canonical preferences endpoint', async () => {
    const payload = { email_enabled: false }

    await userApi.updateNotificationSettings(payload)

    expect(requestPostMock).toHaveBeenCalledWith('/api/notification/preferences', payload)
    expect(requestPutMock).not.toHaveBeenCalled()
  })
})
