import type { SystemSettings, SystemSettingsSection } from './TradingApiManager.types.ts'

const BACKEND_SUPPORTED_SECTIONS = ['datasource'] as const satisfies ReadonlyArray<SystemSettingsSection>
const UNSUPPORTED_SECTIONS = ['general', 'notification', 'security'] as const satisfies ReadonlyArray<SystemSettingsSection>

type SystemSettingsSnapshotInput = {
  datasource: unknown | null
}

export function buildSystemSettingsSnapshot({
  datasource,
}: SystemSettingsSnapshotInput): SystemSettings {
  return {
    general: null,
    datasource,
    notification: null,
    security: null,
    meta: {
      contractStatus: 'degraded',
      unifiedBackendApiAvailable: false,
      backendReadSections: [...BACKEND_SUPPORTED_SECTIONS],
      backendWriteSections: [...BACKEND_SUPPORTED_SECTIONS],
      unsupportedSections: [...UNSUPPORTED_SECTIONS],
      pageSaveMode: 'local-storage-degrade',
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
      'System-Config currently supports only datasource backend writes; other sections remain degraded.',
  )
}
