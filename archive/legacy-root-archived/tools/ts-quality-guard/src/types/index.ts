/**
 * TypeScript Quality Configuration Types
 */

export interface ProjectConfig {
  name: string
  type: 'vue-frontend' | 'react-app' | 'node-api' | 'angular-app' | 'library'
  framework: 'vue3' | 'react' | 'angular' | 'node' | 'vanilla'
  typescript: string
  styling?: 'css-modules' | 'tailwind' | 'element-plus' | 'material-ui' | 'styled-components'
  state?: 'pinia' | 'vuex' | 'zustand' | 'redux' | 'context'
  api?: 'axios' | 'fetch' | 'apollo' | 'react-query'
}

export interface StandardsConfig {
  strict: boolean
  noImplicitAny: boolean
  exactOptionalPropertyTypes: boolean
  noUnusedLocals: boolean
  noUnusedParameters: boolean
  namingConvention: 'camelCase' | 'PascalCase' | 'snake_case'
  apiCase: 'snake_case' | 'camelCase'
  maxFileLines: number
  maxFunctionLines: number
  requiredJSDoc: boolean
}

export interface ChecklistsConfig {
  component: string[]
  adapter: string[]
  service: string[]
  store: string[]
}

export interface GatesConfig {
  preCommit: {
    enabled: boolean
    threshold: number
    blockOnError: boolean
    allowWarnings: boolean
    autoFix: boolean
  }
  prePush: {
    enabled: boolean
    threshold: number
    blockOnError: boolean
    allowWarnings: boolean
  }
  ci: {
    enabled: boolean
    threshold: number
    failOnWarning: boolean
    reportFormat: 'json' | 'markdown' | 'junit'
  }
}

export interface MonitoringConfig {
  enabled: boolean
  realTime: boolean
  idePlugin: boolean
  feedbackLevel: 'silent' | 'summary' | 'errors' | 'warnings' | 'verbose'
  debounceMs: number
  maxConcurrentFiles: number
  cacheEnabled: boolean
  cacheSize: number
  reportFrequency: 'daily' | 'weekly' | 'never'
}

export interface NotificationsConfig {
  enabled: boolean
  channels: {
    slack?: {
      webhook: string
      channel: string
      username: string
      icon: string
      notifyOnFailure: boolean
      notifyOnSuccess: boolean
      notifyOnWarning: boolean
    }
    email?: {
      smtp: {
        host: string
        port: number
        secure: boolean
        auth: {
          user: string
          pass: string
        }
      }
      from: string
      to: string[]
      subject: string
      notifyOnFailure: boolean
    }
    webhook?: {
      url: string
      method: 'GET' | 'POST' | 'PUT'
      headers: Record<string, string>
      notifyOnFailure: boolean
    }
  }
}

export interface QualityConfig {
  version: string
  project: ProjectConfig
  standards: StandardsConfig
  checklists: ChecklistsConfig
  gates: GatesConfig
  monitoring: MonitoringConfig
  notifications: NotificationsConfig
}

/**
 * Check Results Types
 */
export interface CheckResult {
  type: 'typescript' | 'eslint' | 'custom'
  score: number
  passed: boolean
  errors: number
  warnings: number
  details: CheckDetail[]
}

export interface CheckDetail {
  file: string
  line: number
  column: number
  message: string
  severity: 'error' | 'warning' | 'info'
  rule?: string
  fix?: {
    description: string
    changes: TextEdit[]
  }
}

export interface TextEdit {
  start: { line: number; character: number }
  end: { line: number; character: number }
  newText: string
}

export interface CheckResults {
  typescript: CheckResult
  eslint: CheckResult
  custom: CheckResult
  overall: {
    score: number
    passed: boolean
  }
}

/**
 * Command Options Types
 */
export interface CheckCommandOptions {
  files?: string
  staged?: boolean
  threshold?: string
  config?: string
  ci?: boolean
  format?: 'console' | 'json' | 'markdown' | 'junit'
  rules?: string
  fix?: boolean
}

export interface InitCommandOptions {
  force?: boolean
  projectType?: string
}

export interface StandardsCommandOptions {
  projectType?: string
  output?: string
  config?: string
}

export interface WatchCommandOptions {
  dir?: string
  port?: string
  ide?: 'vscode' | 'webstorm'
  config?: string
}

export interface InstallHooksCommandOptions {
  only?: string
  config?: string
}

export interface ValidateConfigCommandOptions {
  config?: string
  verbose?: boolean
}
