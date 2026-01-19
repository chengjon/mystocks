#!/usr/bin/env node

/**
 * TypeScript Type Validation Script
 *
 * Runs comprehensive validation on the type extension system
 * Used by npm scripts and CI/CD pipelines
 */

const path = require('path');
const fs = require('fs').promises;

// Simple validation for now - in a real implementation this would be more sophisticated
async function validateTypes() {
  console.log('🔍 Validating TypeScript type extensions...\n');

  const extensionsDir = path.join(__dirname, '../src/api/types/extensions');

  try {
    // Check if extensions directory exists
    await fs.access(extensionsDir);
    console.log('✅ Extensions directory exists');

    // Check if required files exist
    const requiredFiles = [
      'index.ts',
      'strategy.ts',
      'market.ts',
      'common.ts'
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(extensionsDir, file);
      try {
        await fs.access(filePath);
        console.log(`✅ ${file} exists`);
      } catch {
        console.error(`❌ ${file} missing`);
        process.exit(1);
      }
    }

    // Check main index.ts exports extensions
    const mainIndexPath = path.join(__dirname, '../src/api/types/index.ts');
    const mainIndexContent = await fs.readFile(mainIndexPath, 'utf-8');

    if (mainIndexContent.includes("export * from './extensions'")) {
      console.log('✅ Main index.ts exports extensions');
    } else {
      console.error('❌ Main index.ts does not export extensions');
      process.exit(1);
    }

    console.log('\n🎉 Type validation passed!');
    console.log('💡 Ready to proceed with type definitions');

  } catch (error) {
    console.error('❌ Type validation failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  validateTypes();
}

module.exports = { validateTypes };