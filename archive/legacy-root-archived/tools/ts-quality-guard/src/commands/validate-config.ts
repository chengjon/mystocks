/**
 * Command: Validate configuration
 */

import chalk from 'chalk'
import { ConfigManager } from '../core/ConfigManager'
import { ValidateConfigCommandOptions } from '../types'

export async function validateConfigCommand(options: ValidateConfigCommandOptions) {
  const { config: configPath, verbose = false } = options

  try {
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
      validation.errors.forEach(error => {
        console.log(chalk.red(`   • ${error}`))
      })
      console.log('')
      console.log(chalk.yellow('💡 Fix suggestions:'))
      console.log(chalk.gray('   • Run: npx ts-quality-guard init --force'))
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
    console.log(chalk.gray('   • Run: npx ts-quality-guard init'))

    process.exit(1)
  }
}
