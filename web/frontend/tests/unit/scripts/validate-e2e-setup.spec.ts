import { createRequire } from "node:module";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const scriptPath = resolve(process.cwd(), "validate-e2e-setup.js");

const loadValidator = () => require(scriptPath);

describe("validate-e2e-setup", () => {
  it("treats validate, stable, axe, lighthouse, and comprehensive package scripts as required E2E entrypoints", () => {
    const { PACKAGE_SCRIPT_REQUIREMENTS } = loadValidator();

    expect(PACKAGE_SCRIPT_REQUIREMENTS).toEqual({
      "test:e2e:validate": "validate-e2e-setup.js",
      "test:e2e:stable": "playwright test --config playwright.config.js --project=chromium",
      "test:e2e:axe": "accessibility-smoke.spec.ts",
      "test:e2e:lighthouse": "lhci autorun",
      "test:e2e:comprehensive": "run-comprehensive-e2e.js",
    });
  });

  it("documents the shared PM2, axe, and lighthouse workflows in required README sections", () => {
    const { README_REQUIRED_SECTIONS } = loadValidator();

    expect(README_REQUIRED_SECTIONS).toContain("npm run test:e2e:validate");
    expect(README_REQUIRED_SECTIONS).toContain("npm run test:e2e:stable");
    expect(README_REQUIRED_SECTIONS).toContain("npm run test:e2e:axe");
    expect(README_REQUIRED_SECTIONS).toContain("npm run test:e2e:lighthouse");
  });

  it("prints shared PM2 safe next steps instead of pointing operators at the comprehensive runner", () => {
    const { buildSuccessNextSteps } = loadValidator();
    const steps = buildSuccessNextSteps();

    expect(steps).toContain("1. Start MyStocks services via PM2 (or reuse existing shared PM2 services)");
    expect(steps).toContain("2. Run: npm run test:e2e:validate");
    expect(steps).toContain("3. Run shared-PM2 stable suite with:");
    expect(steps.join("\n")).toContain("npm run test:e2e:stable");
    expect(steps.join("\n")).not.toContain("npm run test:e2e:comprehensive");
  });
});
