import type { SystemSettings, SystemSettingsSection } from './TradingApiManager.types.ts'

const BACKEND_SUPPORTED_SECTIONS = ['datasource', 'notification'] as const satisfies ReadonlyArray<SystemSettingsSection>
const UNSUPPORTED_SECTIONS = ['general', 'security'] as const satisfies ReadonlyArray<SystemSettingsSection>

type SystemSettingsSnapshotInput = {
  datasource: unknown | null
  notification: unknown | null
}

export function buildSystemSettingsSnapshot({
  datasource,
  notification,
}: SystemSettingsSnapshotInput): SystemSettings {
  return {
    general: null,
    datasource,
    notification,
    security: null,
    meta: {
      contractStatus: 'sectioned',
      unifiedBackendApiAvailable: false,
      backendReadSections: [...BACKEND_SUPPORTED_SECTIONS],
      backendWriteSections: [...BACKEND_SUPPORTED_SECTIONS],
      unsupportedSections: [...UNSUPPORTED_SECTIONS],
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
    },
  }
}

export function getUnsupportedSystemSettingsSections(
  settings: Partial<SystemSettings>,
): SystemSettingsSection[] {
  return UNSUPPORTED_SECTIONS.filter((section) => settings[section] != null)
}

export function assertSupportedSystemSettingsWrite(settings: Partial<SystemSettings>): void {
  const unsupported = getUnsupportedSystemSettingsSections(settings)

  if (unsupported.length === 0) {
    return
  }

  throw new Error(
    `Unsupported unified system settings sections: ${unsupported.join(', ')}. ` +
      'System-Config currently supports datasource and notification backend writes; other sections remain unavailable.',
  )
}
