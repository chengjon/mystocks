import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { createRequire } from "node:module";
import { afterEach, describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const scriptPath = resolve(process.cwd(), "scripts/audit-pinia-store-migration.js");
const tempDirs: string[] = [];

const loadAudit = () => require(scriptPath);

const createTempDir = () => {
  const dir = mkdtempSync(join(tmpdir(), "pinia-migration-audit-"));
  tempDirs.push(dir);
  return dir;
};

const writeFixture = (rootDir: string, relativePath: string, content: string) => {
  const filePath = join(rootDir, relativePath);
  mkdirSync(dirname(filePath), { recursive: true });
  writeFileSync(filePath, content, "utf8");
};

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("audit-pinia-store-migration", () => {
  it("flags store-ready candidates for standardized capabilities", () => {
    const { auditPiniaStoreMigration } = loadAudit();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "src/views/trade/Signals.vue",
      `import { strategyApi } from '@/api'
async function loadSignals() {
  return strategyApi.getSignals({ limit: 20 })
}`,
    );

    const report = auditPiniaStoreMigration({ rootDir });

    expect(report.summary.storeReady).toBe(1);
    expect(report.summary.gaps).toBe(0);
    expect(report.candidates).toEqual([
      expect.objectContaining({
        file: "src/views/trade/Signals.vue",
        capability: "trading-signals",
        replacement: "useTradingSignalsStore",
        status: "store-ready",
      }),
    ]);
  });

  it("flags legacy watchlist paths as migration gaps", () => {
    const { auditPiniaStoreMigration } = loadAudit();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "src/components/watchlist/Panel.ts",
      `import { apiClient } from '@/api/apiClient'
async function loadWatchlist() {
  return apiClient.get('/v1/monitoring/watchlists')
}`,
    );

    const report = auditPiniaStoreMigration({ rootDir });

    expect(report.summary.storeReady).toBe(0);
    expect(report.summary.gaps).toBe(1);
    expect(report.candidates).toEqual([
      expect.objectContaining({
        file: "src/components/watchlist/Panel.ts",
        capability: "user-watchlists-legacy",
        replacement: "useWatchlistsStore",
        status: "gap",
      }),
    ]);
  });

  it("ignores unrelated API usage outside standardized capabilities", () => {
    const { auditPiniaStoreMigration } = loadAudit();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "src/views/system/Health.vue",
      `import { apiClient } from '@/api/apiClient'
async function loadHealth() {
  return apiClient.get('/health')
}`,
    );

    const report = auditPiniaStoreMigration({ rootDir });

    expect(report.candidates).toEqual([]);
    expect(report.summary.storeReady).toBe(0);
    expect(report.summary.gaps).toBe(0);
  });
});
