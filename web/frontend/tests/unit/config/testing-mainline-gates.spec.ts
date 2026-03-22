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

  it("keeps Lighthouse on the cjs mainline config only", () => {
    expect(fs.existsSync(path.join(frontendRoot, ".lighthouserc.json"))).toBe(false);
    expect(fs.existsSync(path.join(frontendRoot, "lighthouserc.cjs"))).toBe(true);
    expect(packageJson.scripts?.["test:e2e:lighthouse"]).toContain("lighthouserc.cjs");
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
