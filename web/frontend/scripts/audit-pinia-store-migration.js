#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const TARGET_DIRECTORIES = ["src/views", "src/components", "src/composables"];
const FILE_EXTENSIONS = new Set([".ts", ".vue"]);

const MIGRATION_RULES = [
  {
    id: "auth-login",
    replacement: "useAuthStore",
    status: "store-ready",
    reason: "auth store 已标准化并支持 custom request executor",
    match: (source) => /authApi\.login\s*\(|apiClient\.(post|get)\s*\(\s*['"`]\/v1\/auth\/login/u.test(source),
  },
  {
    id: "strategy-management",
    replacement: "useStrategyStore",
    status: "store-ready",
    reason: "strategy management 已通过 standardized fetch path 接入",
    match: (source) => /tradingApiManager\.getStrategyManagement\s*\(|getStrategyManagement\s*\(/u.test(source),
  },
  {
    id: "trading-signals",
    replacement: "useTradingSignalsStore",
    status: "store-ready",
    reason: "trading signals 已有 realtime standardized store",
    match: (source) => /strategyApi\.getSignals\s*\(|apiClient\.get\s*\(\s*['"`]\/api\/trading\/signals/u.test(source),
  },
  {
    id: "risk-alerts",
    replacement: "useRiskAlertsStore",
    status: "store-ready",
    reason: "risk alerts 已有 realtime standardized store",
    match: (source) => /apiClient\.get\s*\(\s*['"`]\/api\/risk\/alerts/u.test(source),
  },
  {
    id: "technical-indicators",
    replacement: "useTechnicalIndicatorsStore",
    status: "store-ready",
    reason: "technical indicators 已有 standardized store",
    match: (source) => /apiClient\.(post|get)\s*\(\s*['"`]\/api\/analysis\/indicators/u.test(source),
  },
  {
    id: "monitoring-watchlists",
    replacement: "useWatchlistsStore",
    status: "store-ready",
    reason: "monitoring watchlists 已有 standardized store",
    match: (source) => /apiClient\.get\s*\(\s*['"`]\/v1\/monitoring\/watchlists(?:['"`)]|\/)/u.test(source),
  },
  {
    id: "monitoring-watchlist-stocks",
    replacement: "useWatchlistStocksStore",
    status: "store-ready",
    reason: "watchlist stocks 已有 parameterized standardized store",
    match: (source) => /apiClient\.get\s*\(\s*['"`]\/v1\/monitoring\/watchlists\/\$\{[^}]+\}\/stocks/u.test(source),
  },
  {
    id: "user-watchlists-legacy",
    replacement: "useWatchlistsStore",
    status: "gap",
    reason: "发现旧 watchlist 路径，需迁移到 monitoring standardized stores",
    match: (source) => /\/api\/watchlist\b|\/api\/portfolio\/v2\/watchlist\b|\/api\/user\/watchlists\b/u.test(source),
  },
];

function normalizePath(filePath) {
  return filePath.split(path.sep).join("/");
}

function shouldScan(filePath) {
  const extension = path.extname(filePath);
  if (!FILE_EXTENSIONS.has(extension)) {
    return false;
  }

  const normalized = normalizePath(filePath);
  return !normalized.includes("/__tests__/") && !normalized.includes("/tests/") && !normalized.includes("/__node_tests__/");
}

function collectSourceFiles(rootDir, relativeDir) {
  const absoluteDir = path.join(rootDir, relativeDir);
  const files = [];

  if (!fs.existsSync(absoluteDir)) {
    return files;
  }

  for (const entry of fs.readdirSync(absoluteDir, { withFileTypes: true })) {
    const absolutePath = path.join(absoluteDir, entry.name);

    if (entry.isDirectory()) {
      files.push(...collectSourceFiles(rootDir, normalizePath(path.join(relativeDir, entry.name))));
      continue;
    }

    if (entry.isFile() && shouldScan(absolutePath)) {
      files.push(absolutePath);
    }
  }

  return files;
}

function scanFile(relativePath, source) {
  return MIGRATION_RULES.flatMap((rule) => {
    if (!rule.match(source)) {
      return [];
    }

    return [{
      file: relativePath,
      capability: rule.id,
      replacement: rule.replacement,
      status: rule.status,
      reason: rule.reason,
    }];
  });
}

function auditPiniaStoreMigration({ rootDir = process.cwd() } = {}) {
  const normalizedRoot = path.resolve(rootDir);
  const files = TARGET_DIRECTORIES.flatMap((dir) => collectSourceFiles(normalizedRoot, dir));
  const candidates = files.flatMap((absolutePath) => {
    const relativePath = normalizePath(path.relative(normalizedRoot, absolutePath));
    const source = fs.readFileSync(absolutePath, "utf8");
    return scanFile(relativePath, source);
  });

  const summary = {
    scannedFiles: files.length,
    candidateFiles: new Set(candidates.map((candidate) => candidate.file)).size,
    storeReady: candidates.filter((candidate) => candidate.status === "store-ready").length,
    gaps: candidates.filter((candidate) => candidate.status === "gap").length,
  };

  return {
    summary,
    candidates: candidates.sort((left, right) => left.file.localeCompare(right.file) || left.capability.localeCompare(right.capability)),
  };
}

function printHumanReport(report) {
  console.log("[pinia-migration] scanned files:", report.summary.scannedFiles);
  console.log("[pinia-migration] candidate files:", report.summary.candidateFiles);
  console.log("[pinia-migration] store-ready:", report.summary.storeReady);
  console.log("[pinia-migration] gaps:", report.summary.gaps);

  for (const candidate of report.candidates) {
    console.log(
      `- [${candidate.status}] ${candidate.file} -> ${candidate.replacement} (${candidate.capability}) :: ${candidate.reason}`,
    );
  }
}

if (require.main === module) {
  const report = auditPiniaStoreMigration();

  if (process.argv.includes("--json")) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    printHumanReport(report);
  }
}

module.exports = {
  MIGRATION_RULES,
  TARGET_DIRECTORIES,
  auditPiniaStoreMigration,
  collectSourceFiles,
  normalizePath,
  scanFile,
  shouldScan,
};
