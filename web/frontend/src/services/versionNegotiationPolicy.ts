export interface VersionCompatibility {
  isCompatible: boolean
  currentVersion: string
  requiredVersion: string
  breakingChanges?: string[]
  deprecationWarnings?: string[]
}

export interface VersionMigrationStep {
  fromVersion: string
  toVersion: string
  type: 'compatible' | 'breaking'
  changes: string[]
}

export interface VersionMigrationPath {
  currentVersion: string
  targetVersion: string
  isBreaking: boolean
  steps: VersionMigrationStep[]
}

export interface AdaptedApiRequest<TPayload = unknown> {
  endpoint: string
  payload: TPayload
  headers: Record<string, string>
  migrationPath: VersionMigrationPath
}

export interface AdaptedApiClientRequest<TPayload = unknown> extends AdaptedApiRequest<TPayload> {
  url: string
}

type VersionLookup = Iterable<[string, string]> | Record<string, string>

export const VERSION_CONFIG: {
  supportedVersions: {
    min: string
    max: string
    preferred: string
  }
  endpoints: Record<string, string>
  deprecationWarnings: Record<string, string>
  compatibilityMatrix: Record<string, string[]>
} = {
  supportedVersions: {
    min: '1.0.0',
    max: '2.0.0',
    preferred: '1.0.0'
  },

  endpoints: {
    '/api/v1/auth': '1.0.0',
    '/api/auth': '1.0.0',
    '/api/v1/market': '1.0.0',
    '/api/market/v2': '2.0.0',
    '/api/v1/strategy': '1.0.0',
    '/api/v1/monitoring': '1.0.0',
    '/api/v1/technical': '1.0.0',
    '/api/v1/data': '1.0.0',
    '/api/v1/system': '1.0.0',
    '/api/v1/indicators': '1.0.0',
    '/api/v1/tdx': '1.0.0',
    '/api/v1/announcement': '1.0.0',
    '/api/v1/data-sources': '1.0.0',
    '/api/contracts': '1.0.0'
  },

  deprecationWarnings: {
    '0.x.x': 'API版本0.x.x已弃用，请升级到1.0.0+版本',
    '1.0.0': 'API版本1.0.0计划在未来版本中弃用，建议升级到最新版本'
  },

  compatibilityMatrix: {
    '1.0.0': ['1.0.0', '1.1.0', '1.2.0'],
    '2.0.0': ['2.0.0', '2.1.0']
  }
}

export function resolveContractVersionPath(endpoint: string): string {
  const contractName = endpoint
    .replace('/api/v1/', '')
    .replace('/api/', '')

  return `/contracts/versions/${contractName}/active`
}

export function compareVersions(version1: string, version2: string): number {
  const v1 = version1.split('.').map(Number)
  const v2 = version2.split('.').map(Number)

  for (let i = 0; i < Math.max(v1.length, v2.length); i++) {
    const num1 = v1[i] || 0
    const num2 = v2[i] || 0

    if (num1 > num2) return 1
    if (num1 < num2) return -1
  }

  return 0
}

export function describeBreakingChanges(currentVersion: string, requiredVersion: string): string[] {
  return [`API版本${currentVersion}与所需版本${requiredVersion}不兼容`]
}

export function isVersionCompatible(current: string, required: string): boolean {
  for (const compatibleVersions of Object.values(VERSION_CONFIG.compatibilityMatrix)) {
    if (compatibleVersions.includes(required)) {
      return compatibleVersions.includes(current)
    }
  }

  return compareVersions(current, required) >= 0
}

export function normalizeEndpointDomain(endpoint: string): string {
  return endpoint
    .split('/')
    .filter(Boolean)
    .filter((segment) => segment !== 'api' && !/^v\d+$/.test(segment))
    .join('/')
}

export function findConfiguredEndpointPrefix(endpoint: string, version?: string): string | null {
  const entries = Object.entries(VERSION_CONFIG.endpoints)
    .sort(([left], [right]) => right.length - left.length)

  const match = entries.find(([prefix, configuredVersion]) => (
    endpoint.startsWith(prefix) && (!version || configuredVersion === version)
  ))

  return match?.[0] || null
}

export function normalizeApiClientEndpoint(url: string): string {
  if (/^https?:\/\//.test(url)) {
    return url
  }

  if (url.startsWith('/api/')) {
    return url
  }

  if (url.startsWith('/')) {
    return `/api${url}`
  }

  return url
}

export function toApiClientRequestUrl(endpoint: string): string {
  if (endpoint.startsWith('/api/')) {
    return endpoint.slice('/api'.length)
  }

  return endpoint
}

export function getEndpointVersion(endpoint: string, detectedVersions?: VersionLookup): string {
  const exactDetected = findVersionEntry(endpoint, detectedVersions)
  if (exactDetected) {
    return exactDetected
  }

  const prefixedDetected = findPrefixedVersionEntry(endpoint, detectedVersions)
  if (prefixedDetected) {
    return prefixedDetected
  }

  for (const [configEndpoint, version] of Object.entries(VERSION_CONFIG.endpoints)) {
    if (endpoint.startsWith(configEndpoint)) {
      return version
    }
  }

  return findVersionEntry('system', detectedVersions) || VERSION_CONFIG.supportedVersions.preferred
}

