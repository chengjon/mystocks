#!/usr/bin/env node

const fs = require("fs").promises;
const path = require("path");

const FRONTEND_ROOT = path.resolve(__dirname, "..");
const PROJECT_ROOT = path.resolve(FRONTEND_ROOT, "..", "..");
const DEFAULT_REPORT_DIR = path.join(
  PROJECT_ROOT,
  "reports",
  "analysis",
  "typescript-extension-validation",
);
const DEFAULT_DASHBOARD_DIR = path.join(DEFAULT_REPORT_DIR, "dashboard");

function parseArgs(argv) {
  const options = {
    reportDir: DEFAULT_REPORT_DIR,
    dashboardDir: DEFAULT_DASHBOARD_DIR,
    reportFile: null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];

    if (value === "--report-dir") {
      options.reportDir = path.resolve(argv[index + 1]);
      options.dashboardDir = path.join(options.reportDir, "dashboard");
      index += 1;
    } else if (value === "--dashboard-dir") {
      options.dashboardDir = path.resolve(argv[index + 1]);
      index += 1;
    } else if (value === "--report-file") {
      options.reportFile = path.resolve(argv[index + 1]);
      index += 1;
    }
  }

  return options;
}

function timestampToken(date = new Date()) {
  return date.toISOString().replace(/[-:]/gu, "").replace(/\.\d{3}Z$/u, "Z");
}

