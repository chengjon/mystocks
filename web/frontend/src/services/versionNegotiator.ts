/**
 * API版本协商服务
 *
 * 负责前端与后端API版本的协商和兼容性管理
 * 包括版本检测、兼容性检查、版本切换、弃用警告等功能
 */

import { ElNotification } from 'element-plus'
import { apiClient } from '@/api/apiClient.ts'
import {
  VERSION_CONFIG,
  adaptApiRequestForVersion as adaptVersionedApiRequest,
  calculateMigrationPath as calculateVersionMigrationPath,
  describeBreakingChanges,
  getEndpointVersion as getPolicyEndpointVersion,
  isVersionCompatible,
  resolveContractVersionPath,
  resolveRequiredVersion,
  type AdaptedApiRequest,
  type VersionCompatibility,
  type VersionMigrationPath,
} from './versionNegotiationPolicy.ts'

export {
  resolveContractVersionPath,
}

export type {
  AdaptedApiRequest,
  VersionCompatibility,
  VersionMigrationPath,
  VersionMigrationStep,
} from './versionNegotiationPolicy.ts'

interface _ApiVersion {
  name: string
  version: string
  prefix: string
  tags: string[]
  endpoints?: Record<string, string>
}

interface NegotiationResult {
  success: boolean
  selectedVersion: string
  fallbackVersion?: string
  warnings?: string[]
  errors?: string[]
  migrationPath?: VersionMigrationPath
}

interface VersionDetectionOptions {
  probeContracts?: boolean
}

class ApiVersionNegotiator {
  private detectedVersions: Map<string, string> = new Map()
  private compatibilityCache: Map<string, VersionCompatibility> = new Map()
  private negotiationHistory: NegotiationResult[] = []

  constructor() {
    this.seedDefaultEndpointVersions()
    this.initializeVersionDetection()
  }

  private seedDefaultEndpointVersions(): void {
    for (const [endpoint, version] of Object.entries(VERSION_CONFIG.endpoints)) {
      this.detectedVersions.set(endpoint, version)
    }
  }

  private async initializeVersionDetection(options: VersionDetectionOptions = {}): Promise<void> {
    try {
      await this.detectSystemVersion()
      if (options.probeContracts) {
        await this.detectApiVersions()
      }
    } catch (error) {
      console.error('❌ API版本检测失败:', error)
    }
  }

  private async detectSystemVersion(): Promise<void> {
    try {
      const response = await apiClient.get('/health')
      const data = response.data as Record<string, unknown> | undefined
      if (response.success && data?.version) {
        this.detectedVersions.set('system', String(data.version))
      }
    } catch (error) {
      console.warn('⚠️ 无法检测系统版本:', error)
      this.detectedVersions.set('system', '1.0.0')
    }
  }

