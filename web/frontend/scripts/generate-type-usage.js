#!/usr/bin/env node

const {
  EXTENSIONS_ROOT,
  getExtensionPublicExportMap,
  getMainIndexExtensionExportMode,
  getRootPublicExportMap,
} = require("./type-tooling-common.js");
const fs = require("fs").promises;
const path = require("path");

async function countTypeScriptFiles(rootPath) {
  let total = 0;
  const queue = [rootPath];

  while (queue.length) {
    const currentPath = queue.pop();
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        queue.push(entryPath);
      } else if (entry.isFile() && entry.name.endsWith(".ts")) {
        total += 1;
      }
    }
  }

  return total;
}

async function generateTypeUsage() {
  const extensionExportMode = await getMainIndexExtensionExportMode();
  const rootExports = await getRootPublicExportMap();
  const extensionExports = await getExtensionPublicExportMap();
  const extensionFiles = await countTypeScriptFiles(EXTENSIONS_ROOT);

  const payload = {
    generated_at: new Date().toISOString(),
    extensions: {
      files: extensionFiles,
      exported_types: extensionExports.size,
    },
    main_index: {
      exports_extensions: extensionExportMode !== "missing",
      extension_export_mode: extensionExportMode,
      exported_types: rootExports.size,
    },
    combined_public_surface: {
      exported_types: rootExports.size + extensionExports.size,
    },
  };

  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

if (require.main === module) {
  generateTypeUsage().catch((error) => {
    console.error("❌ Type usage generation failed:", error.message);
    process.exit(1);
  });
}

module.exports = { generateTypeUsage };
