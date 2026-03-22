#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const DEFAULT_LEGACY_ALLOWLIST = new Set([
  "tests/e2e/api-integration.spec.ts",
  "tests/e2e/artdeco-config-integration.spec.ts",
  "tests/e2e/comprehensive-all-pages.spec.ts",
  "tests/e2e/market-data.spec.ts",
  "tests/e2e/strategy-backtest.spec.ts",
  "tests/e2e/strategy-crud.spec.ts",
  "tests/e2e/strategy-management-boundary.spec.ts",
  "tests/e2e/strategy-management-chain.spec.ts",
  "tests/e2e/strategy-monitor.spec.ts",
  "tests/e2e/test-component-rendering.spec.ts",
]);

const FORBIDDEN_PATTERNS = [
  { name: "locator", regex: /\.\s*locator\s*\(/u },
  { name: "querySelector", regex: /querySelector(All)?\s*\(/u },
  { name: "$$", regex: /\.\s*\$\$\s*\(/u },
  { name: "$", regex: /\.\s*\$\s*\(/u },
];

function normalizePath(filePath) {
  return filePath.split(path.sep).join("/");
}

function collectSpecFiles(specDir) {
  const files = [];

  if (!fs.existsSync(specDir)) {
    return files;
  }

  for (const entry of fs.readdirSync(specDir, { withFileTypes: true })) {
    const absolutePath = path.join(specDir, entry.name);

    if (entry.isDirectory()) {
      files.push(...collectSpecFiles(absolutePath));
      continue;
    }

    if (!entry.isFile() || !entry.name.endsWith(".spec.ts")) {
      continue;
    }

    if (absolutePath.includes(`${path.sep}helpers${path.sep}`)) {
      continue;
    }

    files.push(absolutePath);
  }

  return files;
}

function scanSourceForForbiddenLocators(source) {
  const violations = [];
  const lines = source.split(/\r?\n/u);

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed || trimmed.startsWith("//") || line.includes("e2e-selector-exception")) {
      return;
    }

    for (const pattern of FORBIDDEN_PATTERNS) {
      if (pattern.regex.test(line)) {
        violations.push({
          line: index + 1,
          pattern: pattern.name,
        });
        break;
      }
    }
  });

  return violations;
}

function checkE2EUserLocators({ rootDir = process.cwd(), legacyAllowlist = DEFAULT_LEGACY_ALLOWLIST } = {}) {
  const normalizedRoot = path.resolve(rootDir);
  const specDir = path.join(normalizedRoot, "tests", "e2e");
  const scannedFiles = [];
  const violations = [];

  for (const absolutePath of collectSpecFiles(specDir)) {
    const relativePath = normalizePath(path.relative(normalizedRoot, absolutePath));
    scannedFiles.push(relativePath);

    if (legacyAllowlist.has(relativePath)) {
      continue;
    }

    const fileViolations = scanSourceForForbiddenLocators(fs.readFileSync(absolutePath, "utf8"));
    fileViolations.forEach((violation) => {
      violations.push({
        file: relativePath,
        line: violation.line,
        pattern: violation.pattern,
      });
    });
  }

  return { scannedFiles, violations };
}

if (require.main === module) {
  const result = checkE2EUserLocators();

  if (result.violations.length > 0) {
    console.error("[e2e-selectors] User-facing locator policy failed.");
    for (const violation of result.violations) {
      console.error(`- ${violation.file}:${violation.line} uses forbidden ${violation.pattern} selector`);
    }
    console.error(
      "[e2e-selectors] Use getByRole/getByLabel/getByPlaceholder/getByText/getByTestId. Legacy exceptions must stay on the explicit allowlist.",
    );
    process.exit(1);
  }

  console.log(
    `[e2e-selectors] User-facing locator policy passed for ${result.scannedFiles.length} canonical E2E specs.`,
  );
}

module.exports = {
  DEFAULT_LEGACY_ALLOWLIST,
  FORBIDDEN_PATTERNS,
  checkE2EUserLocators,
  collectSpecFiles,
  normalizePath,
  scanSourceForForbiddenLocators,
};
