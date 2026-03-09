/**
 * Command: Generate coding standards
 */

import chalk from 'chalk'
import * as fs from 'fs-extra'
import * as path from 'path'
import { ConfigManager } from '../core/ConfigManager'
import { StandardsGenerator } from '../core/StandardsGenerator'
import { StandardsCommandOptions } from '../types'

export async function standardsCommand(options: StandardsCommandOptions) {
  const { projectType, output = 'typescript-standards.md', config: configPath } = options

  try {
    // Load configuration
    const config = await ConfigManager.loadConfig(configPath)

    // Determine project type
    let projectConfig = config.project
    if (projectType) {
      projectConfig = ConfigManager['detectProjectConfig'](projectType)
    }

    console.log(chalk.blue('📝 Generating coding standards...'))
    console.log(chalk.gray(`   Project: ${projectConfig.type} (${projectConfig.framework})`))
    console.log(chalk.gray(`   TypeScript: ${projectConfig.typescript}`))

    // Generate standards
    const standards = StandardsGenerator.generateStandards(projectConfig)

    // Save to file
    const outputPath = path.resolve(output)
    await fs.writeFile(outputPath, standards, 'utf-8')

    console.log('')
    console.log(chalk.green('✅ Coding standards generated successfully!'))
    console.log(chalk.blue(`📁 Saved to: ${outputPath}`))
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
}
