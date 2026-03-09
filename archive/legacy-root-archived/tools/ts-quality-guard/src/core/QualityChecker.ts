/**
 * Quality Checker Engine
 * Core engine for running TypeScript quality checks
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import * as fs from 'fs-extra'
import * as path from 'path'
import { glob } from 'glob'
import { CheckResults, CheckResult, CheckDetail } from '../types'

const execAsync = promisify(exec)

export class QualityChecker {
  /**
   * Run comprehensive quality checks
   */
  static async runChecks(
    files: string[] = [],
    options: {
      configPath?: string
      threshold?: number
      ci?: boolean
      rules?: string[]
    } = {}
  ): Promise<CheckResults> {
    const { configPath, threshold = 85, ci = false, rules = ['typescript', 'eslint', 'custom'] } = options

    // Get files to check
    const filesToCheck = files.length > 0 ? files : await this.getDefaultFiles()

    // Run checks in parallel
    const checks = await Promise.allSettled([
      rules.includes('typescript') ? this.runTypeScriptCheck(filesToCheck, { ci }) : Promise.resolve(this.createEmptyResult('typescript')),
      rules.includes('eslint') ? this.runESLintCheck(filesToCheck, { ci }) : Promise.resolve(this.createEmptyResult('eslint')),
      rules.includes('custom') ? this.runCustomChecks(filesToCheck) : Promise.resolve(this.createEmptyResult('custom'))
    ])

    // Process results
    const results: CheckResults = {
      typescript: this.extractResult(checks[0], 'typescript'),
      eslint: this.extractResult(checks[1], 'eslint'),
      custom: this.extractResult(checks[2], 'custom'),
      overall: { score: 0, passed: false }
    }

    // Calculate overall score
    const totalScore = results.typescript.score + results.eslint.score + results.custom.score
    results.overall.score = Math.round(totalScore / 3)
    results.overall.passed = results.overall.score >= threshold

    return results
  }

  /**
   * Run TypeScript compilation check
   */
  private static async runTypeScriptCheck(
    files: string[],
    options: { ci?: boolean } = {}
  ): Promise<CheckResult> {
    try {
      const { ci = false } = options

      // Check if vue-tsc is available (for Vue projects)
      const hasVueTsc = await this.checkCommandExists('vue-tsc')
      const command = hasVueTsc ? 'vue-tsc --noEmit' : 'tsc --noEmit'

      const { stdout, stderr } = await execAsync(command, { cwd: process.cwd() })

      // Parse TypeScript errors
      const errors = this.parseTypeScriptErrors(stderr)
      const score = Math.max(0, 100 - (errors.length * 5)) // Each error reduces score by 5

      return {
        type: 'typescript',
        score: Math.min(100, score),
        passed: errors.length === 0 || (!ci && errors.length < 10),
        errors: errors.length,
        warnings: 0,
        details: errors
      }
    } catch (error: any) {
      // Parse errors from stderr even if command failed
      const errors = this.parseTypeScriptErrors(error.stderr || '')
      return {
        type: 'typescript',
        score: 0,
        passed: false,
        errors: errors.length,
        warnings: 0,
        details: errors
      }
    }
  }

  /**
   * Run ESLint check
   */
  private static async runESLintCheck(
    files: string[],
    options: { ci?: boolean } = {}
  ): Promise<CheckResult> {
    try {
      const { ci = false } = options

      // Check if ESLint is available
      const hasEslint = await this.checkCommandExists('eslint')
      if (!hasEslint) {
        return this.createEmptyResult('eslint')
      }

      const fileArgs = files.length > 0 ? files.join(' ') : '.'
      const { stdout, stderr } = await execAsync(`eslint --format json ${fileArgs}`, { cwd: process.cwd() })

      const results = JSON.parse(stdout)
      const errors = this.flattenESLintResults(results, 'error')
      const warnings = this.flattenESLintResults(results, 'warning')

      const score = Math.max(0, 100 - (errors.length * 3) - (warnings.length * 1))

      return {
        type: 'eslint',
        score: Math.min(100, score),
        passed: errors.length === 0 || (!ci && errors.length < 5),
        errors: errors.length,
        warnings: warnings.length,
        details: [...errors, ...warnings]
      }
    } catch (error: any) {
      // Try to parse JSON error output
      try {
        const results = JSON.parse(error.stdout || '[]')
        const errors = this.flattenESLintResults(results, 'error')
        const warnings = this.flattenESLintResults(results, 'warning')

        return {
          type: 'eslint',
          score: Math.max(0, 100 - (errors.length * 3) - (warnings.length * 1)),
          passed: errors.length === 0,
          errors: errors.length,
          warnings: warnings.length,
          details: [...errors, ...warnings]
        }
      } catch {
        return {
          type: 'eslint',
          score: 0,
          passed: false,
          errors: 1,
          warnings: 0,
          details: [{
            file: 'unknown',
            line: 1,
            column: 1,
            message: 'ESLint execution failed',
            severity: 'error'
          }]
        }
      }
    }
  }

  /**
   * Run custom quality checks
   */
  private static async runCustomChecks(files: string[]): Promise<CheckResult> {
    const issues: CheckDetail[] = []

    // Check for common issues
    for (const file of files) {
      if (!file.endsWith('.ts') && !file.endsWith('.tsx') && !file.endsWith('.vue')) continue

      try {
        const content = await fs.readFile(file, 'utf-8')
        const fileIssues = await this.checkFileContent(file, content)
        issues.push(...fileIssues)
      } catch (error) {
        // Skip files that can't be read
      }
    }

    const score = Math.max(0, 100 - (issues.length * 2))
    return {
      type: 'custom',
      score: Math.min(100, score),
      passed: issues.filter(i => i.severity === 'error').length === 0,
      errors: issues.filter(i => i.severity === 'error').length,
      warnings: issues.filter(i => i.severity === 'warning').length,
      details: issues
    }
  }

  /**
   * Check individual file content for quality issues
   */
  private static async checkFileContent(filePath: string, content: string): Promise<CheckDetail[]> {
    const issues: CheckDetail[] = []
    const lines = content.split('\n')

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const lineNumber = i + 1

      // Check for common issues
      if (line.includes(': any') && !line.includes('//')) {
        issues.push({
          file: filePath,
          line: lineNumber,
          column: line.indexOf(': any') + 1,
          message: 'Avoid using "any" type - use specific types instead',
          severity: 'warning',
          rule: 'no-any'
        })
      }

      // Check for console.log in production code
      if (line.includes('console.log') && !line.includes('//')) {
        issues.push({
          file: filePath,
          line: lineNumber,
          column: line.indexOf('console.log') + 1,
          message: 'Avoid console.log in production code',
          severity: 'warning',
          rule: 'no-console'
        })
      }

      // Check for TODO comments
      if (line.toLowerCase().includes('todo') && line.includes('//')) {
        issues.push({
          file: filePath,
          line: lineNumber,
          column: line.indexOf('TODO') + 1,
          message: 'TODO comment found - consider addressing it',
          severity: 'info',
          rule: 'todo-comments'
        })
      }
    }

    return issues
  }

  /**
   * Get default files to check
   */
  private static async getDefaultFiles(): Promise<string[]> {
    const patterns = [
      'src/**/*.{ts,tsx,vue}',
      'lib/**/*.{ts,tsx}',
      'packages/*/src/**/*.{ts,tsx,vue}'
    ]

    const files: string[] = []
    for (const pattern of patterns) {
      const matches = await glob(pattern, { cwd: process.cwd() })
      files.push(...matches)
    }

    return Array.from(new Set(files))
  }

  /**
   * Parse TypeScript compilation errors
   */
  private static parseTypeScriptErrors(output: string): CheckDetail[] {
    const errors: CheckDetail[] = []
    const lines = output.split('\n')

    for (const line of lines) {
      // Match TypeScript error format: file(line,column): error TS#### message
      const match = line.match(/^(.+)\((\d+),(\d+)\):\s+(error|warning)\s+TS(\d+)\s+(.+)$/)
      if (match) {
        const [, file, lineNum, colNum, severity, code, message] = match
        errors.push({
          file: path.relative(process.cwd(), file),
          line: parseInt(lineNum),
          column: parseInt(colNum),
          message,
          severity: severity as 'error' | 'warning',
          rule: `TS${code}`
        })
      }
    }

    return errors
  }

  /**
   * Flatten ESLint results
   */
  private static flattenESLintResults(results: any[], severity: string): CheckDetail[] {
    const details: CheckDetail[] = []

    for (const result of results) {
      for (const message of result.messages || []) {
        if (message.severity === (severity === 'error' ? 2 : 1)) {
          details.push({
            file: path.relative(process.cwd(), result.filePath),
            line: message.line,
            column: message.column,
            message: message.message,
            severity: severity as 'error' | 'warning',
            rule: message.ruleId
          })
        }
      }
    }

    return details
  }

  /**
   * Check if command exists
   */
  private static async checkCommandExists(command: string): Promise<boolean> {
    try {
      await execAsync(`which ${command}`)
      return true
    } catch {
      return false
    }
  }

  /**
   * Create empty result
   */
  private static createEmptyResult(type: 'typescript' | 'eslint' | 'custom'): CheckResult {
    return {
      type,
      score: 100,
      passed: true,
      errors: 0,
      warnings: 0,
      details: []
    }
  }

  /**
   * Extract result from PromiseSettledResult
   */
  private static extractResult(
    result: PromiseSettledResult<CheckResult>,
    type: 'typescript' | 'eslint' | 'custom'
  ): CheckResult {
    if (result.status === 'fulfilled') {
      return result.value
    } else {
      return {
        type,
        score: 0,
        passed: false,
        errors: 1,
        warnings: 0,
        details: [{
          file: 'unknown',
          line: 1,
          column: 1,
          message: `Check execution failed: ${result.reason}`,
          severity: 'error'
        }]
      }
    }
  }
}
