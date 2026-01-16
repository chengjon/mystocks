#!/usr/bin/env node

/**
 * TypeScript Quality Guard - CLI Entry Point
 *
 * Comprehensive TypeScript quality assurance system
 * From prevention to validation, ensuring code quality at every stage
 */

import { Command } from 'commander'
import chalk from 'chalk'
import * as fs from 'fs-extra'

// Result display functions
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

function displayConsoleResults(results: any, threshold: number) {
  console.log('')
  console.log(chalk.blue('📊 TypeScript Quality Report'))

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

function formatScore(result: any): string {
  const score = `${result.score}/100`
  const status = result.passed ? chalk.green('✅') : chalk.red('❌')
  const issues = chalk.gray(`(${result.errors} errors, ${result.warnings} warnings)`)
  return `${score} ${status} ${issues}`
}

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
// Commands will be implemented inline for now

const program = new Command()

program
  .name('ts-quality-guard')
  .description('TypeScript Quality Assurance System - From prevention to validation')
  .version('1.0.0')

// Quality check command
program
  .command('check')
  .description('Run comprehensive quality checks on TypeScript files')
  .option('-f, --files <files>', 'specific files to check (comma-separated)', '')
  .option('--staged', 'check only staged files in git', false)
  .option('-t, --threshold <number>', 'quality threshold (0-100)', '85')
  .option('-c, --config <path>', 'path to config file', '.ts-quality-guard.json')
  .option('--ci', 'CI mode - stricter checks, fail on warnings', false)
  .option('--format <format>', 'output format (console, json, markdown, junit)', 'console')
  .option('--rules <rules>', 'specific rules to check (comma-separated)', '')
  .option('--fix', 'automatically fix fixable issues', false)
  .action(async (options) => {
    try {
      const { QualityChecker } = await import('../core/QualityChecker')
      const { ConfigManager } = await import('../core/ConfigManager')

      const {
        files,
        staged,
        threshold = '85',
        config: configPath,
        ci = false,
        format = 'console',
        rules
      } = options

      // Load configuration
      const config = await ConfigManager.loadConfig(configPath)
      const thresholdNum = parseInt(threshold.toString())

      // Determine files to check
      let filesToCheck: string[] = []
      if (files) {
        filesToCheck = files.split(',').map((f: string) => f.trim())
      } else if (staged) {
        // TODO: Implement git staged files detection
        console.log(chalk.yellow('⚠️  Staged files checking not yet implemented'))
        filesToCheck = await QualityChecker['getDefaultFiles']()
      } else {
        filesToCheck = await QualityChecker['getDefaultFiles']()
      }

      if (filesToCheck.length === 0) {
        console.log(chalk.yellow('⚠️  No TypeScript files found to check'))
        return
      }

      console.log(chalk.blue(`🔍 Checking ${filesToCheck.length} files...`))

      // Determine which rules to run
      let rulesToRun: string[]
      if (rules) {
        rulesToRun = rules.split(',')
      } else {
        rulesToRun = ['typescript', 'eslint', 'custom']
      }

      // Run quality checks
      const results = await QualityChecker.runChecks(filesToCheck, {
        configPath,
        threshold: thresholdNum,
        ci,
        rules: rulesToRun
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
  })

// Initialize project
program
  .command('init')
  .description('Initialize TypeScript Quality Guard for the project')
  .option('-f, --force', 'overwrite existing configuration', false)
  .option('-p, --project-type <type>', 'project type (vue-frontend, react-app, node-api)', '')
  .action(async (options) => {
    try {
      const { ConfigManager } = await import('../core/ConfigManager')

      const { force = false, projectType } = options

      console.log(chalk.blue('🚀 Initializing TypeScript Quality Guard...'))

      // Check if config already exists
      const configPath = '.ts-quality-guard.json'
      const configExists = await fs.pathExists(configPath)

      if (configExists && !force) {
        console.log(chalk.yellow('⚠️  Configuration file already exists.'))
        console.log(chalk.gray('   Use --force to overwrite existing configuration.'))
        console.log(chalk.gray(`   File: ${configPath}`))
        return
      }

      if (configExists && force) {
        console.log(chalk.yellow('⚠️  Overwriting existing configuration...'))
      }

      // Create configuration
      console.log(chalk.gray('📋 Detecting project type and dependencies...'))
      const config = await ConfigManager.createDefaultConfig(projectType)

      // Validate configuration
      console.log(chalk.gray('🔍 Validating configuration...'))
      const validation = ConfigManager.validateConfig(config)

      if (!validation.valid) {
        console.log(chalk.red('❌ Configuration validation failed:'))
        validation.errors.forEach((error: string) => {
          console.log(chalk.red(`   - ${error}`))
        })
        process.exit(1)
      }

      // Save configuration
      console.log(chalk.gray('💾 Saving configuration...'))
      await ConfigManager.saveConfig(config)

      // Display success message
      console.log('')
      console.log(chalk.green('✅ TypeScript Quality Guard initialized successfully!'))
      console.log('')
      console.log(chalk.blue('📁 Configuration saved to: .ts-quality-guard.json'))
      console.log('')
      console.log(chalk.yellow('🎯 Next steps:'))
      console.log(chalk.gray('   1. Review and customize the configuration'))
      console.log(chalk.gray('   2. Run: ts-quality-guard check'))
      console.log(chalk.gray('   3. Install hooks: ts-quality-guard install-hooks'))
      console.log('')
      console.log(chalk.blue('📊 Project detected:'))
      console.log(chalk.gray(`   Type: ${config.project.type}`))
      console.log(chalk.gray(`   Framework: ${config.project.framework}`))
      console.log(chalk.gray(`   TypeScript: ${config.project.typescript}`))

      if (config.project.styling) {
        console.log(chalk.gray(`   Styling: ${config.project.styling}`))
      }
      if (config.project.state) {
        console.log(chalk.gray(`   State: ${config.project.state}`))
      }
      if (config.project.api) {
        console.log(chalk.gray(`   API: ${config.project.api}`))
      }

    } catch (error: any) {
      console.error(chalk.red('❌ Initialization failed:'), error.message)
      process.exit(1)
    }
  })

// Generate coding standards
program
  .command('generate-standards')
  .alias('standards')
  .description('Generate coding standards and best practices for the project')
  .option('-p, --project-type <type>', 'project type', '')
  .option('-o, --output <file>', 'output file path', 'typescript-standards.md')
  .option('-c, --config <path>', 'config file path', '.ts-quality-guard.json')
  .action(async (options) => {
    try {
      const { ConfigManager } = await import('../core/ConfigManager')
      const { StandardsGenerator } = await import('../core/StandardsGenerator')

      const { projectType, output = 'typescript-standards.md', config: configPath } = options

      console.log(chalk.blue('📝 Generating coding standards...'))

      // Load configuration
      const config = await ConfigManager.loadConfig(configPath)

      // Determine project type
      let projectConfig = config.project
      if (projectType) {
        projectConfig = ConfigManager['detectProjectConfig'](projectType)
      }

      console.log(chalk.gray(`   Project: ${projectConfig.type} (${projectConfig.framework})`))
      console.log(chalk.gray(`   TypeScript: ${projectConfig.typescript}`))

      // Generate standards
      const standards = StandardsGenerator.generateStandards(projectConfig)

      // Save to file
      await fs.writeFile(output, standards, 'utf-8')

      console.log('')
      console.log(chalk.green('✅ Coding standards generated successfully!'))
      console.log(chalk.blue(`📁 Saved to: ${output}`))
      console.log('')
      console.log(chalk.yellow('📋 Standards Summary:'))
      console.log(chalk.gray(`   • Strict mode: ${config.standards.strict ? 'Enabled' : 'Disabled'}`))
      console.log(chalk.gray(`   • No implicit any: ${config.standards.noImplicitAny ? 'Enabled' : 'Disabled'}`))
      console.log(chalk.gray(`   • Max file lines: ${config.standards.maxFileLines}`))
      console.log(chalk.gray(`   • Naming convention: ${config.standards.namingConvention}`))
      console.log('')
      console.log(chalk.blue('💡 Usage Tips:'))
      console.log(chalk.gray('   • Share this file with your team'))
      console.log(chalk.gray('   • Use as AI coding prompt reference'))
      console.log(chalk.gray('   • Integrate into code review checklists'))

    } catch (error: any) {
      console.error(chalk.red('❌ Standards generation failed:'), error.message)
      process.exit(1)
    }
  })

// Real-time monitoring
program
  .command('watch')
  .description('Start real-time quality monitoring')
  .option('-d, --dir <directory>', 'directory to watch', 'src')
  .option('-p, --port <port>', 'IDE plugin port', '3001')
  .option('--ide <ide>', 'IDE to integrate with (vscode, webstorm)', 'vscode')
  .option('-c, --config <path>', 'config file path', '.ts-quality-guard.json')
  .action(async (options) => {
    console.log(chalk.blue('👁️  Starting real-time monitoring...'))
    console.log(chalk.yellow('⚠️  Watch command not yet implemented'))
    console.log(chalk.gray('   This is a placeholder implementation'))
  })

// Install git hooks
program
  .command('install-hooks')
  .description('Install git hooks for quality gates')
  .option('--only <hook>', 'install only specific hook (pre-commit, pre-push, commit-msg)', '')
  .option('-c, --config <path>', 'config file path', '.ts-quality-guard.json')
  .action(async (options) => {
    console.log(chalk.blue('🔧 Installing git hooks...'))
    console.log(chalk.yellow('⚠️  Install-hooks command not yet implemented'))
    console.log(chalk.gray('   This is a placeholder implementation'))
  })

// Validate configuration
program
  .command('validate-config')
  .description('Validate configuration file')
  .option('-c, --config <path>', 'config file path', '.ts-quality-guard.json')
  .option('-v, --verbose', 'verbose output', false)
  .action(async (options) => {
    try {
      const { ConfigManager } = await import('../core/ConfigManager')

      const { config: configPath, verbose = false } = options

      console.log(chalk.blue('🔍 Validating configuration...'))

      // Load configuration
      const config = await ConfigManager.loadConfig(configPath)

      if (verbose) {
        console.log(chalk.gray('📋 Loaded configuration:'))
        console.log(JSON.stringify(config, null, 2))
        console.log('')
      }

      // Validate configuration
      const validation = ConfigManager.validateConfig(config)

      if (validation.valid) {
        console.log(chalk.green('✅ Configuration is valid!'))
        console.log('')
        console.log(chalk.blue('📊 Configuration Summary:'))
        console.log(chalk.gray(`   Project: ${config.project.name} (${config.project.type})`))
        console.log(chalk.gray(`   Framework: ${config.project.framework}`))
        console.log(chalk.gray(`   TypeScript: ${config.project.typescript}`))
        console.log(chalk.gray(`   Strict mode: ${config.standards.strict ? 'Enabled' : 'Disabled'}`))
        console.log(chalk.gray(`   Quality threshold: ${config.gates.preCommit.threshold}`))
      } else {
        console.log(chalk.red('❌ Configuration validation failed!'))
        console.log('')
        console.log(chalk.red('🚨 Issues found:'))
        validation.errors.forEach((error: string) => {
          console.log(chalk.red(`   • ${error}`))
        })
        console.log('')
        console.log(chalk.yellow('💡 Fix suggestions:'))
        console.log(chalk.gray('   • Run: ts-quality-guard init --force'))
        console.log(chalk.gray('   • Check .ts-quality-guard.json syntax'))
        console.log(chalk.gray('   • Refer to documentation for valid options'))

        process.exit(1)
      }

    } catch (error: any) {
      console.error(chalk.red('❌ Configuration validation failed:'), error.message)
      console.log('')
      console.log(chalk.yellow('💡 Common solutions:'))
      console.log(chalk.gray('   • Ensure .ts-quality-guard.json exists'))
      console.log(chalk.gray('   • Check JSON syntax is valid'))
      console.log(chalk.gray('   • Run: ts-quality-guard init'))

      process.exit(1)
    }
  })

// Error handling
program.on('command:*', (unknownCommand) => {
  console.error(chalk.red(`❌ Unknown command: ${unknownCommand[0]}`))
  console.log('')
  console.log(chalk.blue('Available commands:'))
  program.commands.forEach(cmd => {
    if (cmd.name() !== '*') {
      console.log(`  ${chalk.green(cmd.name())} - ${cmd.description()}`)
    }
  })
  process.exit(1)
})

// Global error handler
process.on('uncaughtException', (error) => {
  console.error(chalk.red('❌ Uncaught Exception:'), error.message)
  process.exit(1)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error(chalk.red('❌ Unhandled Rejection at:'), promise, 'reason:', reason)
  process.exit(1)
})

// Parse arguments
program.parse(process.argv)

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp()
}
