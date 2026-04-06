import { describe, expect, it } from 'vitest'

import {
  assertSupportedSystemSettingsWrite,
  buildSystemSettingsSnapshot,
  getUnsupportedSystemSettingsSections,
} from '../systemSettingsContract'

describe('systemSettingsContract', () => {
  it('builds a sectioned snapshot with all sections mapped to canonical owners', () => {
    const general = {
      backend_url: 'http://localhost:8020',
      max_backtest_jobs: 4,
      default_slippage_percent: 0.05,
      fee_rate_bps: 2.5,
    }
    const datasource = { providers: ['akshare'], writable: true }
    const notification = { email_enabled: true, websocket_enabled: true }
    const security = {
      session_timeout_minutes: 120,
      mfa_required: false,
      ip_allowlist_enabled: false,
      password_policy_level: 'standard',
    }

    const snapshot = buildSystemSettingsSnapshot({ general, datasource, notification, security })

    expect(snapshot.general).toEqual(general)
    expect(snapshot.datasource).toEqual(datasource)
    expect(snapshot.notification).toEqual(notification)
    expect(snapshot.security).toEqual(security)
    expect(snapshot.meta).toEqual({
      contractStatus: 'sectioned',
      unifiedBackendApiAvailable: false,
      backendReadSections: ['general', 'datasource', 'notification', 'security'],
      backendWriteSections: ['general', 'datasource', 'notification', 'security'],
      unsupportedSections: [],
      pageSaveMode: 'section-routed',
      sections: {
        general: {
          scope: 'system',
          owner: 'system-settings',
          readStatus: 'available',
          writeStatus: 'available',
          evidenceType: 'measured',
        },
        datasource: {
          scope: 'system',
          owner: 'data-source-config',
          readStatus: 'available',
          writeStatus: 'available',
          evidenceType: 'measured',
        },
        notification: {
          scope: 'user',
          owner: 'notification-preferences',
          readStatus: 'available',
          writeStatus: 'available',
          evidenceType: 'measured',
        },
        security: {
          scope: 'system',
          owner: 'system-settings',
          readStatus: 'available',
          writeStatus: 'available',
          evidenceType: 'measured',
        },
      },
    })
  })

  it('detects no unsupported sections after general and security contracts land', () => {
    const unsupported = getUnsupportedSystemSettingsSections({
      general: { timezone: 'Asia/Shanghai' },
      datasource: { providers: ['akshare'] },
      notification: { email: true },
      security: { twoFactor: false },
    })

    expect(unsupported).toEqual([])
  })

  it('allows all canonical section writes to pass through', () => {
    expect(() =>
      assertSupportedSystemSettingsWrite({
        general: { timezone: 'Asia/Shanghai' },
        datasource: { providers: ['akshare'] },
        notification: { email_enabled: true },
        security: { session_timeout_minutes: 120 },
      }),
    ).not.toThrow()
  })
})
