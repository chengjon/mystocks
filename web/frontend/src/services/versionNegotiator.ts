/**
 * API版本协商服务
 *
 * 负责前端与后端API版本的协商和兼容性管理
 * 包括版本检测、兼容性检查、版本切换、弃用警告等功能
 */

import { apiClient } from '@/api/apiClient'
import { ElMessage, ElNotification } from 'element-plus'

interface ApiVersion {
  name: string
  version: string
  prefix: string
  tags: string[]
  endpoints?: Record<string, string>
}

interface VersionCompatibility {
  isCompatible: boolean
  currentVersion: string
  requiredVersion: string
  breakingChanges?: string[]
  deprecationWarnings?: string[]
}

interface NegotiationResult {
  success: boolean
  selectedVersion: string
  fallbackVersion?: string
  warnings?: string[]
  errors?: string[]
}

const VERSION_CONFIG = {
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
  } as Record<string, string>,

  deprecationWarnings: {
    '0.x.x': 'API版本0.x.x已弃用，请升级到1.0.0+版本',
    '1.0.0': 'API版本1.0.0计划在未来版本中弃用，建议升级到最新版本'
  } as Record<string, string>,

  compatibilityMatrix: {
    '1.0.0': ['1.0.0', '1.1.0', '1.2.0'],
    '2.0.0': ['2.0.0', '2.1.0']
  } as Record<string, string[]>
}

class ApiVersionNegotiator {
  private detectedVersions: Map<string, string> = new Map()
  private compatibilityCache: Map<string, VersionCompatibility> = new Map()
  private negotiationHistory: NegotiationResult[] = []

  constructor() {
    this.initializeVersionDetection()
  }

  private async initializeVersionDetection(): Promise<void> {
    try {
      await this.detectSystemVersion()
      await this.detectApiVersions()

      console.log('✅ API版本检测完成', {
        detectedVersions: Object.fromEntries(this.detectedVersions),
        compatibilityCache: Object.fromEntries(this.compatibilityCache)
      })
    } catch (error) {
      console.error('❌ API版本检测失败:', error)
    }
  }

  private async detectSystemVersion(): Promise<void> {
    try {
      const response = await apiClient.get('/health')
      if (response.success && response.data?.version) {
        this.detectedVersions.set('system', response.data.version)
      }
    } catch (error) {
      console.warn('⚠️ 无法检测系统版本:', error)
      this.detectedVersions.set('system', '1.0.0')
    }
  }

  private async detectApiVersions(): Promise<void> {
    const endpoints = Object.keys(VERSION_CONFIG.endpoints)

    const versionPromises = endpoints.map(async (endpoint) => {
      try {
        const contractResponse = await apiClient.get(`/contracts/${endpoint.replace('/api/v1/', '').replace('/api/', '')}/active`)
        if (contractResponse.success && contractResponse.data?.version) {
          this.detectedVersions.set(endpoint, contractResponse.data.version)
          return { endpoint, version: contractResponse.data.version, source: 'contract' }
        }
      } catch (error) {
        const defaultVersion = VERSION_CONFIG.endpoints[endpoint]
        this.detectedVersions.set(endpoint, defaultVersion)
        return { endpoint, version: defaultVersion, source: 'config' }
      }
    })

    const results = await Promise.allSettled(versionPromises)
    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        const { endpoint, version, source } = result.value
        console.log(`📋 ${endpoint}: ${version} (${source})`)
      } else if (result.status === 'rejected') {
        const endpoint = endpoints[index]
        console.warn(`⚠️ 版本检测失败 ${endpoint}:`, result.reason)
      }
    })
  }

  public checkCompatibility(apiName: string, requiredVersion?: string): VersionCompatibility {
    const cacheKey = `${apiName}:${requiredVersion || 'auto'}`
    if (this.compatibilityCache.has(cacheKey)) {
      return this.compatibilityCache.get(cacheKey)!
    }

    const currentVersion = this.detectedVersions.get(apiName) || this.detectedVersions.get('system') || '1.0.0'
    const required = requiredVersion || VERSION_CONFIG.supportedVersions.preferred

    const compatibility: VersionCompatibility = {
      isCompatible: this.isVersionCompatible(currentVersion, required),
      currentVersion,
      requiredVersion: required,
      breakingChanges: [],
      deprecationWarnings: []
    }

    if (VERSION_CONFIG.deprecationWarnings[currentVersion]) {
      compatibility.deprecationWarnings!.push(VERSION_CONFIG.deprecationWarnings[currentVersion])
    }

    if (!compatibility.isCompatible) {
      compatibility.breakingChanges!.push(`API版本${currentVersion}与所需版本${required}不兼容`)
    }

    this.compatibilityCache.set(cacheKey, compatibility)
    return compatibility
  }

  private isVersionCompatible(current: string, required: string): boolean {
    const compatibilityMatrix = VERSION_CONFIG.compatibilityMatrix

    for (const [baseVersion, compatibleVersions] of Object.entries(compatibilityMatrix)) {
      if (compatibleVersions.includes(required)) {
        return compatibleVersions.includes(current)
      }
    }

    return this.compareVersions(current, required) >= 0
  }

  /**
   * 语义化版本比较
   */
  private compareVersions(version1: string, version2: string): number {
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

  public async negotiateVersion(apiName: string, preferredVersion?: string): Promise<NegotiationResult> {
    const result: NegotiationResult = {
      success: false,
      selectedVersion: '',
      warnings: [],
      errors: []
    }

    try {
      const compatibility = this.checkCompatibility(apiName, preferredVersion)

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

  private findFallbackVersion(apiName: string, preferredVersion: string): string | null {
    const compatibilityMatrix = VERSION_CONFIG.compatibilityMatrix

    for (const [baseVersion, compatibleVersions] of Object.entries(compatibilityMatrix)) {
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
    if (this.detectedVersions.has(endpoint)) {
      return this.detectedVersions.get(endpoint)!
    }

    for (const [apiEndpoint, version] of this.detectedVersions) {
      if (endpoint.startsWith(apiEndpoint)) {
        return version
      }
    }

    for (const [configEndpoint, version] of Object.entries(VERSION_CONFIG.endpoints)) {
      if (endpoint.startsWith(configEndpoint)) {
        return version
      }
    }

    return this.detectedVersions.get('system') || VERSION_CONFIG.supportedVersions.preferred
  }

  public getNegotiationHistory(): NegotiationResult[] {
    return [...this.negotiationHistory]
  }

  public async refreshVersions(): Promise<void> {
    this.detectedVersions.clear()
    this.compatibilityCache.clear()
    await this.initializeVersionDetection()
  }
}

export const versionNegotiator = new ApiVersionNegotiator()

export const negotiateApiVersion = (apiName: string, preferredVersion?: string) =>
  versionNegotiator.negotiateVersion(apiName, preferredVersion)

export const checkApiCompatibility = (apiName: string, requiredVersion?: string) =>
  versionNegotiator.checkCompatibility(apiName, requiredVersion)

export const getEndpointVersion = (endpoint: string) =>
  versionNegotiator.getEndpointVersion(endpoint)

export const showVersionNotifications = () =>
  versionNegotiator.showCompatibilityNotifications()

export const getVersionSummary = () =>
  versionNegotiator.getVersionSummary()

export const refreshApiVersions = () =>
  versionNegotiator.refreshVersions()

export default versionNegotiator