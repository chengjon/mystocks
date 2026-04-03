import { describe, expect, it } from 'vitest'

import {
  assertSupportedSystemSettingsWrite,
  buildSystemSettingsSnapshot,
  getUnsupportedSystemSettingsSections,
} from '../systemSettingsContract'

describe('systemSettingsContract', () => {
  it('builds a degraded snapshot that keeps datasource as the only backend-backed section', () => {
    const datasource = { providers: ['akshare'], writable: true }

    const snapshot = buildSystemSettingsSnapshot({ datasource })

    expect(snapshot.general).toBeNull()
    expect(snapshot.datasource).toEqual(datasource)
    expect(snapshot.notification).toBeNull()
    expect(snapshot.security).toBeNull()
    expect(snapshot.meta).toEqual({
      contractStatus: 'degraded',
      unifiedBackendApiAvailable: false,
      backendReadSections: ['datasource'],
      backendWriteSections: ['datasource'],
      unsupportedSections: ['general', 'notification', 'security'],
      pageSaveMode: 'local-storage-degrade',
    })
  })

  it('detects unsupported sections for unified system settings writes', () => {
    const unsupported = getUnsupportedSystemSettingsSections({
      general: { timezone: 'Asia/Shanghai' },
      datasource: { providers: ['akshare'] },
      notification: { email: true },
      security: { twoFactor: false },
    })

    expect(unsupported).toEqual(['general', 'notification', 'security'])
  })

  it('rejects writes outside the datasource section', () => {
    expect(() =>
      assertSupportedSystemSettingsWrite({
        general: { timezone: 'Asia/Shanghai' },
        datasource: { providers: ['akshare'] },
      }),
    ).toThrow(/unsupported unified system settings sections/i)
  })

  it('allows datasource-only writes to pass through', () => {
    expect(() =>
      assertSupportedSystemSettingsWrite({
        datasource: { providers: ['akshare'], writable: true },
      }),
    ).not.toThrow()
  })
})
