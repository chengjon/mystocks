import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getDataSourceConfigMock,
  updateDataSourceConfigMock,
  getNotificationSettingsMock,
  updateNotificationSettingsMock,
} = vi.hoisted(() => ({
  getDataSourceConfigMock: vi.fn(),
  updateDataSourceConfigMock: vi.fn(),
  getNotificationSettingsMock: vi.fn(),
  updateNotificationSettingsMock: vi.fn(),
}))

vi.mock('@/api/index.ts', () => ({
  dataApi: {},
  monitoringApi: {
    getDataSourceConfig: getDataSourceConfigMock,
    updateDataSourceConfig: updateDataSourceConfigMock,
  },
  strategyApi: {
    getSignals: vi.fn(),
  },
}))

vi.mock('@/api/market.ts', () => ({
  marketApi: {},
}))

vi.mock('@/services/api/marketService.ts', () => ({
  marketService: {},
}))

vi.mock('@/api/strategy.ts', () => ({
  strategyApi: {},
}))

vi.mock('@/api/monitoring.ts', () => ({
  monitoringApi: {},
}))

vi.mock('@/api/trade.ts', () => ({
  tradeApi: {},
}))

vi.mock('@/api/indicatorApi.ts', () => ({
  indicatorApi: {},
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {
    getNotificationSettings: getNotificationSettingsMock,
    updateNotificationSettings: updateNotificationSettingsMock,
  },
}))

import { TradingApiManager } from '../TradingApiManager'

describe('TradingApiManager system settings contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns a sectioned snapshot and reads datasource plus notification from canonical truths', async () => {
    getDataSourceConfigMock.mockResolvedValue({
      success: true,
      data: {
        providers: ['akshare'],
        writable: true,
      },
    })

    getNotificationSettingsMock.mockResolvedValue({
      email_enabled: true,
      websocket_enabled: true,
    })

    const manager = new TradingApiManager()
    const snapshot = await manager.getSystemSettings()

    expect(snapshot.datasource).toEqual({
      providers: ['akshare'],
      writable: true,
    })
    expect(snapshot.notification).toEqual({
      email_enabled: true,
      websocket_enabled: true,
    })
    expect(snapshot.meta.contractStatus).toBe('sectioned')
    expect(snapshot.meta.backendReadSections).toEqual(['datasource', 'notification'])
    expect(getNotificationSettingsMock).toHaveBeenCalledTimes(1)
  })

  it('rejects writes to unsupported unified system settings sections', async () => {
    const manager = new TradingApiManager()

    await expect(
      manager.saveSystemSettings({
        general: { timezone: 'Asia/Shanghai' },
      }),
    ).rejects.toThrow(/unsupported unified system settings sections/i)
  })

  it('persists datasource writes through the backend-backed config route only', async () => {
    updateDataSourceConfigMock.mockResolvedValue({
      success: true,
      data: {},
    })

    const manager = new TradingApiManager()
    const datasourcePayload = {
      operations: [
        {
          action: 'update',
          endpoint_name: 'akshare.stock_zh_a_hist',
          updates: {
            status: 'maintenance',
          },
        },
      ],
    }

    await expect(
      manager.saveSystemSettings({
        datasource: datasourcePayload,
      }),
    ).resolves.toBe(true)

    expect(updateDataSourceConfigMock).toHaveBeenCalledWith(datasourcePayload)
    expect(updateNotificationSettingsMock).not.toHaveBeenCalled()
  })

  it('persists notification writes through the canonical notification preferences route', async () => {
    updateNotificationSettingsMock.mockResolvedValue(undefined)

    const manager = new TradingApiManager()
    const notificationPayload = {
      email_enabled: false,
      websocket_enabled: true,
    }

    await expect(
      manager.saveSystemSettings({
        notification: notificationPayload,
      }),
    ).resolves.toBe(true)

    expect(updateNotificationSettingsMock).toHaveBeenCalledWith(notificationPayload)
    expect(updateDataSourceConfigMock).not.toHaveBeenCalled()
  })
})