  private async detectApiVersions(): Promise<void> {
    const endpoints = Object.keys(VERSION_CONFIG.endpoints)

    const versionPromises = endpoints.map(async (endpoint) => {
      const defaultVersion = VERSION_CONFIG.endpoints[endpoint]

      try {
        const contractResponse = await apiClient.get(resolveContractVersionPath(endpoint))
        const data = contractResponse.data as Record<string, unknown> | undefined

        if (contractResponse.success && data?.version) {
          this.detectedVersions.set(endpoint, String(data.version))
          return { endpoint, version: String(data.version), source: 'contract' }
        }
      } catch (_error) {
        // Fall through to config-backed default below.
      }

      this.detectedVersions.set(endpoint, defaultVersion)
      return { endpoint, version: defaultVersion, source: 'config' }
    })

    const results = await Promise.allSettled(versionPromises)
    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        void result.value
      } else if (result.status === 'rejected') {
        const endpoint = endpoints[index]
        console.warn(`⚠️ 版本检测失败 ${endpoint}:`, result.reason)
      }
    })
  }

  private resolveRequiredVersion(apiName: string, requiredVersion?: string): string {
    return resolveRequiredVersion(apiName, requiredVersion, this.detectedVersions)
  }

  private describeBreakingChanges(currentVersion: string, requiredVersion: string): string[] {
    return describeBreakingChanges(currentVersion, requiredVersion)
  }

  public checkCompatibility(apiName: string, requiredVersion?: string): VersionCompatibility {
    const cacheKey = `${apiName}:${requiredVersion || 'auto'}`
    const cachedCompatibility = this.compatibilityCache.get(cacheKey)
    if (cachedCompatibility) {
      return cachedCompatibility
    }

    const currentVersion = getPolicyEndpointVersion(apiName, this.detectedVersions)
    const required = this.resolveRequiredVersion(apiName, requiredVersion)

    const compatibility: VersionCompatibility = {
      isCompatible: this.isVersionCompatible(currentVersion, required),
      currentVersion,
      requiredVersion: required,
      breakingChanges: [],
      deprecationWarnings: []
    }

    if (VERSION_CONFIG.deprecationWarnings[currentVersion] && compatibility.deprecationWarnings) {
      compatibility.deprecationWarnings.push(VERSION_CONFIG.deprecationWarnings[currentVersion])
    }

    if (!compatibility.isCompatible && compatibility.breakingChanges) {
      compatibility.breakingChanges.push(...this.describeBreakingChanges(currentVersion, required))
    }

    this.compatibilityCache.set(cacheKey, compatibility)
    return compatibility
  }

  private isVersionCompatible(current: string, required: string): boolean {
    return isVersionCompatible(current, required)
  }

  public calculateMigrationPath(apiName: string, targetVersion?: string): VersionMigrationPath {
    return calculateVersionMigrationPath(apiName, targetVersion, this.detectedVersions)
  }

  public async negotiateVersion(apiName: string, preferredVersion?: string): Promise<NegotiationResult> {
    const result: NegotiationResult = {
      success: false,
      selectedVersion: '',
      warnings: [],
      errors: []
    }

    try {
      const compatibility = this.checkCompatibility(apiName, preferredVersion)
      result.migrationPath = this.calculateMigrationPath(apiName, preferredVersion)

      if (compatibility.isCompatible) {
        result.success = true
        result.selectedVersion = compatibility.currentVersion

        if (compatibility.deprecationWarnings && compatibility.deprecationWarnings.length > 0) {
          result.warnings = compatibility.deprecationWarnings
        }
      } else {
        const fallbackVersion = this.findFallbackVersion(apiName, preferredVersion || VERSION_CONFIG.supportedVersions.preferred)

        if (fallbackVersion) {
          result.success = true
          result.selectedVersion = fallbackVersion
          result.fallbackVersion = fallbackVersion
          result.warnings = [`使用回退版本${fallbackVersion}代替请求版本${preferredVersion || VERSION_CONFIG.supportedVersions.preferred}`]
        } else {
          result.errors = [`无法找到与${apiName}兼容的版本`]
        }
      }
    } catch (error) {
      result.errors = [`版本协商失败: ${error instanceof Error ? error.message : String(error)}`]
    }

    this.negotiationHistory.push(result)
    return result
  }

  public adaptRequestForVersion<TPayload = unknown>(
    endpoint: string,
    payload: TPayload,
    targetVersion?: string,
  ): AdaptedApiRequest<TPayload> {
    return adaptVersionedApiRequest(endpoint, payload, targetVersion, this.detectedVersions)
  }

  private findFallbackVersion(apiName: string, preferredVersion: string): string | null {
    const compatibilityMatrix = VERSION_CONFIG.compatibilityMatrix

    for (const [_baseVersion, compatibleVersions] of Object.entries(compatibilityMatrix)) {
      if (compatibleVersions.includes(preferredVersion)) {
        const currentVersion = this.detectedVersions.get(apiName)
        if (currentVersion && compatibleVersions.includes(currentVersion)) {
          return currentVersion
        }
        return compatibleVersions[compatibleVersions.length - 1]
      }
    }

    return null
  }

  public getVersionSummary(): {
    systemVersion: string
    supportedVersions: typeof VERSION_CONFIG.supportedVersions
    detectedVersions: Record<string, string>
    compatibilityStatus: Record<string, VersionCompatibility>
  } {
    const compatibilityStatus: Record<string, VersionCompatibility> = {}

    for (const [apiName] of this.detectedVersions) {
      compatibilityStatus[apiName] = this.checkCompatibility(apiName)
    }

    return {
      systemVersion: this.detectedVersions.get('system') || 'unknown',
      supportedVersions: VERSION_CONFIG.supportedVersions,
      detectedVersions: Object.fromEntries(this.detectedVersions),
      compatibilityStatus
    }
  }

  public showCompatibilityNotifications(): void {
    const summary = this.getVersionSummary()

    for (const [apiName, compatibility] of Object.entries(summary.compatibilityStatus)) {
      if (compatibility.deprecationWarnings && compatibility.deprecationWarnings.length > 0) {
        ElNotification({
          title: 'API版本弃用警告',
          message: `${apiName}: ${compatibility.deprecationWarnings.join(', ')}`,
          type: 'warning',
          duration: 5000
        })
      }

      if (!compatibility.isCompatible) {
        ElNotification({
          title: 'API版本不兼容',
          message: `${apiName}: 当前版本${compatibility.currentVersion}与所需版本${compatibility.requiredVersion}不兼容`,
          type: 'error',
          duration: 10000
        })
      }
    }
  }

  public getEndpointVersion(endpoint: string): string {
    return getPolicyEndpointVersion(endpoint, this.detectedVersions)
  }

  public getNegotiationHistory(): NegotiationResult[] {
    return [...this.negotiationHistory]
  }

  public async refreshVersions(): Promise<void> {
    this.detectedVersions.clear()
    this.compatibilityCache.clear()
    this.seedDefaultEndpointVersions()
    await this.initializeVersionDetection({ probeContracts: true })
  }
}

export const versionNegotiator = new ApiVersionNegotiator()

export const negotiateApiVersion = (
  apiName: string,
  preferredVersion?: string
): Promise<NegotiationResult> =>
  versionNegotiator.negotiateVersion(apiName, preferredVersion)

export const checkApiCompatibility = (
  apiName: string,
  requiredVersion?: string
): VersionCompatibility =>
  versionNegotiator.checkCompatibility(apiName, requiredVersion)

export const calculateApiMigrationPath = (
  apiName: string,
  targetVersion?: string,
): VersionMigrationPath =>
  versionNegotiator.calculateMigrationPath(apiName, targetVersion)

export const adaptApiRequestForVersion = <TPayload = unknown>(
  endpoint: string,
  payload: TPayload,
  targetVersion?: string,
): AdaptedApiRequest<TPayload> =>
  versionNegotiator.adaptRequestForVersion(endpoint, payload, targetVersion)

export const getEndpointVersion = (endpoint: string): string =>
  versionNegotiator.getEndpointVersion(endpoint)

export const showVersionNotifications = (): void =>
  versionNegotiator.showCompatibilityNotifications()

export const getVersionSummary = (): ReturnType<ApiVersionNegotiator['getVersionSummary']> =>
  versionNegotiator.getVersionSummary()

export const refreshApiVersions = (): Promise<void> =>
  versionNegotiator.refreshVersions()

export default versionNegotiator
