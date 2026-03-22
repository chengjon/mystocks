import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { createRequire } from "node:module";
import { afterEach, describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const scriptPath = resolve(process.cwd(), "scripts/check-e2e-user-locators.js");

const tempDirs: string[] = [];

const loadChecker = () => require(scriptPath);

const createTempDir = () => {
  const dir = mkdtempSync(join(tmpdir(), "e2e-user-locator-check-"));
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

describe("check-e2e-user-locators", () => {
  it("passes for user-facing locators", () => {
    const { checkE2EUserLocators } = loadChecker();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "tests/e2e/user-facing.spec.ts",
      `import { test, expect } from "@playwright/test";
test("uses user facing locators", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await page.getByRole("button", { name: "刷新行情" }).click();
});`,
    );

    const result = checkE2EUserLocators({ rootDir });

    expect(result.violations).toHaveLength(0);
  });

  it("flags raw locator usage outside the legacy allowlist", () => {
    const { checkE2EUserLocators } = loadChecker();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "tests/e2e/new-smoke.spec.ts",
      `import { test } from "@playwright/test";
test("uses css locator", async ({ page }) => {
  await page.locator(".market-card").click();
});`,
    );

    writeFixture(
      rootDir,
      "tests/e2e/legacy.spec.ts",
      `import { test } from "@playwright/test";
test("legacy locator", async ({ page }) => {
  await page.locator(".legacy-card").click();
});`,
    );

    const result = checkE2EUserLocators({
      rootDir,
      legacyAllowlist: new Set(["tests/e2e/legacy.spec.ts"]),
    });

    expect(result.violations).toEqual([
      {
        file: "tests/e2e/new-smoke.spec.ts",
        line: 3,
        pattern: "locator",
      },
    ]);
  });

  it("allows explicit inline exceptions for unavoidable selector edge cases", () => {
    const { checkE2EUserLocators } = loadChecker();
    const rootDir = createTempDir();

    writeFixture(
      rootDir,
      "tests/e2e/chart.spec.ts",
      `import { test } from "@playwright/test";
test("uses exception", async ({ page }) => {
  await page.locator("canvas").click(); // e2e-selector-exception
});`,
    );

    const result = checkE2EUserLocators({ rootDir });

    expect(result.violations).toHaveLength(0);
  });
});
