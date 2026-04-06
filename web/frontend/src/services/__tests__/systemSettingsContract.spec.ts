import { describe, expect, it } from 'vitest'

import {
  assertSupportedSystemSettingsWrite,
  buildSystemSettingsSnapshot,
  getUnsupportedSystemSettingsSections,
} from '../systemSettingsContract'

describe('systemSettingsContract', () => {
  it('builds a sectioned snapshot with datasource and notification as backend-backed sections', () => {
    const datasource = { providers: ['akshare'], writable: true }
    const notification = { email_enabled: true, websocket_enabled: true }

    const snapshot = buildSystemSettingsSnapshot({ datasource, notification })

    expect(snapshot.general).toBeNull()
    expect(snapshot.datasource).toEqual(datasource)
    expect(snapshot.notification).toEqual(notification)
    expect(snapshot.security).toBeNull()
    expect(snapshot.meta).toEqual({
      contractStatus: 'sectioned',
      unifiedBackendApiAvailable: false,
      backendReadSections: ['datasource', 'notification'],
      backendWriteSections: ['datasource', 'notification'],
      unsupportedSections: ['general', 'security'],
      pageSaveMode: 'section-routed',
      sections: {
        general: {
          scope: 'system',
          owner: 'system-settings',
          readStatus: 'unavailable',
          writeStatus: 'unavailable',
          evidenceType: 'inferred',
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
          readStatus: 'unavailable',
          writeStatus: 'unavailable',
          evidenceType: 'inferred',
        },
      },
    })
  })

  it('detects unsupported sections for unified system settings writes', () => {
    const unsupported = getUnsupportedSystemSettingsSections({
      general: { timezone: 'Asia/Shanghai' },
      datasource: { providers: ['akshare'] },
      notification: { email: true },
      security: { twoFactor: false },
    })

    expect(unsupported).toEqual(['general', 'security'])
  })

  it('rejects writes outside the datasource section', () => {
    expect(() =>
      assertSupportedSystemSettingsWrite({
        general: { timezone: 'Asia/Shanghai' },
        datasource: { providers: ['akshare'] },
      }),
    ).toThrow(/unsupported unified system settings sections/i)
  })

  it('allows datasource and notification writes to pass through', () => {
    expect(() =>
      assertSupportedSystemSettingsWrite({
        datasource: { providers: ['akshare'], writable: true },
        notification: { email_enabled: true },
      }),
    ).not.toThrow()
  })
})
