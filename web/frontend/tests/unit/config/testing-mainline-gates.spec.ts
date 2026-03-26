import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const packageJson = JSON.parse(
  fs.readFileSync(path.join(frontendRoot, "package.json"), "utf8"),
) as {
  scripts?: Record<string, string>;
  devDependencies?: Record<string, string>;
};

describe("Testing mainline gates", () => {
  it("keeps Playwright as the only standard browser automation dependency", () => {
    expect(packageJson.devDependencies?.puppeteer).toBeUndefined();
    expect(packageJson.scripts?.["test:e2e"]).toContain("playwright test");
  });

  it("defines canonical auth and business-smoke Playwright entrypoints", () => {
    expect(packageJson.scripts?.["test:e2e:auth"]).toContain("tests/e2e/auth-login.spec.ts");
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain("tests/e2e/auth-login.spec.ts");
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain(
      "tests/e2e/critical/menu-navigation-fixed.spec.ts",
    );
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain("tests/e2e/market-data.spec.ts");
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain(
      "tests/e2e/strategy-management-chain.spec.ts",
    );
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain(
      "tests/e2e/strategy-backtest.spec.ts",
    );
    expect(packageJson.scripts?.["test:e2e:business-smoke"]).toContain("tests/e2e/kline-chart.spec.ts");
  });

  it("keeps Lighthouse on the cjs mainline config only", () => {
    expect(fs.existsSync(path.join(frontendRoot, ".lighthouserc.json"))).toBe(false);
    expect(fs.existsSync(path.join(frontendRoot, "lighthouserc.cjs"))).toBe(true);
    expect(packageJson.scripts?.["test:e2e:lighthouse"]).toContain("lighthouserc.cjs");
  });

  it("defines canonical visual regression entrypoints", () => {
    expect(packageJson.scripts?.["test:visual"]).toContain("tests/visual/config/visual.config.ts");
    expect(packageJson.scripts?.["test:visual:update"]).toContain("--update-snapshots");
    expect(packageJson.scripts?.["test:visual:dashboard"]).toContain("tests/visual/pages/dashboard.spec.ts");
    expect(packageJson.scripts?.["test:visual:charts"]).toContain("tests/visual/components/charts/backtest.spec.ts");
    expect(packageJson.scripts?.["test:visual:dashboard:update"]).toContain("--update-snapshots");
    expect(packageJson.scripts?.["test:visual:dashboard:update"]).toContain("tests/visual/pages/dashboard.spec.ts");
    expect(packageJson.scripts?.["test:visual:charts:update"]).toContain("--update-snapshots");
  });

  it("removes Cypress from the active frontend test toolchain", () => {
    expect(fs.existsSync(path.join(frontendRoot, "cypress.config.ts"))).toBe(false);
    expect(fs.existsSync(path.join(frontendRoot, "cypress"))).toBe(false);
  });

  it("removes top-level Puppeteer page runners from the active toolchain", () => {
    expect(fs.existsSync(path.join(frontendRoot, "test_all_pages.js"))).toBe(false);
    expect(fs.existsSync(path.join(frontendRoot, "scripts", "diagnose-pages.js"))).toBe(false);
  });
});
