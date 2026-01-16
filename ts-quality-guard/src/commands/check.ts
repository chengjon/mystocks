/**
 * Command: Run quality checks
 */

import chalk from 'chalk'
import { QualityChecker } from '../core/QualityChecker'
import { ConfigManager } from '../core/ConfigManager'
import { CheckCommandOptions } from '../types'

export async function checkCommand(options: CheckCommandOptions) {
  const {
    files,
    staged = false,
    threshold = '85',
    config: configPath,
    ci = false,
    format = 'console',
    rules,
    fix = false
  } = options

  try {
    // Load configuration
    const config = await ConfigManager.loadConfig(configPath)
    const thresholdNum = parseInt(threshold.toString())

    // Determine files to check
    let filesToCheck: string[] = []
    if (files) {
      filesToCheck = files.split(',').map(f => f.trim())
    } else if (staged) {
      // TODO: Implement git staged files detection
      console.log(chalk.yellow('⚠️  Staged files checking not yet implemented'))
      filesToCheck = await getDefaultFiles()
    } else {
      filesToCheck = await getDefaultFiles()
    }

    if (filesToCheck.length === 0) {
      console.log(chalk.yellow('⚠️  No TypeScript files found to check'))
      return
    }

    console.log(chalk.blue(`🔍 Checking ${filesToCheck.length} files...`))

    // Run quality checks
    const results = await QualityChecker.runChecks(filesToCheck, {
      configPath,
      threshold: thresholdNum,
      ci,
      rules: rules ? rules.split(',') : undefined
    })

    // Display results
    displayResults(results, format, thresholdNum)

    // Exit with appropriate code
    if (!results.overall.passed) {
      process.exit(1)
    }

  } catch (error: any) {
    console.error(chalk.red('❌ Check failed:'), error.message)
    process.exit(1)
  }
}

/**
 * Get default files to check
 */
async function getDefaultFiles(): Promise<string[]> {
  const { QualityChecker } = await import('../core/QualityChecker')
  return QualityChecker['getDefaultFiles'] ? QualityChecker['getDefaultFiles']() : []
}

/**
 * Display results in specified format
 */
function displayResults(results: any, format: string, threshold: number) {
  switch (format) {
    case 'json':
      console.log(JSON.stringify(results, null, 2))
      break

    case 'markdown':
      displayMarkdownResults(results, threshold)
      break

    default:
      displayConsoleResults(results, threshold)
  }
}

/**
 * Display results in console format
 */
function displayConsoleResults(results: any, threshold: number) {
  console.log('')
  console.log(chalk.blue('📊 TypeScript Quality Report'))
  console.log('')

  // Overall score
  const overallScore = results.overall.score
  const grade = getGrade(overallScore)
  const status = overallScore >= threshold ? chalk.green('✅ PASSED') : chalk.red('❌ FAILED')

  console.log(chalk.bold(`Overall Score: ${overallScore}/100 (${grade}) ${status}`))
  console.log('')

  // Individual checks
  console.log(chalk.blue('📋 Check Results:'))
  console.log(`  TypeScript: ${formatScore(results.typescript)}`)
  console.log(`  ESLint:     ${formatScore(results.eslint)}`)
  console.log(`  Custom:     ${formatScore(results.custom)}`)
  console.log('')

  // Issues summary
  const totalErrors = results.typescript.errors + results.eslint.errors + results.custom.errors
  const totalWarnings = results.typescript.warnings + results.eslint.warnings + results.custom.warnings

  if (totalErrors > 0 || totalWarnings > 0) {
    console.log(chalk.blue('🚨 Issues Summary:'))
    if (totalErrors > 0) {
      console.log(chalk.red(`  Errors: ${totalErrors}`))
    }
    if (totalWarnings > 0) {
      console.log(chalk.yellow(`  Warnings: ${totalWarnings}`))
    }
    console.log('')

    // Show top issues
    const allIssues = [
      ...results.typescript.details,
      ...results.eslint.details,
      ...results.custom.details
    ].slice(0, 5)

    if (allIssues.length > 0) {
      console.log(chalk.blue('🔍 Top Issues:'))
      allIssues.forEach(issue => {
        const severity = issue.severity === 'error' ? chalk.red('❌') : chalk.yellow('⚠️')
        console.log(`  ${severity} ${issue.file}:${issue.line} ${issue.message}`)
      })
    }
  } else {
    console.log(chalk.green('🎉 No issues found!'))
  }
}

/**
 * Display results in markdown format
 */
function displayMarkdownResults(results: any, threshold: number) {
  const overallScore = results.overall.score
  const grade = getGrade(overallScore)
  const status = overallScore >= threshold ? '✅ PASSED' : '❌ FAILED'

  console.log('# 🔍 TypeScript Quality Report')
  console.log('')
  console.log(`**Overall Score:** ${overallScore}/100 (${grade}) ${status}`)
  console.log('')

  console.log('## 📋 Check Results')
  console.log('')
  console.log('| Check | Score | Status | Errors | Warnings |')
  console.log('|-------|-------|--------|--------|----------|')
  console.log(`| TypeScript | ${results.typescript.score}/100 | ${results.typescript.passed ? '✅' : '❌'} | ${results.typescript.errors} | ${results.typescript.warnings} |`)
  console.log(`| ESLint | ${results.eslint.score}/100 | ${results.eslint.passed ? '✅' : '❌'} | ${results.eslint.errors} | ${results.eslint.warnings} |`)
  console.log(`| Custom | ${results.custom.score}/100 | ${results.custom.passed ? '✅' : '❌'} | ${results.custom.errors} | ${results.custom.warnings} |`)
  console.log('')

  const allIssues = [
    ...results.typescript.details,
    ...results.eslint.details,
    ...results.custom.details
  ]

  if (allIssues.length > 0) {
    console.log('## 🚨 Issues')
    console.log('')
    allIssues.slice(0, 10).forEach(issue => {
      const severity = issue.severity === 'error' ? '❌' : '⚠️'
      console.log(`- ${severity} **${issue.file}:${issue.line}** ${issue.message}`)
    })

    if (allIssues.length > 10) {
      console.log(`- ... and ${allIssues.length - 10} more issues`)
    }
  } else {
    console.log('## 🎉 No Issues Found')
    console.log('')
    console.log('All quality checks passed successfully!')
  }
}

/**
 * Format score with color
 */
function formatScore(result: any): string {
  const score = `${result.score}/100`
  const status = result.passed ? chalk.green('✅') : chalk.red('❌')
  const issues = chalk.gray(`(${result.errors} errors, ${result.warnings} warnings)`)
  return `${score} ${status} ${issues}`
}

/**
 * Get grade from score
 */
function getGrade(score: number): string {
  if (score >= 95) return 'A+'
  if (score >= 90) return 'A'
  if (score >= 85) return 'B+'
  if (score >= 80) return 'B'
  if (score >= 75) return 'C+'
  if (score >= 70) return 'C'
  if (score >= 60) return 'D'
  return 'F'
}
