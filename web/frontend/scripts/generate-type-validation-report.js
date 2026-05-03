#!/usr/bin/env node

const fs = require("fs").promises;
const path = require("path");
const { spawnSync } = require("node:child_process");

const FRONTEND_ROOT = path.resolve(__dirname, "..");
const PROJECT_ROOT = path.resolve(FRONTEND_ROOT, "..", "..");
const DEFAULT_REPORT_DIR = path.join(
  PROJECT_ROOT,
  "reports",
  "analysis",
  "typescript-extension-validation",
);

function parseArgs(argv) {
  const options = {
    reportDir: DEFAULT_REPORT_DIR,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];

    if (value === "--report-dir") {
      options.reportDir = path.resolve(argv[index + 1]);
      index += 1;
    }
  }

  return options;
}

function runCommand(command, args, { cwd = FRONTEND_ROOT } = {}) {
  const result = spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    shell: process.platform === "win32",
  });

  return {
    status: typeof result.status === "number" ? result.status : 1,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    error: result.error || null,
  };
}

function countTypeScriptErrors(output) {
  return Array.from(output.matchAll(/\berror TS\d+:/gu)).length;
}

function parseExtensionExportMode(output) {
  const match = output.match(/Extension export mode:\s+([^\s]+)/u);
  return match ? match[1] : "unknown";
}

function parseConflictExportCounts(output) {
  const rootMatch = output.match(/Root public exports:\s+(\d+)/u);
  const extensionMatch = output.match(/Extension public exports:\s+(\d+)/u);
  const modeMatch = output.match(/Main index extension export mode:\s+([^\s]+)/u);

  return {
    root_public_exports: rootMatch ? Number.parseInt(rootMatch[1], 10) : null,
    extension_public_exports: extensionMatch ? Number.parseInt(extensionMatch[1], 10) : null,
    extension_export_mode: modeMatch ? modeMatch[1] : "unknown",
  };
}

function timestampToken(date = new Date()) {
  return date.toISOString().replace(/[-:]/gu, "").replace(/\.\d{3}Z$/u, "Z");
}

async function ensureDirectory(dirPath) {
  await fs.mkdir(dirPath, { recursive: true });
}

async function writeJson(filePath, payload) {
  await fs.writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function runValidationScript() {
  const result = runCommand("node", ["scripts/validate-types.js"]);
  const output = `${result.stdout}\n${result.stderr}`;

  return {
    ok: result.status === 0 && /Type validation passed!/u.test(output),
    status: result.status,
    extension_export_mode: parseExtensionExportMode(output),
    extensions_directory_exists: /Extensions directory exists/u.test(output),
    required_files: {
      index: /index\.ts exists/u.test(output),
      strategy: /strategy\.ts exists/u.test(output),
      market_index: /market\/index\.ts exists/u.test(output),
      common: /common\.ts exists/u.test(output),
      ui: /ui\.ts exists/u.test(output),
    },
  };
}

function runConflictScript() {
  const result = runCommand("node", ["scripts/check-type-conflicts.js"]);
  const parsed = parseConflictExportCounts(`${result.stdout}\n${result.stderr}`);

  return {
    ok: result.status === 0 && /No type conflicts detected/u.test(result.stdout),
    status: result.status,
    ...parsed,
  };
}

function runJsonScript(relativeScriptPath) {
  const result = runCommand("node", [relativeScriptPath]);
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || `${relativeScriptPath} failed`);
  }

  return JSON.parse(result.stdout);
}

function runTypeCheck() {
  const result = runCommand("npm", ["run", "type-check"]);
  const combinedOutput = `${result.stdout}\n${result.stderr}`;

  return {
    ok: result.status === 0,
    status: result.status,
    type_error_count: countTypeScriptErrors(combinedOutput),
  };
}

function buildCoverageSummary(audit, usage) {
  const totalExportedTypes =
    usage?.extensions?.exported_types ??
    audit?.extensions?.exported_types ??
    0;
  const uncoveredExportedTypes = audit?.unused?.count ?? 0;
  const coveredExportedTypes = Math.max(0, totalExportedTypes - uncoveredExportedTypes);
  const percent = totalExportedTypes > 0
    ? Number.parseFloat(((coveredExportedTypes / totalExportedTypes) * 100).toFixed(2))
    : 0;

  return {
    metric: "consumed_extension_exports",
    target_percent: 95,
    total_exported_types: totalExportedTypes,
    covered_exported_types: coveredExportedTypes,
    uncovered_exported_types: uncoveredExportedTypes,
    percent,
    ok: percent >= 95,
  };
}

async function generateTypeValidationReport({ reportDir = DEFAULT_REPORT_DIR } = {}) {
  const generatedAt = new Date().toISOString();
  const validation = runValidationScript();
  const conflicts = runConflictScript();
  const audit = runJsonScript("scripts/audit-type-extension-quality.js");
  const usage = runJsonScript("scripts/generate-type-usage.js");
  const typecheck = runTypeCheck();
  const coverage = buildCoverageSummary(audit, usage);

  const report = {
    summary_schema_version: 1,
    generated_at: generatedAt,
    frontend_root: path.relative(PROJECT_ROOT, FRONTEND_ROOT),
    validation,
    conflicts,
    audit,
    usage,
    coverage,
    typecheck,
    overall: {
      ok:
        validation.ok &&
        conflicts.ok &&
        audit.naming.ok &&
        audit.jsdoc.ok &&
        coverage.ok &&
        typecheck.ok,
      checks: {
        validation: validation.ok,
        conflicts: conflicts.ok,
        naming: audit.naming.ok,
        jsdoc: audit.jsdoc.ok,
        coverage: coverage.ok,
        typecheck: typecheck.ok,
      },
      observations: {
        unused_type_definition_count: audit.unused.count,
        type_coverage_percent: coverage.percent,
      },
    },
  };

  await ensureDirectory(reportDir);

  const timestampedJson = path.join(
    reportDir,
    `${timestampToken(new Date(generatedAt))}-type-extension-validation-report.json`,
  );
  const latestJson = path.join(reportDir, "latest.json");

  report.report_paths = {
    timestamped_json: timestampedJson,
    latest_json: latestJson,
  };

  await writeJson(timestampedJson, report);
  await writeJson(latestJson, report);

  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  return report;
}

if (require.main === module) {
  const options = parseArgs(process.argv.slice(2));
  generateTypeValidationReport(options).catch((error) => {
    console.error("❌ Type validation report generation failed:", error.message);
    process.exit(1);
  });
}

module.exports = {
  DEFAULT_REPORT_DIR,
  generateTypeValidationReport,
  parseArgs,
};