async function ensureDirectory(dirPath) {
  await fs.mkdir(dirPath, { recursive: true });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function statusLabel(value) {
  return value ? "PASS" : "OPEN";
}

function statusClass(value) {
  return value ? "ok" : "open";
}

function renderCheckRow(label, value) {
  return `
    <tr>
      <th>${escapeHtml(label)}</th>
      <td><span class="badge ${statusClass(value)}">${statusLabel(value)}</span></td>
    </tr>
  `;
}

function renderUnusedList(unusedNames) {
  if (!unusedNames.length) {
    return "<p>No unused extension types detected.</p>";
  }

  return `
    <ul>
      ${unusedNames.map((name) => `<li>${escapeHtml(name)}</li>`).join("\n")}
    </ul>
  `;
}

function formatPercent(value) {
  return Number.isFinite(value) ? `${Number(value).toFixed(2)}%` : "unknown";
}

function renderHtml(report) {
  const usage = report.usage?.extensions ?? {};
  const unusedNames = report.audit?.unused?.names ?? [];
  const coverage = report.coverage ?? {};

  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Type Extension Health Dashboard</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f5f7fb;
        --surface: #ffffff;
        --text: #14213d;
        --muted: #52607a;
        --border: #d7deea;
        --ok: #0a7f3f;
        --open: #a63d40;
        --accent: #195190;
      }
      body {
        margin: 0;
        padding: 32px;
        font-family: "Segoe UI", "PingFang SC", sans-serif;
        background: linear-gradient(180deg, #eef3fb 0%, var(--bg) 100%);
        color: var(--text);
      }
      main {
        max-width: 1080px;
        margin: 0 auto;
      }
      h1, h2 {
        margin: 0 0 12px;
      }
      p {
        color: var(--muted);
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin: 24px 0;
      }
      .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 16px 40px rgba(20, 33, 61, 0.06);
      }
      .card strong {
        display: block;
        margin-top: 8px;
        font-size: 28px;
      }
      .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.04em;
      }
      .badge.ok {
        background: rgba(10, 127, 63, 0.12);
        color: var(--ok);
      }
      .badge.open {
        background: rgba(166, 61, 64, 0.12);
        color: var(--open);
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        padding: 12px 14px;
        border-bottom: 1px solid var(--border);
        text-align: left;
      }
      th {
        width: 40%;
      }
      code {
        font-family: "JetBrains Mono", "SFMono-Regular", monospace;
        color: var(--accent);
      }
      ul {
        margin: 0;
        padding-left: 20px;
        column-count: 2;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Type Extension Health Dashboard</h1>
      <p>Generated at <code>${escapeHtml(report.generated_at ?? "unknown")}</code>.</p>

      <section class="grid">
        <article class="card">
          <span class="badge ${statusClass(report.overall?.ok)}">${statusLabel(report.overall?.ok)}</span>
          <strong>${escapeHtml(report.overall?.ok ? "Healthy" : "Attention Needed")}</strong>
          <p>Overall repo-truth validation status.</p>
        </article>
        <article class="card">
          <span class="badge ${statusClass(report.typecheck?.ok)}">${statusLabel(report.typecheck?.ok)}</span>
          <strong>${escapeHtml(report.typecheck?.type_error_count ?? 0)}</strong>
          <p>TypeScript compile errors in current validation run.</p>
        </article>
        <article class="card">
          <span class="badge ${statusClass((report.audit?.unused?.count ?? 0) === 0)}">${escapeHtml(
            report.audit?.unused?.count === 0 ? "CLEAR" : "OPEN",
          )}</span>
          <strong>${escapeHtml(report.audit?.unused?.count ?? 0)}</strong>
          <p>Unused extension type definitions still reported by audit.</p>
        </article>
        <article class="card">
          <span class="badge ok">INFO</span>
          <strong>${escapeHtml(usage.exported_types ?? "unknown")}</strong>
          <p>Current exported extension type count across tracked files.</p>
        </article>
        <article class="card">
          <span class="badge ${statusClass(coverage.ok)}">${statusLabel(coverage.ok)}</span>
          <strong>${escapeHtml(formatPercent(coverage.percent))}</strong>
          <p>Type coverage across extension public exports. Target: ${escapeHtml(
            coverage.target_percent ?? 95,
          )}%.</p>
        </article>
      </section>

      <section class="card">
        <h2>Validation Checks</h2>
        <table>
          <tbody>
            ${renderCheckRow("Validation script", report.validation?.ok)}
            ${renderCheckRow("Conflict check", report.conflicts?.ok)}
            ${renderCheckRow("Naming audit", report.audit?.naming?.ok)}
            ${renderCheckRow("JSDoc audit", report.audit?.jsdoc?.ok)}
            ${renderCheckRow("Type coverage", coverage.ok)}
            ${renderCheckRow("TypeScript type-check", report.typecheck?.ok)}
          </tbody>
        </table>
      </section>

      <section class="card" style="margin-top: 24px;">
        <h2>Surface Summary</h2>
        <table>
          <tbody>
            <tr>
              <th>Extension files</th>
              <td>${escapeHtml(usage.files ?? "unknown")}</td>
            </tr>
            <tr>
              <th>Exported extension types</th>
              <td>${escapeHtml(usage.exported_types ?? "unknown")}</td>
            </tr>
            <tr>
              <th>Unused definitions</th>
              <td>${escapeHtml(report.audit?.unused?.count ?? 0)}</td>
            </tr>
            <tr>
              <th>Covered / total exports</th>
              <td>${escapeHtml(coverage.covered_exported_types ?? "unknown")} / ${escapeHtml(
                coverage.total_exported_types ?? "unknown",
              )}</td>
            </tr>
            <tr>
              <th>Type coverage</th>
              <td>${escapeHtml(formatPercent(coverage.percent))}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="card" style="margin-top: 24px;">
        <h2>Unused Extension Types</h2>
        ${renderUnusedList(unusedNames)}
      </section>
    </main>
  </body>
</html>
`;
}

async function readJson(filePath) {
  const content = await fs.readFile(filePath, "utf8");
  return JSON.parse(content);
}

async function writeText(filePath, content) {
  await fs.writeFile(filePath, content, "utf8");
}

async function generateTypeHealthDashboard({
  reportDir = DEFAULT_REPORT_DIR,
  dashboardDir = DEFAULT_DASHBOARD_DIR,
  reportFile = null,
} = {}) {
  const resolvedReportFile = reportFile || path.join(reportDir, "latest.json");
  const report = await readJson(resolvedReportFile);

  await ensureDirectory(dashboardDir);

  const timestamp = timestampToken(new Date(report.generated_at || new Date().toISOString()));
  const timestampedHtml = path.join(dashboardDir, `${timestamp}-type-extension-health-dashboard.html`);
  const latestHtml = path.join(dashboardDir, "latest.html");

  const html = renderHtml(report);
  await writeText(timestampedHtml, html);
  await writeText(latestHtml, html);

  const payload = {
    generated_at: new Date().toISOString(),
    report_source: resolvedReportFile,
    overall: report.overall,
    dashboard_paths: {
      timestamped_html: timestampedHtml,
      latest_html: latestHtml,
    },
  };

  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  return payload;
}

if (require.main === module) {
  const options = parseArgs(process.argv.slice(2));
  generateTypeHealthDashboard(options).catch((error) => {
    console.error("❌ Type health dashboard generation failed:", error.message);
    process.exit(1);
  });
}

module.exports = {
  DEFAULT_DASHBOARD_DIR,
  DEFAULT_REPORT_DIR,
  generateTypeHealthDashboard,
  parseArgs,
  renderHtml,
};
