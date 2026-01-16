/**
 * Command: Install git hooks
 */

import * as fs from 'fs-extra'
import * as path from 'path'
import chalk from 'chalk'
import { InstallHooksCommandOptions } from '../types'

export async function installHooksCommand(options: InstallHooksCommandOptions) {
  const { only, config: configPath } = options

  try {
    console.log(chalk.blue('🔧 Installing Git hooks...'))

    const hooksDir = path.join(process.cwd(), '.git', 'hooks')
    const hooksToInstall = only ? [only] : ['pre-commit', 'pre-push', 'commit-msg']

    // Ensure hooks directory exists
    await fs.ensureDir(hooksDir)

    // Install each hook
    for (const hookName of hooksToInstall) {
      await installHook(hookName, hooksDir)
    }

    // Make hooks executable
    for (const hookName of hooksToInstall) {
      const hookPath = path.join(hooksDir, hookName)
      try {
        await fs.chmod(hookPath, '755')
      } catch (error) {
        console.warn(chalk.yellow(`⚠️  Could not make ${hookName} executable`))
      }
    }

    console.log('')
    console.log(chalk.green('✅ Git hooks installed successfully!'))
    console.log('')
    console.log(chalk.blue('🎣 Installed hooks:'))
    hooksToInstall.forEach(hook => {
      console.log(chalk.gray(`   • ${hook}`))
    })
    console.log('')
    console.log(chalk.yellow('💡 Hook behaviors:'))
    console.log(chalk.gray('   • pre-commit: Checks staged files before commit'))
    console.log(chalk.gray('   • pre-push: Checks commits before push'))
    console.log(chalk.gray('   • commit-msg: Validates commit message format'))
    console.log('')
    console.log(chalk.blue('🚫 To skip hooks (not recommended):'))
    console.log(chalk.gray('   git commit --no-verify'))
    console.log(chalk.gray('   git push --no-verify'))

  } catch (error: any) {
    console.error(chalk.red('❌ Hook installation failed:'), error.message)
    console.log('')
    console.log(chalk.yellow('💡 Troubleshooting:'))
    console.log(chalk.gray('   • Ensure .git directory exists'))
    console.log(chalk.gray('   • Check write permissions on .git/hooks/'))
    console.log(chalk.gray('   • Run: git init (if .git is missing)'))

    process.exit(1)
  }
}

/**
 * Install a specific git hook
 */
async function installHook(hookName: string, hooksDir: string): Promise<void> {
  const hookPath = path.join(hooksDir, hookName)
  const hookContent = generateHookContent(hookName)

  // Check if hook already exists
  const exists = await fs.pathExists(hookPath)
  if (exists) {
    const existingContent = await fs.readFile(hookPath, 'utf-8')
    if (existingContent.includes('ts-quality-guard') && !existingContent.includes('# TS-QUALITY-GUARD-HOOK')) {
      console.log(chalk.yellow(`⚠️  ${hookName} hook already exists and may conflict`))
      console.log(chalk.gray(`   Consider backing up: cp ${hookPath} ${hookPath}.backup`))
    }
  }

  // Write hook content
  await fs.writeFile(hookPath, hookContent, 'utf-8')
  console.log(chalk.gray(`   ✓ ${hookName} hook installed`))
}

/**
 * Generate hook content based on hook type
 */
function generateHookContent(hookName: string): string {
  const shebang = '#!/bin/bash'
  const marker = '# TS-QUALITY-GUARD-HOOK'

  switch (hookName) {
    case 'pre-commit':
      return `${shebang}
${marker}

echo "🔍 Running TypeScript Quality Check (pre-commit)..."

# Check if ts-quality-guard is available
if ! command -v ts-quality-guard &> /dev/null; then
    echo "⚠️  ts-quality-guard not found. Install with: npm install -g ts-quality-guard"
    echo "💡 Skipping quality check..."
    exit 0
fi

# Run quality check on staged files
if ! npx ts-quality-guard check --staged --gate commit; then
    echo "❌ Quality check failed. Fix issues or use --no-verify to skip."
    exit 1
fi

echo "✅ Quality check passed!"
exit 0
`

    case 'pre-push':
      return `${shebang}
${marker}

echo "🚀 Running TypeScript Quality Check (pre-push)..."

# Check if ts-quality-guard is available
if ! command -v ts-quality-guard &> /dev/null; then
    echo "⚠️  ts-quality-guard not found. Install with: npm install -g ts-quality-guard"
    echo "💡 Skipping quality check..."
    exit 0
fi

# Get commits being pushed
while read local_ref local_sha remote_ref remote_sha
do
    if [ "$local_sha" = $z40 ]; then
        # Deleting branch, skip check
        exit 0
    fi

    # Check commit range
    if ! npx ts-quality-guard check --files "$(git diff --name-only $remote_sha..$local_sha | grep -E '\\.(ts|tsx|vue)$' | tr '\\n' ',')" --gate push; then
        echo "❌ Quality check failed. Fix issues or use --no-verify to skip."
        exit 1
    fi
done

echo "✅ Quality check passed!"
exit 0
`

    case 'commit-msg':
      return `${shebang}
${marker}

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat $COMMIT_MSG_FILE)

# Check commit message format
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,}"; then
    echo "❌ Invalid commit message format"
    echo ""
    echo "📝 Expected format:"
    echo "   type(scope): description"
    echo ""
    echo "📝 Examples:"
    echo "   feat(auth): add JWT token validation"
    echo "   fix(ui): resolve button alignment issue"
    echo "   docs(readme): update installation guide"
    echo ""
    echo "🎯 Valid types: feat, fix, docs, style, refactor, test, chore"
    exit 1
fi

echo "✅ Commit message format is valid"
exit 0
`

    default:
      throw new Error(`Unsupported hook type: ${hookName}`)
  }
}
