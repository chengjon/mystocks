#!/usr/bin/env node

const fs = require("fs").promises;
const path = require("path");

const FRONTEND_ROOT = path.resolve(__dirname, "..");
const TYPES_ROOT = path.join(FRONTEND_ROOT, "src", "api", "types");
const EXTENSIONS_ROOT = path.join(TYPES_ROOT, "extensions");
const EXTENSIONS_INDEX_PATH = path.join(EXTENSIONS_ROOT, "index.ts");
const MAIN_INDEX_PATH = path.join(TYPES_ROOT, "index.ts");

const DECLARATION_EXPORT_RE = /^\s*export\s+(?:interface|type|enum|class)\s+([A-Za-z_][A-Za-z0-9_]*)/gm;
const NAMED_REEXPORT_RE = /^\s*export\s+(?:type\s+)?\{([^}]+)\}\s+from\s+['"](.+?)['"]/gm;
const STAR_REEXPORT_RE = /^\s*export\s+\*\s+from\s+['"](.+?)['"]/gm;

async function readText(filePath) {
  return fs.readFile(filePath, "utf-8");
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function fileExists(filePath) {
  try {
    const stat = await fs.stat(filePath);
    return stat.isFile();
  } catch {
    return false;
  }
}

function normalizeExportName(rawName) {
  const trimmed = rawName.trim();
  if (!trimmed) {
    return null;
  }

  const aliasParts = trimmed.split(/\s+as\s+/i);
  return (aliasParts[1] || aliasParts[0]).trim();
}

function addExport(exportMap, exportName, sourcePath) {
  if (!exportName) {
    return;
  }

  const sources = exportMap.get(exportName) || new Set();
  sources.add(sourcePath);
  exportMap.set(exportName, sources);
}

function mergeExportMaps(targetMap, sourceMap) {
  for (const [exportName, sources] of sourceMap.entries()) {
    const currentSources = targetMap.get(exportName) || new Set();
    for (const sourcePath of sources) {
      currentSources.add(sourcePath);
    }
    targetMap.set(exportName, currentSources);
  }
}

async function resolveModulePath(baseFilePath, specifier) {
  const rawTarget = path.resolve(path.dirname(baseFilePath), specifier);
  const candidates = [rawTarget, `${rawTarget}.ts`, `${rawTarget}.js`, path.join(rawTarget, "index.ts"), path.join(rawTarget, "index.js")];

  for (const candidate of candidates) {
    if (await fileExists(candidate)) {
      return candidate;
    }
  }

  throw new Error(`Unable to resolve module path "${specifier}" from ${baseFilePath}`);
}

async function collectModuleExports(filePath, cache = new Map()) {
  const normalizedPath = path.resolve(filePath);
  if (cache.has(normalizedPath)) {
    return cache.get(normalizedPath);
  }

  const exportMap = new Map();
  cache.set(normalizedPath, exportMap);

  const content = await readText(normalizedPath);

  for (const match of content.matchAll(DECLARATION_EXPORT_RE)) {
    addExport(exportMap, match[1], normalizedPath);
  }

  for (const match of content.matchAll(NAMED_REEXPORT_RE)) {
    const resolvedTarget = await resolveModulePath(normalizedPath, match[2]);
    for (const rawName of match[1].split(",")) {
      addExport(exportMap, normalizeExportName(rawName), resolvedTarget);
    }
  }

  for (const match of content.matchAll(STAR_REEXPORT_RE)) {
    const resolvedTarget = await resolveModulePath(normalizedPath, match[1]);
    const targetExports = await collectModuleExports(resolvedTarget, cache);
    mergeExportMaps(exportMap, targetExports);
  }

  return exportMap;
}

function getDuplicateExports(exportMap) {
  return [...exportMap.entries()]
    .filter(([, sources]) => sources.size > 1)
    .map(([name, sources]) => ({
      name,
      sources: [...sources].sort(),
    }))
    .sort((left, right) => left.name.localeCompare(right.name));
}

async function getMainIndexExtensionExportMode() {
  const content = await readText(MAIN_INDEX_PATH);

  if (/export\s+\*\s+from\s+['"]\.\/extensions['"]/.test(content)) {
    return "star";
  }

  if (/export\s+\*\s+as\s+extensions\s+from\s+['"]\.\/extensions['"]/.test(content)) {
    return "namespace";
  }

  return "missing";
}

async function getRootPublicExportMap() {
  const mainIndexContent = await readText(MAIN_INDEX_PATH);
  const exportMap = new Map();

  for (const match of mainIndexContent.matchAll(STAR_REEXPORT_RE)) {
    if (match[1] === "./extensions") {
      continue;
    }

    const resolvedTarget = await resolveModulePath(MAIN_INDEX_PATH, match[1]);
    const targetExports = await collectModuleExports(resolvedTarget);
    mergeExportMaps(exportMap, targetExports);
  }

  return exportMap;
}

async function getExtensionPublicExportMap() {
  return collectModuleExports(EXTENSIONS_INDEX_PATH);
}

function findConflictingExports(leftMap, rightMap) {
  return [...leftMap.keys()]
    .filter((exportName) => rightMap.has(exportName))
    .sort()
    .map((name) => ({
      name,
      main_sources: [...leftMap.get(name)].sort(),
      extension_sources: [...rightMap.get(name)].sort(),
    }));
}

module.exports = {
  EXTENSIONS_INDEX_PATH,
  EXTENSIONS_ROOT,
  FRONTEND_ROOT,
  MAIN_INDEX_PATH,
  TYPES_ROOT,
  collectModuleExports,
  fileExists,
  pathExists,
  findConflictingExports,
  getDuplicateExports,
  getExtensionPublicExportMap,
  getMainIndexExtensionExportMode,
  getRootPublicExportMap,
  readText,
};