export function resolveRequiredVersion(
  apiName: string,
  requiredVersion?: string,
  detectedVersions?: VersionLookup,
): string {
  if (requiredVersion) {
    return requiredVersion
  }

  return (
    VERSION_CONFIG.endpoints[apiName] ||
    findVersionEntry(apiName, detectedVersions) ||
    getEndpointVersion(apiName, detectedVersions)
  )
}

export function calculateMigrationPath(
  apiName: string,
  targetVersion?: string,
  detectedVersions?: VersionLookup,
): VersionMigrationPath {
  const currentVersion = getEndpointVersion(apiName, detectedVersions)
  const requiredVersion = resolveRequiredVersion(apiName, targetVersion, detectedVersions)

  if (currentVersion === requiredVersion) {
    return {
      currentVersion,
      targetVersion: requiredVersion,
      isBreaking: false,
      steps: [],
    }
  }

  const compatible = isVersionCompatible(currentVersion, requiredVersion)
  return {
    currentVersion,
    targetVersion: requiredVersion,
    isBreaking: !compatible,
    steps: [
      {
        fromVersion: currentVersion,
        toVersion: requiredVersion,
        type: compatible ? 'compatible' : 'breaking',
        changes: compatible ? [] : describeBreakingChanges(currentVersion, requiredVersion),
      },
    ],
  }
}

export function adaptEndpointForVersion(endpoint: string, targetVersion: string): string {
  const currentPrefix = findConfiguredEndpointPrefix(endpoint)
  if (!currentPrefix) {
    return endpoint
  }

  const currentDomain = normalizeEndpointDomain(currentPrefix)
  const targetEntry = Object.entries(VERSION_CONFIG.endpoints)
    .sort(([left], [right]) => right.length - left.length)
    .find(([prefix, version]) => (
      version === targetVersion && normalizeEndpointDomain(prefix) === currentDomain
    ))

  if (!targetEntry || targetEntry[0] === currentPrefix) {
    return endpoint
  }

  return `${targetEntry[0]}${endpoint.slice(currentPrefix.length)}`
}

export function adaptApiRequestForVersion<TPayload = unknown>(
  endpoint: string,
  payload: TPayload,
  targetVersion?: string,
  detectedVersions?: VersionLookup,
): AdaptedApiRequest<TPayload> {
  const migrationPath = calculateMigrationPath(endpoint, targetVersion, detectedVersions)
  const headers: Record<string, string> = {
    'X-API-Version': migrationPath.targetVersion,
    'X-API-Version-From': migrationPath.currentVersion,
  }

  if (migrationPath.steps.length > 0) {
    headers['X-API-Migration-Path'] = migrationPath.steps
      .map((step) => `${step.fromVersion}->${step.toVersion}`)
      .join(',')
  }

  return {
    endpoint: adaptEndpointForVersion(endpoint, migrationPath.targetVersion),
    payload,
    headers,
    migrationPath,
  }
}

export function adaptApiClientRequestForVersion<TPayload = unknown>(
  url: string,
  payload: TPayload,
  targetVersion?: string,
  detectedVersions?: VersionLookup,
): AdaptedApiClientRequest<TPayload> {
  const endpoint = normalizeApiClientEndpoint(url)
  if (!findConfiguredEndpointPrefix(endpoint)) {
    return {
      endpoint,
      payload,
      headers: {},
      migrationPath: calculateMigrationPath(endpoint, targetVersion, detectedVersions),
      url,
    }
  }

  const adapted = adaptApiRequestForVersion(endpoint, payload, targetVersion, detectedVersions)
  return {
    ...adapted,
    url: adapted.endpoint === endpoint ? url : toApiClientRequestUrl(adapted.endpoint),
  }
}

function findVersionEntry(endpoint: string, versionLookup?: VersionLookup): string | null {
  const entry = resolveVersionEntries(versionLookup).find(([candidate]) => candidate === endpoint)
  return entry?.[1] || null
}

function findPrefixedVersionEntry(endpoint: string, versionLookup?: VersionLookup): string | null {
  const entry = resolveVersionEntries(versionLookup).find(([candidate]) => endpoint.startsWith(candidate))
  return entry?.[1] || null
}

function resolveVersionEntries(versionLookup?: VersionLookup): Array<[string, string]> {
  if (!versionLookup) {
    return []
  }

  if (isVersionEntryIterable(versionLookup)) {
    return Array.from(versionLookup)
  }

  return Object.entries(versionLookup)
}

function isVersionEntryIterable(value: VersionLookup): value is Iterable<[string, string]> {
  return typeof (value as Iterable<[string, string]>)[Symbol.iterator] === 'function'
}
