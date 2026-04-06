import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getSystemGeneralSettingsMock,
  updateSystemGeneralSettingsMock,
  getDataSourceConfigMock,
  updateDataSourceConfigMock,
  getNotificationSettingsMock,
  updateNotificationSettingsMock,
  getSystemSecuritySettingsMock,
  updateSystemSecuritySettingsMock,
} = vi.hoisted(() => ({
  getSystemGeneralSettingsMock: vi.fn(),
  updateSystemGeneralSettingsMock: vi.fn(),
  getDataSourceConfigMock: vi.fn(),
  updateDataSourceConfigMock: vi.fn(),
  getNotificationSettingsMock: vi.fn(),
  updateNotificationSettingsMock: vi.fn(),
  getSystemSecuritySettingsMock: vi.fn(),
  updateSystemSecuritySettingsMock: vi.fn(),
}))

vi.mock('@/api/index.ts', () => ({
  dataApi: {},
  monitoringApi: {
    getSystemGeneralSettings: getSystemGeneralSettingsMock,
    updateSystemGeneralSettings: updateSystemGeneralSettingsMock,
    getDataSourceConfig: getDataSourceConfigMock,
    getSystemSecuritySettings: getSystemSecuritySettingsMock,
    updateDataSourceConfig: updateDataSourceConfigMock,
    updateSystemSecuritySettings: updateSystemSecuritySettingsMock,
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

  it('returns a sectioned snapshot and reads all sections through their canonical truths', async () => {
    getSystemGeneralSettingsMock.mockResolvedValue({
      success: true,
      data: {
        backend_url: 'http://localhost:8020',
        max_backtest_jobs: 4,
      },
    })
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
    getSystemSecuritySettingsMock.mockResolvedValue({
      success: true,
      data: {
        session_timeout_minutes: 120,
        mfa_required: false,
      },
    })

    const manager = new TradingApiManager()
    const snapshot = await manager.getSystemSettings()

    expect(snapshot.general).toEqual({
      backend_url: 'http://localhost:8020',
      max_backtest_jobs: 4,
    })
    expect(snapshot.datasource).toEqual({
      providers: ['akshare'],
      writable: true,
    })
    expect(snapshot.notification).toEqual({
      email_enabled: true,
      websocket_enabled: true,
    })
    expect(snapshot.security).toEqual({
      session_timeout_minutes: 120,
      mfa_required: false,
    })
    expect(snapshot.meta.contractStatus).toBe('sectioned')
    expect(snapshot.meta.backendReadSections).toEqual(['general', 'datasource', 'notification', 'security'])
    expect(getSystemGeneralSettingsMock).toHaveBeenCalledTimes(1)
    expect(getNotificationSettingsMock).toHaveBeenCalledTimes(1)
    expect(getSystemSecuritySettingsMock).toHaveBeenCalledTimes(1)
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

  it('persists general writes through the canonical system settings route', async () => {
    updateSystemGeneralSettingsMock.mockResolvedValue({
      success: true,
      data: {},
    })

    const manager = new TradingApiManager()
    const generalPayload = {
      backend_url: 'http://localhost:9020',
      max_backtest_jobs: 6,
      default_slippage_percent: 0.08,
      fee_rate_bps: 3.2,
    }

    await expect(
      manager.saveSystemSettings({
        general: generalPayload,
      }),
    ).resolves.toBe(true)

    expect(updateSystemGeneralSettingsMock).toHaveBeenCalledWith(generalPayload)
    expect(updateDataSourceConfigMock).not.toHaveBeenCalled()
    expect(updateNotificationSettingsMock).not.toHaveBeenCalled()
    expect(updateSystemSecuritySettingsMock).not.toHaveBeenCalled()
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

  it('persists security writes through the canonical system settings route', async () => {
    updateSystemSecuritySettingsMock.mockResolvedValue({
      success: true,
      data: {},
    })

    const manager = new TradingApiManager()
    const securityPayload = {
      session_timeout_minutes: 90,
      mfa_required: true,
      ip_allowlist_enabled: true,
      password_policy_level: 'strict',
    }

    await expect(
      manager.saveSystemSettings({
        security: securityPayload,
      }),
    ).resolves.toBe(true)

    expect(updateSystemSecuritySettingsMock).toHaveBeenCalledWith(securityPayload)
    expect(updateDataSourceConfigMock).not.toHaveBeenCalled()
    expect(updateNotificationSettingsMock).not.toHaveBeenCalled()
  })
})
