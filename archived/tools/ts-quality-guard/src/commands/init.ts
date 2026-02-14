/**
 * Command: Initialize project configuration
 */

import * as fs from 'fs-extra'
import * as path from 'path'
import chalk from 'chalk'
import { ConfigManager } from '../core/ConfigManager'
import { InitCommandOptions } from '../types'

export async function initCommand(options: InitCommandOptions) {
  const { force = false, projectType } = options

  console.log(chalk.blue('🚀 Initializing TypeScript Quality Guard...'))

  try {
    // Check if config already exists
    const configPath = path.join(process.cwd(), '.ts-quality-guard.json')
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
      validation.errors.forEach(error => {
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
    console.log(chalk.gray('   2. Run: npx ts-quality-guard check'))
    console.log(chalk.gray('   3. Install hooks: npx ts-quality-guard install-hooks'))
    console.log('')
    console.log(chalk.blue('📚 Useful commands:'))
    console.log(chalk.gray('   • ts-quality-guard check              # Run quality checks'))
    console.log(chalk.gray('   • ts-quality-guard generate-standards # Generate coding standards'))
    console.log(chalk.gray('   • ts-quality-guard watch              # Start real-time monitoring'))

    // Display project detection results
    console.log('')
    console.log(chalk.blue('🔍 Project detected:'))
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
}
