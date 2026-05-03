#!/usr/bin/env node

const fs = require("fs").promises;
const path = require("path");

const {
  EXTENSIONS_ROOT,
  FRONTEND_ROOT,
  readText,
} = require("./type-tooling-common.js");

const EXPORT_DECLARATION_RE = /^\s*export\s+(?:interface|type|enum|class)\s+([A-Za-z_][A-Za-z0-9_]*)/gm;
const PASCAL_CASE_RE = /^[A-Z][A-Za-z0-9]*$/;
const ALLOWED_LEGACY_EXPORT_NAMES = new Set(["list", "date_type"]);

async function collectTypeScriptFiles(rootPath) {
  const files = [];
  const queue = [rootPath];

  while (queue.length) {
    const currentPath = queue.pop();
    const entries = await fs.readdir(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        queue.push(entryPath);
      } else if (entry.isFile() && entry.name.endsWith(".ts")) {
        files.push(entryPath);
      }
    }
  }

  return files.sort();
}

function indexLineStarts(content) {
  const starts = [0];
  for (let index = 0; index < content.length; index += 1) {
    if (content[index] === "\n") {
      starts.push(index + 1);
    }
  }
  return starts;
}

function lineNumberFromIndex(lineStarts, targetIndex) {
  let line = 0;
  while (line + 1 < lineStarts.length && lineStarts[line + 1] <= targetIndex) {
    line += 1;
  }
  return line + 1;
}

function hasLeadingJsdoc(lines, declarationLineIndex) {
  let cursor = declarationLineIndex - 1;
  while (cursor >= 0 && lines[cursor].trim() === "") {
    cursor -= 1;
  }

  if (cursor < 0 || !lines[cursor].trim().endsWith("*/")) {
    return false;
  }

  while (cursor >= 0) {
    const trimmed = lines[cursor].trim();
    if (trimmed.startsWith("/**")) {
      return true;
    }
    if (trimmed.startsWith("/*") && !trimmed.startsWith("/**")) {
      return false;
    }
    cursor -= 1;
  }

  return false;
}

function collectDeclarations(filePath, content) {
  const declarations = [];
  const lines = content.split(/\r?\n/);
  const lineStarts = indexLineStarts(content);

  for (const match of content.matchAll(EXPORT_DECLARATION_RE)) {
    const name = match[1];
    const declarationIndex = match.index ?? 0;
    const line = lineNumberFromIndex(lineStarts, declarationIndex);
    declarations.push({
      name,
      filePath,
      line,
      hasJsdoc: hasLeadingJsdoc(lines, line - 1),
    });
  }

  return declarations;
}

function isNamingConventionCompliant(name) {
  return PASCAL_CASE_RE.test(name) || ALLOWED_LEGACY_EXPORT_NAMES.has(name);
}

function buildReferenceRegex(name) {
  return new RegExp(`\\b${name}\\b`, "g");
}

async function collectFrontendSourceFiles() {
  const sourceRoot = path.join(FRONTEND_ROOT, "src");
  const files = [];
  const queue = [sourceRoot];

  while (queue.length) {
    const currentPath = queue.pop();
    const entries = await fs.readdir(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        queue.push(entryPath);
      } else if (
        entry.isFile() &&
        (entry.name.endsWith(".ts") || entry.name.endsWith(".vue"))
      ) {
        files.push(entryPath);
      }
    }
  }

  return files.sort();
}

async function collectUnusedExports(declarations) {
  const sourceFiles = await collectFrontendSourceFiles();
  const fileContentCache = new Map();
  const unused = [];

  for (const declaration of declarations) {
    const referenceRegex = buildReferenceRegex(declaration.name);
    let referenceCount = 0;

    for (const sourceFile of sourceFiles) {
      if (path.resolve(sourceFile) === path.resolve(declaration.filePath)) {
        continue;
      }

      let content = fileContentCache.get(sourceFile);
      if (!content) {
        content = await readText(sourceFile);
        fileContentCache.set(sourceFile, content);
      }

      const matches = content.match(referenceRegex);
      if (matches) {
        referenceCount += matches.length;
      }
    }

    if (referenceCount === 0) {
      unused.push({
        name: declaration.name,
        file: path.relative(FRONTEND_ROOT, declaration.filePath),
        line: declaration.line,
      });
    }
  }

  return unused.sort((left, right) =>
    `${left.file}:${left.line}:${left.name}`.localeCompare(
      `${right.file}:${right.line}:${right.name}`,
    ),
  );
}

async function auditTypeExtensionQuality() {
  const extensionFiles = await collectTypeScriptFiles(EXTENSIONS_ROOT);
  const declarations = [];

  for (const filePath of extensionFiles) {
    const content = await readText(filePath);
    declarations.push(...collectDeclarations(filePath, content));
  }

  const namingViolations = declarations
    .filter((declaration) => !isNamingConventionCompliant(declaration.name))
    .map((declaration) => ({
      name: declaration.name,
      file: path.relative(FRONTEND_ROOT, declaration.filePath),
      line: declaration.line,
    }))
    .sort((left, right) =>
      `${left.file}:${left.line}:${left.name}`.localeCompare(
        `${right.file}:${right.line}:${right.name}`,
      ),
    );

  const missingJsdoc = declarations
    .filter((declaration) => !declaration.hasJsdoc)
    .map((declaration) => ({
      name: declaration.name,
      file: path.relative(FRONTEND_ROOT, declaration.filePath),
      line: declaration.line,
    }))
    .sort((left, right) =>
      `${left.file}:${left.line}:${left.name}`.localeCompare(
        `${right.file}:${right.line}:${right.name}`,
      ),
    );

  const unused = await collectUnusedExports(declarations);

  const payload = {
    generated_at: new Date().toISOString(),
    extensions: {
      files: extensionFiles.length,
      exported_types: declarations.length,
    },
    naming: {
      ok: namingViolations.length === 0,
      violations: namingViolations,
      allowed_legacy_aliases: [...ALLOWED_LEGACY_EXPORT_NAMES].sort(),
    },
    jsdoc: {
      ok: missingJsdoc.length === 0,
      missing: missingJsdoc,
    },
    unused: {
      count: unused.length,
      names: unused.map((entry) => entry.name),
      entries: unused,
    },
  };

  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

if (require.main === module) {
  auditTypeExtensionQuality().catch((error) => {
    console.error("❌ Type extension quality audit failed:", error.message);
    process.exit(1);
  });
}

module.exports = {
  auditTypeExtensionQuality,
};
