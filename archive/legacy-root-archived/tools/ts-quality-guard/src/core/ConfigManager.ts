/**
 * Configuration Manager
 * Handles loading, validating, and managing quality guard configurations
 */

import * as fs from 'fs-extra'
import * as path from 'path'
import { QualityConfig, ProjectConfig, StandardsConfig, ChecklistsConfig, GatesConfig, MonitoringConfig, NotificationsConfig } from '../types'

export class ConfigManager {
  private static readonly CONFIG_FILE = '.ts-quality-guard.json'
  private static readonly DEFAULT_CONFIG: QualityConfig = {
    version: '1.0.0',
    project: {
      name: 'unknown',
      type: 'vue-frontend',
      framework: 'vue3',
      typescript: '4.9+'
    },
    standards: {
      strict: true,
      noImplicitAny: true,
      exactOptionalPropertyTypes: true,
      noUnusedLocals: false,
      noUnusedParameters: false,
      namingConvention: 'camelCase',
      apiCase: 'snake_case',
      maxFileLines: 300,
      maxFunctionLines: 50,
      requiredJSDoc: true
    },
    checklists: {
      component: ['props-interface', 'emits-definition', 'label-required'],
      adapter: ['explicit-types', 'error-handling', 'data-validation'],
      service: ['api-contract', 'response-typing', 'error-boundaries'],
      store: ['pinia-best-practices', 'type-safe-mutations']
    },
    gates: {
      preCommit: {
        enabled: true,
        threshold: 85,
        blockOnError: true,
        allowWarnings: true,
        autoFix: false
      },
      prePush: {
        enabled: true,
        threshold: 80,
        blockOnError: false,
        allowWarnings: true
      },
      ci: {
        enabled: true,
        threshold: 90,
        failOnWarning: false,
        reportFormat: 'junit'
      }
    },
    monitoring: {
      enabled: true,
      realTime: true,
      idePlugin: true,
      feedbackLevel: 'warnings',
      debounceMs: 500,
      maxConcurrentFiles: 10,
      cacheEnabled: true,
      cacheSize: 100,
      reportFrequency: 'daily'
    },
    notifications: {
      enabled: false,
      channels: {}
    }
  }

  /**
   * Load configuration from file
   */
  static async loadConfig(configPath?: string): Promise<QualityConfig> {
    const filePath = configPath || this.CONFIG_FILE

    try {
      if (await fs.pathExists(filePath)) {
        const configData = await fs.readJson(filePath)
        return this.mergeWithDefaults(configData)
      }
    } catch (error) {
      console.warn(`Warning: Failed to load config from ${filePath}:`, (error as Error).message)
    }

    return this.DEFAULT_CONFIG
  }

  /**
   * Save configuration to file
   */
  static async saveConfig(config: QualityConfig, configPath?: string): Promise<void> {
    const filePath = configPath || this.CONFIG_FILE
    await fs.writeJson(filePath, config, { spaces: 2 })
  }

  /**
   * Create default configuration for a project
   */
  static async createDefaultConfig(projectType?: string): Promise<QualityConfig> {
    const config = { ...this.DEFAULT_CONFIG }

    if (projectType) {
      config.project = this.detectProjectConfig(projectType)
    } else {
      config.project = await this.autoDetectProjectConfig()
    }

    return config
  }

  /**
   * Validate configuration
   */
  static validateConfig(config: QualityConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    // Version validation
    if (!config.version) {
      errors.push('Missing version field')
    }

    // Project validation
    if (!config.project?.name) {
      errors.push('Missing project.name')
    }
    if (!['vue-frontend', 'react-app', 'node-api', 'angular-app', 'library'].includes(config.project?.type)) {
      errors.push('Invalid project.type')
    }

    // Standards validation
    if (typeof config.standards?.strict !== 'boolean') {
      errors.push('standards.strict must be boolean')
    }
    if (config.standards?.maxFileLines && config.standards.maxFileLines < 100) {
      errors.push('standards.maxFileLines too low')
    }

    // Gates validation
    if (config.gates?.preCommit?.threshold && (config.gates.preCommit.threshold < 0 || config.gates.preCommit.threshold > 100)) {
      errors.push('gates.preCommit.threshold must be between 0-100')
    }

    return {
      valid: errors.length === 0,
      errors
    }
  }

