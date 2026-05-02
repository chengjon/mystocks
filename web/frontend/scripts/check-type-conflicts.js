#!/usr/bin/env node

const {
  getDuplicateExports,
  getExtensionPublicExportMap,
  getMainIndexExtensionExportMode,
  getRootPublicExportMap,
  findConflictingExports,
} = require("./type-tooling-common.js");

async function checkTypeConflicts() {
  const extensionExportMode = await getMainIndexExtensionExportMode();
  if (extensionExportMode === "missing") {
    console.error("❌ Main type index does not export extensions");
    process.exit(1);
  }

  const rootExports = await getRootPublicExportMap();
  const extensionExports = await getExtensionPublicExportMap();
  const rootVsExtensionConflicts =
    extensionExportMode === "star" ? findConflictingExports(rootExports, extensionExports) : [];
  const duplicateExtensionExports = getDuplicateExports(extensionExports);

  if (rootVsExtensionConflicts.length || duplicateExtensionExports.length) {
    console.error("❌ Type conflicts detected");

    for (const conflict of rootVsExtensionConflicts) {
      console.error(
        `- ${conflict.name}: main=${conflict.main_sources.join(", ")} | extensions=${conflict.extension_sources.join(", ")}`
      );
    }

    for (const duplicate of duplicateExtensionExports) {
      console.error(`- duplicate extension export ${duplicate.name}: ${duplicate.sources.join(", ")}`);
    }

    process.exit(1);
  }

  console.log("✅ No type conflicts detected");
  console.log(`ℹ️  Root public exports: ${rootExports.size}`);
  console.log(`ℹ️  Extension public exports: ${extensionExports.size}`);
  console.log(`ℹ️  Main index extension export mode: ${extensionExportMode}`);
}

if (require.main === module) {
  checkTypeConflicts().catch((error) => {
    console.error("❌ Type conflict check failed:", error.message);
    process.exit(1);
  });
}

module.exports = { checkTypeConflicts };
