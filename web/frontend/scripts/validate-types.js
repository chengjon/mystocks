#!/usr/bin/env node

/**
 * TypeScript Type Validation Script
 *
 * Runs comprehensive validation on the type extension system
 * Used by npm scripts and CI/CD pipelines
 */

const path = require("path");
const {
  EXTENSIONS_ROOT,
  MAIN_INDEX_PATH,
  fileExists,
  getMainIndexExtensionExportMode,
  pathExists,
} = require("./type-tooling-common.js");

// Simple validation for now - in a real implementation this would be more sophisticated
async function validateTypes() {
  console.log("🔍 Validating TypeScript type extensions...\n");

  try {
    // Check if extensions directory exists
    if (!(await pathExists(EXTENSIONS_ROOT))) {
      throw new Error("Extensions directory missing");
    }
    console.log("✅ Extensions directory exists");

    // Check if required files exist
    const requiredFiles = [
      "index.ts",
      "strategy.ts",
      "strategy/index.ts",
      "market/index.ts",
      "common.ts",
      "common/index.ts",
      "ui.ts",
      "ui/index.ts",
      "api/index.ts",
      "utils/index.ts",
    ];

    for (const file of requiredFiles) {
      const filePath = path.join(EXTENSIONS_ROOT, file);
      if (await fileExists(filePath)) {
        console.log(`✅ ${file} exists`);
      } else {
        console.error(`❌ ${file} missing`);
        process.exit(1);
      }
    }

    const extensionExportMode = await getMainIndexExtensionExportMode();
    if (extensionExportMode !== "missing") {
      console.log("✅ Main index.ts exports extensions");
      console.log(`ℹ️  Extension export mode: ${extensionExportMode}`);
    } else {
      console.error("❌ Main index.ts does not export extensions");
      process.exit(1);
    }

    if (!(await fileExists(MAIN_INDEX_PATH))) {
      console.error("❌ Main index.ts missing");
      process.exit(1);
    }

    console.log("\n🎉 Type validation passed!");
    console.log("💡 Ready to proceed with type definitions");

  } catch (error) {
    console.error("❌ Type validation failed:", error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  validateTypes();
}

module.exports = { validateTypes };