  /**
   * Auto-detect project configuration
   */
  private static async autoDetectProjectConfig(): Promise<ProjectConfig> {
    const packageJsonPath = path.join(process.cwd(), 'package.json')
    const tsconfigPath = path.join(process.cwd(), 'tsconfig.json')

    let packageJson: any = {}
    let tsconfig: any = {}

    try {
      if (await fs.pathExists(packageJsonPath)) {
        packageJson = await fs.readJson(packageJsonPath)
      }
      if (await fs.pathExists(tsconfigPath)) {
        tsconfig = await fs.readJson(tsconfigPath)
      }
    } catch (error) {
      // Ignore errors, use defaults
    }

    return this.inferProjectConfig(packageJson, tsconfig)
  }

  /**
   * Detect project config based on type
   */
  private static detectProjectConfig(projectType: string): ProjectConfig {
    const baseConfig: ProjectConfig = {
      name: 'unknown',
      type: projectType as any,
      framework: 'vanilla',
      typescript: '4.9+'
    }

    switch (projectType) {
      case 'vue-frontend':
        return {
          ...baseConfig,
          type: 'vue-frontend',
          framework: 'vue3',
          typescript: '4.9+',
          styling: 'element-plus',
          state: 'pinia',
          api: 'axios'
        }
      case 'react-app':
        return {
          ...baseConfig,
          type: 'react-app',
          framework: 'react',
          typescript: '4.9+',
          styling: 'styled-components',
          state: 'zustand',
          api: 'axios'
        }
      case 'node-api':
        return {
          ...baseConfig,
          type: 'node-api',
          framework: 'node',
          typescript: '4.9+',
          api: 'axios'
        }
      default:
        return baseConfig
    }
  }

  /**
   * Infer project config from package.json and tsconfig.json
   */
  private static inferProjectConfig(packageJson: any, tsconfig: any): ProjectConfig {
    const deps = packageJson.dependencies || {}
    const devDeps = packageJson.devDependencies || {}

    let framework: ProjectConfig['framework'] = 'vanilla'
    let type: ProjectConfig['type'] = 'library'
    let styling: ProjectConfig['styling']
    let state: ProjectConfig['state']
    let api: ProjectConfig['api']

    // Detect framework
    if (deps.vue) {
      framework = 'vue3'
      type = 'vue-frontend'
      if (deps['@element-plus/icons-vue']) styling = 'element-plus'
      if (deps.pinia) state = 'pinia'
      if (deps.vuex) state = 'vuex'
    } else if (deps.react) {
      framework = 'react'
      type = 'react-app'
      if (deps['styled-components']) styling = 'styled-components'
      if (deps.zustand) state = 'zustand'
      if (deps.redux) state = 'redux'
    } else if (deps.express || deps.fastify) {
      framework = 'node'
      type = 'node-api'
    }

    // Detect API client
    if (deps.axios) api = 'axios'
    else if (deps['@apollo/client']) api = 'apollo'

    // Detect TypeScript version
    const tsVersion = devDeps.typescript || '4.9+'

    return {
      name: packageJson.name || 'unknown',
      type,
      framework,
      typescript: tsVersion,
      styling,
      state,
      api
    }
  }

  /**
   * Merge user config with defaults
   */
  private static mergeWithDefaults(userConfig: Partial<QualityConfig>): QualityConfig {
    return {
      ...this.DEFAULT_CONFIG,
      ...userConfig,
      project: { ...this.DEFAULT_CONFIG.project, ...userConfig.project },
      standards: { ...this.DEFAULT_CONFIG.standards, ...userConfig.standards },
      checklists: { ...this.DEFAULT_CONFIG.checklists, ...userConfig.checklists },
      gates: { ...this.DEFAULT_CONFIG.gates, ...userConfig.gates },
      monitoring: { ...this.DEFAULT_CONFIG.monitoring, ...userConfig.monitoring },
      notifications: { ...this.DEFAULT_CONFIG.notifications, ...userConfig.notifications }
    }
  }
}
