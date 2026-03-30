import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const repoRoot = path.resolve(frontendRoot, "..", "..");

const readWorkflow = (relativePath: string) =>
  fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
const readJson = <T>(relativePath: string) =>
  JSON.parse(fs.readFileSync(path.join(repoRoot, relativePath), "utf8")) as T;

const packageJson = JSON.parse(
  fs.readFileSync(path.join(frontendRoot, "package.json"), "utf8"),
) as { scripts: Record<string, string> };

describe("CI workflow gates", () => {
  it("defines a dedicated stable unit suite command", () => {
    expect(packageJson.scripts["test:unit:stable"]).toBeDefined();
  });

  it("defines an axe-backed E2E accessibility smoke command", () => {
    expect(packageJson.scripts["test:e2e:axe"]).toBeDefined();
  });

  it("defines a Lighthouse CI smoke command", () => {
    expect(packageJson.scripts["test:e2e:lighthouse"]).toBeDefined();
  });

  it("defines ArtDeco documentation governance commands for full and changed-only checks", () => {
    expect(packageJson.scripts["lint:artdeco:guidance"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:guidance:changed"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:changed"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/layouts");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/layout");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/menu");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/common");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/views/styles");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/shared/ui");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-file src/views/SkeletonUsage.vue");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-file src/views/Stocks.vue");
  });

  it("defines visual regression package scripts for workflow reuse", () => {
    expect(packageJson.scripts["test:visual"]).toBeDefined();
    expect(packageJson.scripts["test:visual:update"]).toBeDefined();
    expect(packageJson.scripts["test:visual:dashboard"]).toBeDefined();
    expect(packageJson.scripts["test:visual:dashboard:update"]).toBeDefined();
    expect(packageJson.scripts["test:visual:charts"]).toBeDefined();
    expect(packageJson.scripts["test:visual:charts:update"]).toBeDefined();
  });

  it("defines a blocking Chromium business-smoke command", () => {
    expect(packageJson.scripts["test:e2e:business-smoke"]).toBeDefined();
    expect(packageJson.scripts["test:e2e:auth"]).toBeDefined();
  });

  it("runs the full frontend unit suite as a blocking frontend-testing gate", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const frontendTestSection = workflowText.split("frontend-test:")[1]?.split("frontend-security:")[0];
    const stableUnitStepMatch = frontendTestSection.match(
      /- name: Run stable unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );
    const unitTestStepMatch = frontendTestSection.match(
      /- name: Run full unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(stableUnitStepMatch?.[1]?.trim()).toBe("npm run test:unit:stable");
    expect(unitTestStepMatch?.[1]?.trim()).toBe("npm run test");
    expect(frontendTestSection).not.toMatch(
      /- name: Run full unit tests[\s\S]*?continue-on-error:\s*true/u,
    );
  });

  it("runs the Chromium business-smoke suite in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const e2eStepMatch = workflowText.match(/- name: Run business smoke e2e tests[\s\S]*?npm run test:e2e:stable/u);

    expect(e2eStepMatch?.[0]).toContain("npm run test:e2e:stable");
  });

  it("runs the axe accessibility smoke in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const axeStepMatch = workflowText.match(
      /- name: Run axe accessibility smoke[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(axeStepMatch?.[1]?.trim()).toBe("npm run test:e2e:axe");
  });

  it("runs Lighthouse CI smoke in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const lighthouseStepMatch = workflowText.match(
      /- name: Run Lighthouse CI smoke[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(lighthouseStepMatch?.[1]?.trim()).toBe("npm run test:e2e:lighthouse");
  });

  it("runs the changed-only ArtDeco guidance gate in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const guidanceStepMatch = workflowText.match(
      /- name: Run ArtDeco guidance changed-file gate[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(guidanceStepMatch?.[1]?.trim()).toBe("npm run lint:artdeco:guidance:changed");
  });

  it("runs the changed-only ArtDeco source gate in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const sourceStepMatch = workflowText.match(
      /- name: Run ArtDeco token changed-file gate[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(sourceStepMatch?.[1]?.trim()).toBe("npm run lint:artdeco:changed");
  });

  it("treats ArtDeco components as ArtDeco scope inputs during workflow detection", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("web/frontend/src/components/artdeco/*");
    expect(workflowText).toContain("web/frontend/src/components/artdeco/**");
    expect(workflowText).toContain("web/frontend/src/layouts/*");
    expect(workflowText).toContain("web/frontend/src/layouts/**");
    expect(workflowText).toContain("web/frontend/src/components/layout/*");
    expect(workflowText).toContain("web/frontend/src/components/layout/**");
    expect(workflowText).toContain("web/frontend/src/components/menu/*");
    expect(workflowText).toContain("web/frontend/src/components/menu/**");
    expect(workflowText).toContain("web/frontend/src/components/common/*");
    expect(workflowText).toContain("web/frontend/src/components/common/**");
    expect(workflowText).toContain("web/frontend/src/views/styles/*");
    expect(workflowText).toContain("web/frontend/src/views/styles/**");
    expect(workflowText).toContain("web/frontend/src/components/shared/ui/*");
    expect(workflowText).toContain("web/frontend/src/components/shared/ui/**");
    expect(workflowText).toContain("web/frontend/src/views/SkeletonUsage.vue");
    expect(workflowText).toContain("web/frontend/src/views/Stocks.vue");
  });

  it("keeps the dedicated cross-browser workflow aligned with the Playwright mainline", () => {
    const workflowText = readWorkflow(".github/workflows/e2e-testing.yml");

    expect(workflowText).toContain("npm run test:e2e:lighthouse");
    expect(workflowText).toContain("tests/e2e/auth-login.spec.ts");
    expect(workflowText).toContain("tests/e2e/critical/menu-navigation-fixed.spec.ts");
    expect(workflowText).toContain("tests/e2e/kline-chart.spec.ts");
    expect(workflowText).not.toContain(".lighthouserc.json");
  });

  it("aligns the standalone Playwright workflow with the standard stable E2E entrypoint", () => {
    const workflowText = readWorkflow(".github/workflows/playwright.yml");

    expect(workflowText).toContain("working-directory: web/frontend");
    expect(workflowText).toContain("npm run test:e2e:stable");
    expect(workflowText).not.toContain("playwright.config.ts");
  });

  it("enforces a zero type error ceiling in the frontend and TypeScript workflows", () => {
    const frontendWorkflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const typeWorkflowText = readWorkflow(".github/workflows/typescript-type-check.yml");

    expect(frontendWorkflowText).toContain("TYPE_ERROR_CEILING: '0'");
    expect(typeWorkflowText).toContain("TYPE_ERROR_CEILING: '0'");
    expect(typeWorkflowText).toContain("node scripts/check-type-error-ceiling.js");
    expect(typeWorkflowText).not.toContain("Filter type errors");
    expect(typeWorkflowText).not.toContain("vue-tsc-filtered.txt");
  });

  it("treats tsc and eslint diagnostics as zero-error gates in the TypeScript workflow", () => {
    const typeWorkflowText = readWorkflow(".github/workflows/typescript-type-check.yml");

    expect(typeWorkflowText).toContain('if [ -f type-check-artifacts/tsc-results/tsc-output.txt ]');
    expect(typeWorkflowText).toContain('TSC_ERROR_COUNT=$(grep -c "error TS" type-check-artifacts/tsc-results/tsc-output.txt');
    expect(typeWorkflowText).toContain('ARTIFACT_DIR="${{ github.workspace }}/type-check-artifacts/tsc-results"');
    expect(typeWorkflowText).toContain('path: type-check-artifacts');
    expect(typeWorkflowText).toContain('if [ "$ESLINT_COUNT" -gt 0 ]');
    expect(typeWorkflowText).not.toContain('if [ "$ESLINT_COUNT" -gt 100 ]');
  });

  it("keeps the long-term frontend type debt baseline aligned with the zero-error gate", () => {
    const baseline = readJson<{ frontend_type_errors: number }>(
      "reports/analysis/tech-debt-baseline.json",
    );

    expect(baseline.frontend_type_errors).toBe(0);
  });

  it("watches the real frontend visual test tree in the visual workflow", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("web/frontend/tests/visual/**");
    expect(workflowText).not.toContain("'tests/visual/**'");
  });

  it("uses package scripts instead of inline playwright commands in the visual workflow", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("npm run test:visual:dashboard --");
    expect(workflowText).toContain("npm run test:visual:charts --");
    expect(workflowText).toContain("npm run test:visual:dashboard:update");
    expect(workflowText).toContain("npm run test:visual:charts:update");
    expect(workflowText).toContain("VISUAL_HTML_REPORT_DIR=playwright-report/dashboard");
    expect(workflowText).toContain("VISUAL_HTML_REPORT_DIR=playwright-report/charts");
    expect(workflowText).toContain("visual-dashboard-results-${{ matrix.browser }}");
    expect(workflowText).toContain("visual-chart-results-${{ matrix.browser }}");
    expect(workflowText).not.toContain("npx playwright test \\");
  });

  it("writes a grouped visual summary for dashboard and chart suites", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("visual-test-summary.json");
    expect(workflowText).toContain("dashboard_tests");
    expect(workflowText).toContain("dashboard_passed");
    expect(workflowText).toContain("chart_tests");
    expect(workflowText).toContain("chart_passed");
  });
});
