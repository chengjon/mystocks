import type { SystemSettings, SystemSettingsSection } from './TradingApiManager.types.ts'

const BACKEND_SUPPORTED_SECTIONS = [
  'general',
  'datasource',
  'notification',
  'security',
] as const satisfies ReadonlyArray<SystemSettingsSection>
const UNSUPPORTED_SECTIONS: SystemSettingsSection[] = []

type SystemSettingsSnapshotInput = {
  general: unknown | null
  datasource: unknown | null
  notification: unknown | null
  security: unknown | null
}

export function buildSystemSettingsSnapshot({
  general,
  datasource,
  notification,
  security,
}: SystemSettingsSnapshotInput): SystemSettings {
  return {
    general,
    datasource,
    notification,
    security,
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
      'System-Config currently supports only the canonical routed section writes that are declared in the section contract.',
  )
}
